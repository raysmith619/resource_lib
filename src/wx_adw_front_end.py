#wx_adw_front_end.py        03Mar2023  crs, Adapted from adw_front_end.py
#
"""
AudioDrawWindow support using wxPython
Created in an attempt to pare down audio_draw_window.py size
"""
import wx
import sys
from math import sqrt
from datetime import datetime
import time 

from wx_stuff import *
from select_trace import SlTrace
from wx_audio_beep import AudioBeep

from braille_cell import BrailleCell
from grid_fill_gobble import GridFillGobble

from magnify_info import MagnifySelect
from wx_adw_menus import AdwMenus
from wx_adw_scanner import AdwScanner
from wx_key_cmd_proc import KeyCmdProc
from wx_canvas_panel_item import CanvasPanelItem

class AdwFrontEnd:

    """
    Front end functions
    """
    # Multi-key commands
    NAV_COLOR_CHANGE = "color_change_cmd"

    # Magnification window viewing
    MAG_PARENT = "mag_parent"
    MAG_CHILD = "mag_child"

    # letter keys for color change
    color_letters = {"r": "red", "o": "orange", "y": "yellow",
                     "g": "green", "b": "blue", "i": "indigo",
                     "v": "violet"}


    def __init__(self, adw, title=None, key_str=None, menu_str=None,
                 pos_check_interval= .1,
                 pos_rep_interval = .1,
                 pos_rep_queue_max = 1,
                 visible_figure = True,
                 enable_mouse = False,
                 silent=False,
                 pgmExit=None,
                 show_marked=False,
                 shift_to_edge=None,
                 color="blue",
                 ):
        """ front end support
        :adw: (AudioDrawWindow) parent window
        :title: title for reporting
        :pos_rep_interval: minimum time between reports
                default: .5 seconds
        :pos_rep_queue_max: maximum position report queue maximum
                default: 4
        :silent: make noise dissapear
                default: adw.silent - False
        :visible_figure: figure is visible
                default: True - visible
        :key_str: initial key command string default: none
        :menu_str: initial menu command string default: none
        """
        self.adw = adw
        self.key_cmd_proc = KeyCmdProc(adw, key_press=self.key_press)
        canv_pan = self.canv_pan = adw.canv_pan   # set fte link
        canv_pan.set_mouse_left_down_proc(self.on_button_1)
        canv_pan.set_mouse_motion_proc(self.motion)
        canv_pan.set_mouse_b1_motion_proc(self.on_button_1_motion)
        self.speaker_control = self.get_speaker_control()
        if title is None:
            title = "Audio Menu"
        self.title = title
        if shift_to_edge is None:
            shift_to_edge = adw.shift_to_edge
        self.shift_to_edge = shift_to_edge
        self.win_print_entry = adw.win_print_entry
        self._multi_key_progress = False    # No multi-key cmd in progress
        self.key_str = key_str
        self.menu_str = menu_str
        self.pos_rep_time = datetime.now()  # Time of last report
        self.pos_rep_interval = pos_rep_interval
        self.pos_x = None           # Latest position (win), if any 
        self.pos_y = None
        self.pos_cell_ixiy = None    # Tracking info, to minimize noise
        self.pos_dist_str = None    # Last position report string
        self.pos_rep_queue = []       # queue of report tuples
        # "dist", ix_dist, iy_dist
        # "fig", cell
        self.rept_at_loc = True         # Start with reporting at loc
        self.pos_rep_force_output = False   # True - force output
        self.pos_rep_queue_max = pos_rep_queue_max
        self.pos_rep_ix_prev = None    # previous report location 
        self.pos_rep_iy_prev = None
        self.pos_rep_str_prev = None    # previous position report
        self.pos_check_interval = pos_check_interval
        self.goto_travel_list_index = 0
        self._echo_input = True     # True -> speak input
        self._loc_list_original = None
        self._loc_list_first = None     # a,b horiz/vert move targets
        self._loc_list_second = None
        self.set_initial_location()
        self._silent = silent           # So prev=self._silent  doesn't fail
        self.set_silent(silent) # Start with speaking
        self.set_using_audio_beep(False)
        self._track_goto_cell = True    # True -> mark cells where we have gone
        self.clear_goto_cell_list()
        self._show_marked = show_marked
        self.set_enable_mouse(enable_mouse)
        self._pendown = False       # True - move marks
        self.set_color(color)
        self.setup_beep()
        # direction for digit pad
        y_up = -1
        y_down = 1
        self.digit_dir = {"7":(-1,y_up),   "8":(0,y_up),   "9":(1,y_up),
                          "4":(-1,0),      "5":(0,0),      "6":(1,0),
                          "1":(-1,y_down), "2":(0,y_down), "3":(1,y_down)}
        self.scanner = AdwScanner(self)
        self.menus = AdwMenus(self, frame=self.adw)

    def add_to_goto_cell_list(self, ixy):
        """ Add to goto history
        :ixy: ix,iy tuple
        """
        self.goto_cell_list.append(ixy)

    def clear_goto_cell_list(self):
        self.goto_cell_list = []

    def get_goto_cell_list(self):
        return self.goto_cell_list

    def set_initial_location(self):
        """ Set/Reset initial location of cursor
        """
        self.x,self.y = (0,0)

    def silence(self):
        """ Function to check for silent mode
        """
        return self.is_silent()

    def is_silent(self):
        return self._silent

    def set_silent(self, val=True):
        """ Set / Clear silent
        :val: value to set
        :returns: previous silent value
        """
        prev_val = self._silent
        self._silent = val
        return prev_val


        self.do_menu_str(menu_str)
        if key_str:
            self.adw.move_to_ixy(self.adw.grid_width/2, self.adw.grid_height//2)
        self.do_key_str(key_str)

    def do_complete(self, menu_str=None, key_str=None):
        """ Complete menu process
        """
        self.motion_level = 0   # Track possible recursive calls
        self.do_menu_str(menu_str)
        if key_str:
            self.adw.move_to_ixy(self.adw.grid_width/2, self.adw.grid_height//2)
        self.do_key_str(key_str)

    def move_to_ixy(self, ix=None, iy=None):
        """ Move to grid (cell) ix,iy
        :ix: ix index default: current ix
        :iy: iy index default: current iy
        """
        ix_cur,iy_cur = self.get_ixy_at()
        if ix is None:
            ix = ix_cur
        if iy is None:
            iy = iy_cur
        win_xc,win_yc = self.get_cell_center_win(ix,iy)
        self.move_to(win_xc,win_yc)

    def wait_on_output(self):
        """ Wait till queued output speech/tones completed
        """
        while True:
            if self.adw.speaker_control.is_busy():
                self.update()
                continue

            break
    """
    Setup menus
    """
    def pgm_exit(self, rc=None):
        SlTrace.lg("fte.pgm_exit")
        self.adw.exit()

    def File_Open_tbd(self):
        print("File_Open_menu to be determined")

    def File_Save_tbd(self):
        print("File_Save_menu to be determined")
    def is_drawing(self):
        return self._drawing

    def set_drawing(self, val=True):
        self._drawing = val
        return val

    def start_drawing(self):
        """ Start/enable drawing
        """
        self.set_drawing()

    def stop_drawing(self):
        """ Stop/disable drawing
        """
        self.set_drawing(False)

    def mag_select(self, cells=None):
        """ Select magnification region
        :cells: cells defining selection region
                selection is the rectangle including
                default: all figure cells traveled so far
                        (self.adw.pos_history)
            :returns: True if some selected else False
        """
        if cells is None:
            cells = self.adw.pos_history
        mag_info = self.get_mag_info()
        if mag_info is None:
            SlTrace.lg("Magnification is not enabled")
            return False

        ix_min, iy_min, ix_max, iy_max = self.adw.bounding_box_ci(cells=cells, add_edge=0)
        if (ix_min is None or iy_min is None
                or ix_max is None or   iy_max is None):
            self.speak_text(f"Bad selection:"
                            f" indexs: {ix_min}, {iy_min}, {ix_max}, {iy_max}")
            return False

        SlTrace.lg(f"select: ix_min:{ix_min} iy_min:{iy_min}"
                   f" ix_max:{ix_max} iy_max:{iy_max}")
        select = MagnifySelect(ix_min=ix_min, iy_min=iy_min,
                               ix_max=ix_max, iy_max=iy_max)
        mag_info.select = select
        self.show_mag_selection(mag_info)
        self.show_mag_selection(mag_info)   # HACK - first call gives shortened rectangle
                                            #        untill refresh
        self.get_cell_bounds("mag_select", cells=cells)
        self.is_selected = True
        return True

    def mag_expand_to_fill(self):
        """ Expand selection region right and left by 20%
        """
        ix_min,iy_min,ix_max,iy_max = self.bounding_box_ci(add_edge=1)
        self.mag_view(cells=[(ix_min,iy_min),(ix_max,iy_max)])

    def mag_expand_top(self):
        """ Expand selection region top and bottom by 20%
        """

    def mag_view(self, cells=None):
        """ View selected region, creating a new AudioDrawWindow
        :cells: selection cells
                default: use select default
        """
        mag_info = self.get_mag_info()
        if mag_info is None:
            SlTrace.lg("Magnification is not enabled")
            return

        # Select again, in case of change.  Doesn't hurt.
        if not self.mag_select(cells=cells):
            self.speak_text("No history to select")
            return

        display_region = mag_info.display_region
        if display_region.ncols is None:
            display_region.ncols = self.adw.grid_width
        if display_region.nrows is None:
            display_region.nrows = self.adw.grid_height

        SlTrace.lg(f"view select: {mag_info}")
        adw = self.create_magnification_window(
            self.adw.mag_info)
        if adw is None:
            self.speak_text("No magnification created")

        else:
            n_cells_created = len(adw.cells)
            self.stop_scanning()    # Stop old scanning - possible confusion
            self.speak_text(f"Magnification has {n_cells_created} cell"
                            "s" if n_cells_created != 1 else "")
            adw.Raise() # Bring to top
            adw.print_braille()   

    def remove_mag_selection(self):
        """ Remove magnify selection and marker
        """
        canv_pan = self.canv_pan
        if self.adw.mag_selection_id is not None:
            canv_pan.delete(self.adw.mag_selection_id)
            self.adw.mag_selection_id = None
            self.update()       # View change
            self.canv_pan.Refresh()
            
    def show_mag_selection(self, mag_info):
        """ Display selected region
        :ix_min: minimum ix index
        :iy_min: minimum iy index
        :ix_max: maximum iy index
        :iy_max: maximum iy index
        """
        select = mag_info.select
        canv_pan = self.canv_pan
        self.remove_mag_selection()
        ixy_ul = (select.ix_min,select.iy_min)
        ul_cx1,ul_cy1,_,_ = self.get_win_ullr_at_ixy_canvas(ixy_ul)

        ixy_lr = (select.ix_max,select.iy_max)
        _,_,lr_cx2,lr_cy2 = self.get_win_ullr_at_ixy_canvas(ixy_lr)
        self.adw.mag_selection_id = canv_pan.create_line(ul_cx1,ul_cy1,
                                                lr_cx2,ul_cy1,
                                                lr_cx2,lr_cy2,
                                                ul_cx1,lr_cy2,
                                                ul_cx1,ul_cy1,
                                                fill="#00008b",
                                                width=4,
                                                disp_type=CanvasPanelItem.DT_MAG_SEL)
        SlTrace.lg(f"Selected region\n"
                   f"  ul_cx1: {ul_cx1} ul_cy1: {ul_cy1}"
                   f"  lr_cx2: {lr_cx2} lr_cy2: {lr_cy2}"
                   )
        self.canv_pan.add_item(self.adw.mag_selection_id)
        canv_pan.RefreshRect(wx.Rect(wx_Point(ul_cx1,ul_cy1),
                                     wx_Point(lr_cx2,lr_cy2)))

    """ End of Magnify support
    """



    """ Navigate support package
    """

    def announce_can_not_do(self, msg=None, val=None):
        """ Announce we can't do something
        """
        audio_beep = self.get_audio_beep()
        if self.audio_beep:
            self.audio_beep.announce_can_not_do(msg=msg, val=val)

    def announce_location(self):
        """ Announce current / cursor location
        """
        self.pos_check(force_output=True, with_voice=True)


    def nav_enable_mouse(self):
        self.nav_audio_beep()
        self.set_enable_mouse()

    def nav_disable_mouse(self):
        self.set_enable_mouse(False)

    def set_enable_mouse(self, val=True):
        """ Enable/Disable mouse dragging operation
        :val: value to set default: True - enable
        """
        self._enable_mouse = val

    def is_enable_mouse(self):
        """ Check if mouse dragging enabled
        """
        return self._enable_mouse

    def nav_echo_on(self):
        self._echo_input = True

    def nav_echo_off(self):
        self._echo_input = False

    def nav_add_loc(self):
        """ Add At location info to report
        """
        self.key_set_rept_at()

    def nav_audio_beep(self):
        """ Use audio beeps to aid positioning
        """
        self.set_using_audio_beep()
        self.nav_echo_off()

    def nav_no_audio_beep(self):
        """ Use audio beeps to aid positioning
        """
        self.set_using_audio_beep(False)

    def nav_no_add_loc(self):
        """ Remove At location info to report
        """
        self.key_set_rept_at(False)

    def nav_logt(self):
        """ Log talking
        """
        self.key_log_speech()

    def nav_no_logt(self):
        self.key_log_speech(False)

    def nav_make_invisible(self):
        self.key_visible(False)

    def nav_make_visible(self):
        self.key_visible()

    def nav_show_marked(self):
        """ Show marked cells
        """
        self.set_show_marked()

    def nav_make_talk(self):
        self.key_talk()

    def nav_redraw(self):
        self.adw.draw_cells()

    def nav_say_position(self):
        self.pos_report(force_output=True)

    def set_show_marked(self,val=True):
        """ Show marked "invisible" cells
        """
        self._show_marked = val

    """ End of Navigate support
    """

    """ Automate functions for menu access
    """
    def do_menu_str(self, menu_str=None):
        """ Execute initial navigate string, if any
            wait on output before each cmd action
        :menu_str: string default: use self.menu_str
        """
        if menu_str is None:
            menu_str = self.menu_str
        if menu_str is None or menu_str == "":
            return

        menu_cmds = menu_str.split(';')
        for cmd in menu_cmds:
            cmd = cmd.strip()
            cmd_type, cmd_letters = cmd.split(':')
            menu_scs = self.get_menu_item_scs(cmd_type)
            if menu_scs is None:
                raise Exception("No command short cut {cmd_type} in {cmd}")
            for c in cmd_letters:
                cmd_command = self.get_menu_cmd(cmd_type, c)
                if cmd_command is None:
                    raise Exception("No command {cmd_type}:{c}")
                self.wait_on_output()
                cmd_command()

    def do_key_str(self, key_str=None):
        """ Execute initial key string, if any
            wait on output before each cmd action
        :key_str: string default: use self.nav_str
        """
        slow_key_str = SlTrace.trace("slow_key_str")
        if key_str is None:
            key_str = self.key_str
        if key_str is None or key_str == "":
            return

        SlTrace.lg(f"do_key_str: {key_str}")
        syms = key_str.split(";")
        for sym in syms:
            SlTrace.lg(f"press: {sym}")
            self.wait_on_output()
            self.key_cmd_proc.put_key_cmd(sym)



    def pause(self, time_sec):
        """ Pause for time (sec) while allowing update events
        :time: pause time in seconds
        """
        end_time = time.time() + time_sec
        SlTrace.lg(f"pause: end_time:{end_time}")
        last_time = time.time()
        while True:
            now = time.time()
            if now > end_time:
                break

            if now > last_time + 30:
                print(f"pause time left:{end_time-now:.2f}")
                last_time = now
            self.update()


    """ key / mouse operation
    and those actions close to that
    """

    def motion(self, x, y):
        """ Mouse motion in  window
        """
        if not self.is_enable_mouse():
            return      # Ignore mouse motion 

        if self.motion_level > 1:
            SlTrace.lg("Motion Recursion: motion_level({self.motion_Level} > 1")
            self.motion_level = 0
            return

        self.set_xy((x, y))
        x,y = self.get_xy()
        x,y = x + self.x_min, y + self.y_min
        self.win_x,self.win_y = x,y
        SlTrace.lg(f"motion x={x} y={y}", "aud_motion")
        quiet = self._drawing   # move quietly if drawing
        self.move_to(x,y, quiet=quiet)
        #self.pos_x = x 
        #self.pos_y = y
        #self.pos_check()
        self.motion_level -= 1
        return              # Processed via pos_check()



    def set_xy(self, xy):
        """ Set our internal win x,y
        :xy: x,y tuple as new win coordinates
        :returs: (x,y) tuple
        """
        self.x,self.y = xy
        return xy

    def get_xy(self):
        """ Get current xy pair
        :returns: (x,y) tuple
        """
        return self.x, self.y

    def get_xy_canvas(self, xy=None):
        """ Get current xy pair on canvas (0-max)
        :xy: xy tuple default: current xy
        :returns: (x,y) tuple
        """
        if xy is None:
            xy = self.get_xy()
        x,y = xy
        return x-self.x_min, y-self.y_min
    
    def set_win_fract(self, val):
        """ Set fraction indicator
        :val: new win_fract
        :returns: new win_fract
        """
        self.win_fract = val
        return val

    def get_win_fract(self):
        return self.win_fract


    def set_x_min(self, val):
        """ Set min
        :val: new x_min
        :returns: new x_min
        """
        self.x_min = val
        return val

    def get_x_min(self):
        return self.x_min

    def set_x_max(self, val):
        """ Set max
        :val: new x_max
        :returns: new x_min
        """
        self.x_max = val
        return val

    def get_x_max(self):
        return self.x_max


    def set_y_min(self, val):
        """ Set min
        :val: new x_min
        :returns: new x_min
        """
        self.y_min = val
        return val

    def get_y_min(self):
        return self.y_min

    def set_y_max(self, val):
        """ Set max
        :val: new y_max
        :returns: new x_min
        """
        self.y_max = val
        return val

    def get_y_max(self):
        return self.x_max


    def on_button_1(self, x, y):
        """ Mouse button in window
        """
        self.set_xy((x, y))
        x,y = self.get_xy()
        x,y = x + self.x_min, y + self.y_min
        self.win_x,self.win_y = x,y
        SlTrace.lg(f"motion x={x} y={y}", "aud_motion")
        self.move_to(x,y, quiet=True)
        cell = self.get_cell_at()
        if SlTrace.trace("mouse_cell"):
            mag_info = self.get_mag_info()
            ix,iy  = self.get_ixy_at()
            SlTrace.lg(f"x:{x},y:{y}"
                       f" ixy:{(ix,iy)}  cell: {cell}")
            ###???mag_info.base_canvas.show_mag_info_items(mag_info, ix=ix, iy=iy)

        if cell is None:
            if self.is_pendown():
                if cell is None:
                    new_cell = self.create_cell()
                    self.display_cell(new_cell)
        else:
            self.set_visible_cell(cell)
        self.pos_check()

    def on_button_1_motion(self, x, y):
        """ Motion with button down is
        treated as mouse click at point
        """
        if self.is_enable_mouse():
            self.on_button_1(x, y)

    def on_key_press(self, event):
        """ Key press event
        :event: Actual event
        """
        keysym = event.keysym
        self.key_press(keysym)

    def key_press(self, keysym):
        """ Actual or simulated key event
        :keysym: Symbolic key value/string
        """
        keyslow = keysym.lower()
        SlTrace.lg(f"on_key_press({keysym}) _multi...{self._multi_key_progress}", "motion")
        if keysym == 'Alt_L':
            return  # Ignore ALT
        self.key_echo(keysym)
        if self._multi_key_progress:
            self.key_multi_process(keysym)
            return

        if keysym == 'Escape':
            self.key_escape()
        elif keysym == 'Up':
            self.key_up()
        elif keysym == 'Down':
            self.key_down()
        elif keysym == 'Left':
            self.key_left()
        elif keysym == 'Right':
            self.key_right()
        elif keysym in "1234567890":
            self.key_digit(keysym)
        elif keyslow == "a":
            self.key_to_hv_move("first")
        elif keyslow == "b":
            self.key_to_hv_move("second")
        elif keyslow == "e":  # Erase current position with current color
            self.key_mark(False)
        elif keyslow == "g":
            self.key_goto()  # Goto closest figure
        elif keyslow == "h":
            self.key_help()  # Help message
        elif keyslow == "j":
            self.key_magnify(self.MAG_PARENT)  # Jump to magnify parent
        elif keyslow == "k":
            self.key_magnify(self.MAG_CHILD)  # jump to magnify child
        elif keyslow == "c":  # Change color
            self.key_color_change()
        elif keyslow == "u":  # raise pen - for subsequent not visible
            self.key_pendown(False)
        elif keyslow == "d":
            self.key_pendown()  # lower pen - for subsequent visible
        elif keyslow == "m":  # Mark current position with current color
            self.key_mark()
        elif keyslow == "p":
            self.key_report_pos()  # Report position
        elif keyslow == "r":
            self.key_report_pos_horz()  # Report horizontal position
        elif keyslow == "t":
            self.key_report_pos_vert()  # Report vertical position
        elif keyslow == "x":
            self.key_to_hv_move("original")
        elif keyslow == "z":
            self.key_clear_display()  # Clear display
        elif keyslow == "w":
            self.key_write_display()  # Write(print) out figure
        elif keyslow == "win_l":
            pass  # Ignore Win key
        else:
            self.key_unrecognized(keysym)

    """
    keyboard commands
    """
    def key_echo(self,keysym):
        """ Echo key, if appropriate
        :keysym; key symbol
        """
        if self._echo_input:
            self.adw.speaker_control.speak_text(keysym, msg_type='ECHO')

    def key_flush(self, keysym):
        """ Do appropriate flushing
        :keysym: key symbol
        """
        self.escape_pressed = True  # Let folks in prog know
        self._multi_key_progress = False
        self._multi_key_cmd = False
        self.flush_rep_queue()
        self.stop_speak_text()
        self.escape_pressed = False

    def key_escape(self):
        SlTrace.lg("Escape pressed")
        #self._multi_key_progress = False    # Stop multi key processing   
        self.key_flush(keysym="Escape")

    def goto_cell(self, ix=None, iy=None):
        """ Move cursor to center of cell
        :ix: cell's ix index
        :iy: cell's iy index
        """
        win_xc,win_yc = self.get_cell_center_win(ix,iy)
        self.move_to(win_xc,win_yc)
        self.add_to_goto_cell_list((ix,iy))
        if self._track_goto_cell:
            self.mark_cell((ix,iy))

    def key_color_change(self):
        """ Accept color change specification
        Next input must be a string for  red, orange, yellow...
        of the rainbow.  We may increase the flexibility here.
        """
        self._multi_key_cmd = self.NAV_COLOR_CHANGE
        self._multi_key_progress = True
        SlTrace.lg(f"key_color_change: ")
        SlTrace.lg(f"cmd: {self._multi_key_cmd}")
        SlTrace.lg(f"multi...{self._multi_key_progress}")

    def key_color_changeing(self, keysym):
        """ Process color changeing
        :keysym: color letter
        """
        color_letter = keysym.lower()
        if color_letter in self.color_letters:
            color = self.color_letters[color_letter]
            self.set_color(color)
            if self.is_at_cell():
                self.set_cell()
        else:
            self.speak_text(f"Don't recognize {color_letter} for color")
        self._multi_key_cmd = None
        self._multi_key_progress = False

    def key_multi_process(self, keysym):
        """ Process multiple keys
        :keysym: next symbol
        """
        if keysym == 'Escape':
            self.speak_text('Escape break')
            self.key_escape()
            return
        if self._multi_key_cmd == self.NAV_COLOR_CHANGE:
            self.key_color_changeing(keysym)
        else:
            self.speak_text("Unrecognized multi-key process")
            self.key_escape()

    def is_pendown(self):
        """ Test if pen is down (marking)
        """
        return self._pendown

    def key_pendown(self, val=True):
        """ Lower/raise pen (starting,stopping) drawing
        :val: lower pen, if True else raise pen
        """
        self._pendown = val

    def key_write_display(self):
        """ Write display
        """
        if self.title is not None:
            title = self.title
        else:
            title = 15*"_" + " Braille " + 15*"_"
        self.print_braille(title=title)

    def key_clear_display(self):
        """ Clear display figure
        """
        self.clear_cells()
            
            



    def set_visible_cell(self, cell, val=True):
        """ Set cells visible/invisible
        Useful to give sighted a vision
        :cell: figure cell
        :val: set visible Default: True
        """
        cell._visible = val
        self.show_cell(ixy=(cell.ix,cell.iy))


    def show_cell(self, ixy=None):
        cells = self.get_cells()
        if ixy in cells:
            cell = cells[ixy]
            self.display_cell(cell)


    def key_help(self):
        """ Help - list keyboard action
        """
        help_str = """
        h - say this help message
        Up - Move up through run of same color/space
        Down - Move down through run of same color/space
        Left - Move left through run of same color/space
        Right - Move right through run of same color/space
        DIGIT - Move one square in direction (from current square):
           7-up left    8-up       9-up right
           4-left       5-mark     6-right
           1-down left  2-down     3-down right
              0-erase
        a - move to first(Left if Horizontal, Top if Vertical)
        b - move to second(Right if Horizontal, Bottom if Vertical)
        c<roygbiv> - set color red, orange, ...
        d - pendown - mark when we move
                
        g - Go to closest figure
        j - jump up to reduced magnification
        k - jump down to magnified region
        m - mark location
        p - Report/Say current position
        r - Horizontal position stuff to left, to Right
        s - raise volume adjustment for tones
        t - Vertical position stuff to Top, to bottom
        u - penup - move with out marking
        v - lower volume adjustment for tones 
        w - write out braille
        x - move to original cell (after a/b Horizontal/Vertical)
        z - clear board
        Escape - flush pending report output
        """
        self.speak_text(help_str)

    def key_up(self):
        y_inc = -1
        self.move_cursor(y_inc=y_inc, general_move=True)

    def key_down(self):
        y_inc = 1
        self.move_cursor(y_inc=y_inc, general_move=True)

    def key_left(self):
        self.move_cursor(x_inc=-1, general_move=True)

    def key_right(self):
        self.move_cursor(x_inc=1, general_move=True)

    def key_exit(self):
        self.speak_text("Quitting Program")
        self.update()     # Process any pending events
        self.adw.Destroy()
        sys.exit(0)         # Quit  program

    def key_color_cell(self, set_val=True):
        """ color/clear cell - change visibility
        :set_val: change visibility default: change
        """
        cell = self.get_cell_at()
        if cell is None:
            return      # TBD beep?, red dot?

        self.set_visible_cell(cell, val=set_val)
        self.update()

    def key_magnify(self, option):
        """ Magnify window jumping
        :option: options
                MAG_PARENT - jump to parent if one
                MAG_CHILD - jump to child 1'st
        """
        mag_info = self.get_mag_info()
        if mag_info is None:
            self.speak_text("Magnification is not enabled")
            return

        if option == self.MAG_PARENT:
            parent = mag_info.parent_info
            if parent is None:
                self.speak_text("No magnification parent")
                return
            display = parent.display_window
        elif option == self.MAG_CHILD:
            children = mag_info.child_infos
            if len(children) == 0:
                self.speak_text("No magnification child")
                return
            display = children[0].display_window
        else:
            raise Exception(f"Unrecognized magnify option: {option}")

        self.adw_window_display(display)

    def adw_window_display(self, window):
        """ Bring this window to focus
        :window: (AudioDrawWindow) to display (switch to)
        """
        """ Bring this window to focus
        """
        self.speak_text("Showing window")
        ###wxport###root = self.mw
        ###wxport###root.focus_force()
        ###wxport###root.lift()
        ###wxport###root.attributes('-topmost', 1)

    def key_talk(self, val=True):
        """ Enable / Disable talking
        """
        self.do_talking = val
        SlTrace.lg(f"do_talking:{self.do_talking}")

    def key_to_hv_move(self, end_pos="first"):
        """ Move to end of previous horizontal(r), vertical(t)
        report
        :end_pos: "first" - first end (horizontal-left, vertical-top)
                  "second" - second end(horizontal-right, vertical-bottom)
                  "original" - original position
                  default: first
        """
        if self._loc_list_first is None:
            return      # No current target

        if end_pos == "first":
            self.move_to_ixy(*self._loc_list_first)
        elif end_pos == "second":
            self.move_to_ixy(*self._loc_list_second)
        elif end_pos == "original":
            self.move_to_ixy(*self._loc_list_original)
        else:
            audio_beep = self.get_audio_beep()
            audio_beep.announce_can_not_do()


    def key_report_pos(self):
        """ Report current position with voice
        """
        self.pos_check(force_output=True, with_voice=True)

    def get_cells_in_dir(self, ixy, dir):
        """ Get list of cells/locations from cell in given direction
        :ixy: ixy cell tuple
        :dir: direction (change-x, change-y) tuple
        :returns: list of locations:
                    BraillCell when location contains a cell
                     ix,iy-tuples when location does not
                List stops at edge
        """
        loc_list = []
        loc = ixy
        chg_x, chg_y = dir
        while True:
            loc_x, loc_y = loc
            loc_x += chg_x
            loc_y += chg_y
            if chg_x > 0:
                if loc_x > self.get_ix_max():
                    break   # Right edge
            if chg_x < 0:
                if loc_x < self.get_ix_min():
                    break   # Left edge
            if chg_y > 0:
                if loc_y > self.get_iy_max():
                    break   # Bottom edge
            if chg_y < 0:
                if loc_y < self.get_iy_min():
                    break   # Top edge

            loc = (loc_x,loc_y)
            cell = self.get_cell_at_ixy(loc)
            if cell is not None:
                loc_list.append(cell)
            else:
                loc_list.append(loc)
        return loc_list

    def set_color(self, color):
        """ Set current color
        """
        self._color = color

    def get_color(self):
        """ Get current color
        """
        return self._color

    def loc_list_target(self, pos_ixy, name, dir):
        """ Create target (msg, ixy) of search
        msg: text description of range
        ixy: ixy tuple of position at end
        
        Where:
        msg:  N {name} type
        where name:= "right", "left",...,
        target: (ix,iy) of location at end
        
        :pos_ixy: curent location tuple
        :name: type direction e.g. "left"
        :dir: chg-x,chg-y in index up =>  y increases
        :returns: (msg_text, target_ixy)
        """
        cell = self.get_cell_at_ixy(pos_ixy)
        loc_list = self.get_cells_in_dir(ixy=pos_ixy, dir=dir)
        msg = ""
        target_ixy = pos_ixy

        if cell is not None:
            colors = {}         # Inside figure
            ncell = 0
            ntblank = 0         # Count trailing blanks if at edge
            cell_end = None     # Set if terminating cell
            for lcell in loc_list:
                if isinstance(lcell, BrailleCell):
                    ncell += 1
                    colors[lcell.color_string()] = 1
                    target_ixy = (lcell.ix, lcell.iy)   # move as string grows
                else:
                    if ncell == 0:
                        for ltblank in loc_list:
                            if not isinstance(ltblank, tuple):
                                cell_end = ltblank   # Set if we have a cell at end
                                target_ixy = (cell_end.ix, cell_end.iy)
                                break
                            ntblank += 1
                            target_ixy = ltblank


                    break
            if ncell > 0:
                plr = "s" if ncell > 1 else ""      # part of string
                msg += f"{ncell} "
                msg +=  '&'.join(sorted(colors.keys()))
                msg += plr
                msg += f" to {name}"
            else:
                if ntblank > 0:                 # Single cell
                    plr = "s" if ntblank  > 1  else ""
                    msg += f"{ntblank} "
                    msg += f"blank{plr}"
                    if cell_end is not None:
                        msg += f" to a {cell_end.color_string()}"
                    msg += f" at {name}"
        else:
            nblank = 0      # Outside figure
            ntcell = 0      # Number of trailing cells
            cell_end = None         # Set if we have a cell at end
            tcell_colors = {}
            for loc_or_cell in loc_list:
                if isinstance(loc_or_cell, tuple):
                    nblank += 1
                    target_ixy = loc_or_cell    # move along blanks
                else:
                    cell_end = loc_or_cell    # Cell after end
                    target_ixy = (cell_end.ix,cell_end.iy)
                    if nblank == 0:
                        for ltcell in loc_list[nblank:]:
                            if not isinstance(ltcell, BrailleCell):
                                break
                            ntcell += 1
                            tcell_colors[ltcell.color_string()] = 1
                            target_ixy = (ltcell.ix, ltcell.iy)

                    break
            if nblank > 0:      # Are there a string of blanks
                plr = "s" if nblank  > 1  else ""
                msg = f"{nblank} blank{plr} to {name}"
                if cell_end is not None:
                    msg += f" to a {cell_end.color_string()}"
            else:
                if ntcell > 0:
                    msg += f"{ntcell} "
                    msg +=  '&'.join(sorted(tcell_colors.keys()))
                    plr = "s" if ntcell  > 1  else ""
                    msg += plr
                msg += f" to {name}"
        return (msg,target_ixy)

    def key_raise_vol_adj(self):
        """ Raise volume adjustment
        """
        self.raise_vol_adj()

    def key_lower_vol_adj(self):
        """ Raise volume adjustment
        """
        self.lower_vol_adj()

    def key_report_pos_horz(self):
        """ Report current horizontal position
                if in figure cell:
                    N left of colors N right of colors
                else:
                    N left of blank N right of blank
        Currently left == neg x, right == pos x
        """
        pos_ixy = self.get_ixy_at()
        msg_left, loc_left_end = self.loc_list_target(pos_ixy,
                                                      name="left", dir=(-1,0))
        msg_right, loc_right_end = self.loc_list_target(pos_ixy,
                                                        name="right", dir=(1,0))
        self._loc_list_original = pos_ixy
        self._loc_list_first = loc_left_end
        self._loc_list_second = loc_right_end
        self.speak_text(msg_left)
        self.speak_text(msg_right)

    def key_report_pos_vert(self):
        """ Report current vertical position
                if in figure cell:
                    N colors to top
                    N colors to bottom
                else:
                    N blanks above to color
                    N blanks of blank
        Currently left == neg x, right == pos x
        """
        dir_up = (0,-1)
        dir_down = (0,1)
        pos_ixy = self.get_ixy_at()
        msg_top, loc_top_end = self.loc_list_target(pos_ixy,
                                                    name="above", dir=dir_up)
        msg_bottom, loc_bottom_end = self.loc_list_target(pos_ixy,
                                                          name="below", dir=dir_down)
        self._loc_list_original = pos_ixy
        self._loc_list_first = loc_top_end
        self._loc_list_second = loc_bottom_end

        self.speak_text(msg_top)
        self.speak_text(msg_bottom)

    def key_silent(self):
        """ Disable sound
        """
        self.make_silent(val=True)

    def make_noisy(self):
        """ Enable sound
        """
        self.make_silent(val=False)

    def make_silent(self, val=True):
        self.set_silent(val)

    def key_space(self):
        """ repeat last key cmd
        """
    def key_tab(self):
        """ repeat last key cmd 4 times
        """

    def key_unrecognized(self, keyslow):
        """ Process unrecognized key
        :keyslow: key symbol (lower case)
        """
        self.speak_text(f"Don't understand {keyslow}")


    def key_backspace(self):
        """ retract last key command
        """

    def key_log_speech(self,log=True):
        """ turn on/off logging of speech/talking
        Turn off if logging/printing impairs NVDA/JAWS
        :log: turn on logging Default: turn on
        """
        self.logging_speech = log
        SlTrace.lg(f"logging_speech:{log}")

    def flush_rep_queue(self):
        self.pos_rep_queue = []

    def key_set_rept_at(self, set_val=True):
        """ Turn on/off "addition of at location" on reporting
        """
        self.rept_at_loc = set_val
        SlTrace.lg(f"rept_at_loc:{self.rept_at_loc}")

    def key_visible(self,val=True):
        """ turn on/off visibility of figure
        
        :val: turn on visibility Default: turn on
        """
        self.set_visible(val)

    def check_if_drawing(self, x=None, y=None,
                         force_output=False):
        """ Check on drawing
        Add report string to report queue
        :x: x-coordinate (win) default: self.pos_x
        :y: y-coordinate (win) default: self.pos_y
        :force_output: if and output, clear queue first
        """
        dist, dist_x, dist_y, cell = self.distance_from_drawing(x,y)
        if dist is None or dist > 0:
            return None,None,None,None       # Not on figure
        if cell is not None:
            self.pos_rep_queue.append(("draw", (cell.ix,cell.iy)))
            return 0,dist_x,dist_y,cell      # Force "on figure"

        return dist,dist_x,dist_y,cell

    def check_distance(self, x=None, y=None,
                       force_output=False):
        """ Check on distance to drawing
        Add report string to report queue
        :x: x-coordinate (win) default: self.pos_x
        :y: y-coordinate (win) default: self.pos_y
        :force_output: if and output, clear queue first
        :returns: dist, dist_x, dist_y, cell
                where: dist - distance
                        dist_x - in cells right
                        dist_y - in cells down
                        cell - closest cell, if one, else None
        """

        dist, dist_x, dist_y, cell = self.distance_from_drawing(x,y)
        if dist is not None and dist > 0:
            if force_output:
                self.pos_rep_force_output = True
                self.pos_rep_queue = []
            self.pos_rep_queue.append(("dist", dist_x, dist_y))
        return dist, dist_x, dist_y, cell

    def distance_from_drawing(self, x=None, y=None):
        """ Approximately minimum distance in cells from point
            to some displayed cell
        :x: window x-coordinate default: current x position
        :y: window y-coordinate default: current y position
        :returns: distance, number_x_cells, number_y_cells,
                             cell iff inside cell
                None - if no figure
                 (0 only iff already in displayed cell)
        """
        return self.distance_from_drawing_win(x=None, y=None)


    def distance_from_drawing_win(self, x=None, y=None):
        """ Approximately minimum distance in cells from point
            to some displayed cell, using window coordinates
        :x: window x-coordinate default: current x position
        :y: window y-coordinate default: current y position
        :returns: distance, number_x_cells, number_y_cells,
                             cell iff inside cell
                None - if no figure
                 (0 only iff already in displayed cell)
        """
        win_x,win_y = self.get_xy()
        if x is None:
            x = win_x
        if y is None:
            y = win_y
        if x is None:
            return  None,None,None,None # Nothing to report

        cells = self.get_cells()
        # Check/Report on distance from figure
        if (cells is None
                or len(cells) == 0):
            return 999,999,999, None   # Far....p

        cell = self.get_cell_at((x,y))
        if cell is not None:
            cell_closest = cell      # We're there
            return 0,0,0, cell        # On drawing

        pt_ixy = self.get_ixy_at((x,y))
        cell_closest = None         # Set if found
        min_dist = None
        min_dist_x = 0      # x,y offset at min dist
        min_dist_y = 0
        pt_ix, pt_iy = pt_ixy
        for cell_ixy in self.get_cells():
            cell_ix, cell_iy = cell_ixy
            dist = sqrt((cell_ix-pt_ix)**2 + (cell_iy-pt_iy)**2)
            if min_dist is None or dist < min_dist:
                min_dist = dist
                min_dist_x = cell_ix - pt_ix
                min_dist_y = cell_iy - pt_iy
                cell_closest = self.get_cells()[cell_ixy]    # Closest so far
        if min_dist <= 0:
            min_dist = .001     # Saving 0 for in display element
        return min_dist, min_dist_x, min_dist_y, cell_closest

    def pos_check(self, x=None, y=None, force_output=False, with_voice=False):
        """ Do position checking followed by report queue processing
        :x: x postion default: current
        :y: y position default: current
        :force_output: force output, flushing current queue
        :with_voice: say if, even if beep enable
        """
        self.pos_check_1(x=x, y=y, force_output=force_output)
        self.pos_report(
            force_output=force_output, with_voice=with_voice)  # Handles reporting, queue, timeing

    def pos_check_1(self, x=None, y=None, force_output=False):
        """ Position check to see if reporting is warranted
        We use this to reduce the probability that too frequent
        reporting will cause the spoken reports to cause noticeable
        backup in response
        :x: x-coordinate default: self.pos_x (last movement)win
        :y: y-coordinate default: self.pos_y
        """
        ###if self.running:
        ###    self.mw.after(int(self.pos_check_interval*1000), self.pos_check)
        now = datetime.now()
        if (not force_output
                and (now-self.pos_rep_time).total_seconds()
                < self.pos_rep_interval):
            return              # No reporting this often

        self.check_distance(x=x, y=y,
                            force_output=force_output)  # check on distance to drawing
        self.check_if_drawing(x=x, y=y,
                              force_output=force_output)    # check if on drawing
            


    def pos_report(self, *args, force_output=False, with_voice=False):
        """ Report position, from queue if sufficient time since last
        report. Reduce queue if too long
        :*args: optional args to add to report queue
        :force_output: force this output, clearing queue, wait-time
        :with_voice: say it default: False - do as set
        """
        if self.pos_rep_force_output:
            force_output = True
            self.pos_rep_force_output = False   # clear for next
        if len(args) > 0:
            rep_type, *rep_args = args
            if rep_type ==  "msg":
                force_output = True
            if force_output:
                self.pos_rep_queue = []     # force flushes queue
                self.pos_rep_queue.append((args))  # Add report

        '''
        now = datetime.now()
        if (not force_output
            and (now-self.pos_rep_time).total_seconds()
            < self.pos_rep_interval):
            return          # too soon since last report
        '''
        '''
        # Remove excess entries
        while len(self.pos_rep_queue) > self.pos_rep_queue_max:
            self.pos_rep_queue.pop(0)   # Discard oldest
        if self.escape_pressed:
            return      # TBD still not atomic!!!!
        '''

        while len(self.pos_rep_queue) > 0:
            rep_type, *rep_args = self.pos_rep_queue.pop(0)
            if rep_type == "dist":
                x_dist, y_dist = rep_args
                x_str = ""
                if x_dist == 999:
                    rep_str = "No Drawing"
                else:
                    if x_dist < 0:
                        x_str = f"left {-x_dist}"
                    elif x_dist > 0:
                        x_str = f"right {x_dist}"
                    y_str = ""
                    if y_dist < 0:
                        y_str = f"up {-y_dist}"
                    elif y_dist > 0:
                        y_str = f"down {y_dist}"
                    rep_str = x_str
                    if rep_str != "":
                        rep_str += " "
                    rep_str += y_str
            elif rep_type == "draw":
                cell_ixiy = rep_args[0]
                cell = self.get_cells()[cell_ixiy]
                color = cell._color
                rep_str = color
            elif rep_type == "msg":
                rep_str = rep_args[0]

            ix,iy = self.get_ixy_at()
            SlTrace.lg(f"from get_ixy_at(): ix:{ix} iy:{iy}",
                       "pos_tracking")
            if self.is_using_audio_beep() and not with_voice:
                audio_beep = self.get_audio_beep()
                audio_beep.announce_pcell((ix,iy), dly=0)
                ###self.update()
                grid_path = self.get_grid_path()
                if grid_path is not None:
                    pcells = grid_path.get_next_positions(max_len=self.get_look_dist())
                    ###self.update()
                    audio_beep.announce_next_pcells(pc_ixys=pcells)
            else:
                if self.rept_at_loc or with_voice:
                    rep_str += f" at row {iy+1} column {ix+1}"
                if (force_output
                        or ix != self.pos_rep_ix_prev    # Avoid repeats
                        or iy != self.pos_rep_iy_prev):
                    self.win_print(rep_str, end= "\n")
                    self.speak_text(rep_str)
                    self.pos_rep_time = datetime.now()  # Time of last report
                    self.pos_rep_ix_prev = ix
                    self.pos_rep_iy_prev = iy
                    self.pos_rep_str_prev = rep_str

    def key_goto(self):
        """ Go to closest figure
            go to figure not in one already
            else go one step within current figure, toward
            longest inside path
        """
        dist, dist_x, dist_y, cell = self.distance_from_drawing()
        if dist is None or cell is None:
            return              # Nowhere

        start_cell = (cell.ix,cell.iy)
        gfg = GridFillGobble(self.get_cells(),start_cell)
        self.goto_travel_list = gfg.find_region(start_cell)
        if dist > 0 and cell is not None:
            self.goto_cell(ix=cell.ix, iy=cell.iy)
            self.clear_goto_cell_list()
            self.add_to_goto_cell_list(start_cell)

            self.goto_travel_list_index = 0
        else:
            if len(self.goto_travel_list) == 0:
                return  # No travel list

            if not hasattr(self, 'goto_travel_list_index'):
                SlTrace.lg("goto_travel_list_index forced to zero")
                self.goto_travel_list_index = 0
            goto_idx = self.goto_travel_list_index + 1
            goto_idx %= len(self.goto_travel_list)
            self.goto_travel_list_index = goto_idx
            new_cell= self.goto_travel_list[goto_idx]
            self.goto_cell(ix=new_cell[0], iy=new_cell[1])


    def win_print(self,*args, dup_stdout=False, **kwargs):
        """ print to listing area
        :*args: print-like args
        :**kwargs: print-flags
        :dup_stdout:  send duplicate to stdout
        """
        lstr = ""
        if "sep" in kwargs:
            sep = kwargs["sep"]
        else:
            sep = " "
        for ls in args:
            lstr += (str(ls)+sep)
        if dup_stdout:
            print(*args, **kwargs)
        ###wxport###self.win_print_entry.delete(0, tk.END)
        ###wxport###self.win_print_entry.insert(0, lstr)
        #time.sleep(.2)

    def key_digit(self, keyslow):
        """ Process digit key as direction
        :keyslow: 1-9 move in direction
                    with 0,5 dependent on self._drawing
                    If drawing: self._drawing == True
                        5 - Mark position with new cell
                        0 - Remove cell at position
                    else:
                        5,0 - announce current location
        """
        if keyslow == "5":
            if self._drawing:
                self.key_mark()
            else:
                self.announce_location()
        elif keyslow == "0":
            if self._drawing:
                self.key_mark(False)
            else:
                self.announce_location()
        elif keyslow in "123456789":
            self.key_direction(keyslow)
        else:
            self.key_unrecognized(keyslow)

    def delete_cell(self, cell=None):
        """ Delete cell
        :cell: cell to delete default: current cell
        """
        if cell is None:
            cell = self.get_cell_at()
        if cell is None:
            return

        self.erase_cell(cell)
        cells = self.get_cells()
        del cells[(cell.ix,cell.iy)]


    def key_mark(self, val=True):
        """ Mark/Erase current location with current color
            if empty create cell, else change current cell
        :val: True - mark location default: True
                False - erase location
        """
        #if not self._drawing:
        #    self.announce_can_not_do("Not drawing", val)

        if val:
            cell = self.get_cell_at()
            if cell is None:
                ixy = self.get_ixy_at()
                cell = self.complete_cell(cell=ixy)
            else:
                cell.color_cell()
            self.display_cell(cell)
        else:
            cell = self.get_cell_at()
            if cell is None:
                return
            
            self.refresh_cell(cell)      # Mark as dirty
            self.delete_cell(cell)


    def key_direction(self, keyslow):
        """ Process key direction command
        :keyslow: key 123 4 6 789
        """
        inc_x, inc_y = self.digit_dir[keyslow]
        self.move_cursor(x_inc=inc_x, y_inc=inc_y)
        

    def is_using_audio_beep(self):
        return self._using_audio_beep

    def set_using_audio_beep(self, using=True):
        self._using_audio_beep = using

    def get_audio_beep(self):
        """ Get access to audio tone feedback for location
        """
        return self.audio_beep

    def setup_beep(self):
        """ Setup audio beep location reporting
        """
        self.audio_beep = AudioBeep(self, self.silence)



    def update(self, full=False):
        """ Update display
        """
        #self.adw.update(full=full)

    def update_idle(self):
        """ Update pending
        """
        #self.adw.update_idle()


    """
    ############################################################
                       Links to scanner
    ############################################################
    """

    def set_cell_time(self, time):
        """ Set cell tone duration hoped
        :time: cell time in seconds
        """
        self.scanner.set_cell_time(time=time)

    def set_space_time(self, time):
        """ Set space tone duration hoped
        :time: cell time in seconds
        """
        self.scanner.set_space_time(time=time)

    def set_combine_wave(self, val=True):
        """ Enable/disable combine wave scanning mode
        :val: value for mode
        """
        self.scanner.set_combine_wave(val=val)

    def set_no_item_wait(self, val=True):
        """ Set/clear scanning no_wait option
        :val: True - no waiting
        """
        self.scanner.set_no_item_wait(val=val)

    def set_profile_running(self, val=True):
        """ Set/clear profiler running
        :val: True set profiling default: True
        """
        self.scanner.set_profile_running(val=val)

    def set_scan_len(self, scan_len):
        """ Set number of items to current scan list
        :scan_len: number of items to add each trip
        """
        self.scanner.set_scan_len(scan_len=scan_len)

    def flip_skip_run(self):
        """ Flip skipping run of equals
        """
        self.scanner.flip_skip_run()

    def set_skip_space(self, val):
        self.scanner.set_skip_space(val=val)

    def set_skip_space_max(self, val):
        self.scanner.set_skip_space_max(val=val)


    def is_skip_space(self):
        return self.scanner.is_skip_space()

    def is_skip_run(self):
        return self.scanner.is_skip_run()

    def set_skip_run(self, val):
        self.scanner.set_skip_run(val=val)

    def set_skip_run_max(self, val):
        self.scanner.set_skip_run_max(val=val)

    def flip_skip_space(self):
        """ Flip skipping spaces
        """
        self.scanner.flip_skip_space()

    def get_vol(self, ix, iy, eye_ixy_l=None, eye_ixy_r=None):
        """ Get tone volume for cell at ix,iy
        volume(left,right)
        Volume(in decibel): k1*(k2-distance from eye), k1=1, k2=0
        :ix: cell ix
        :iy: cell iy
        :eye_xy_l: left eye/ear at x,y default: self.eye_xy_l
        :eye_xy_r: right eye/ear at x,y  default: self.eye_xy_r
        return: volume(left,right) in decibels
        """
        return self.scanner.get_vol(ix=ix, iy=iy, eye_ixy_l=eye_ixy_l, eye_ixy_r=eye_ixy_r)

    def set_scanning(self, cells=None):
        self.scanner.set_scanning(cells=cells)

    def start_scanning(self):
        self.remove_mag_selection()
        self.scanner.start_scanning()


    def stop_scanning(self):
        self.scanner.stop_scanning()


    """
    ############################################################
                       Links to menus
    ############################################################
    """
    def get_menu_scs(self):
        """ Get menu (menubar) short cuts
        """
        return self.menus.get_menu_scs()

    def get_menu_item_scs(self, menu_sc):
        """ Get list of menu item short cuts
        :menu_sc: menu shortcut
        :returns: list of menu itme shortcuts
        """
        return self.menus.get_menu_item_scs(menu_sc)

    def get_menu_cmd(self, menu_sc, mi_sc):
        """ get menu cmd
        :menu_cs: menu shortcut case insensitive
        :mi_cs: menu item shortcut case insensitive
        :returns: menu cmd, if none - None
        """
        return self.menus.get_menu_cmd(menu_sc, mi_sc)
    
     
    def file_direct_call(self, short_cut):
        """ Short-cut call direct to option
        :short_cut: one letter option for call 
        """
        self.menus.file_direct_call(short_cut)

    def draw_direct_call(self, short_cut):
        """ Short-cut call direct to option
        :short_cut: one letter option for call 
        """
        self.menus.draw_direct_call(short_cut)


    def mag_direct_call(self, short_cut):
        """ Short-cut call direct to option
        :short_cut: one letter option for call 
        """
        self.menus.mag_direct_call(short_cut)


    def nav_direct_call(self, short_cut):
        """ Short-cut call direct to option
        :short_cut: one letter option for call 
        """
        self.menus.nav_direct_call(short_cut)

    def scan_direct_call(self, short_cut):
        """ Short-cut call direct to option
        :short_cut: one letter option for call 
        """
        self.menus.scan_direct_call(short_cut)

    """ End of menus links """


    """
    ############################################################
                       Links to speaker control
    ############################################################
    """


    def get_vol_adj(self):
        """ Get current volume adjustment ??? Thread Safe ???
        :returns: current vol_adjustment in db
        """
        return self.speaker_control.get_vol_adj()

    def set_vol_adj(self, adj=0.0):
        """ Set volume adjustment
        :adj: db adjustment default:0.0
        """
        self.speaker_control.set_vol_adj(adj=adj)

    def raise_vol_adj(self, db_adj=None):
        """ Adjust scanning audio level
        """
        self.speaker_control.raise_vol_adj(db_adj=db_adj)

    def lower_vol_adj(self, db_adj=None):
        """ Adjust scanning audio level
        """
        self.speaker_control.lower_vol_adj(db_adj=db_adj)


    """
    ############################################################
                       Links to adw
    ############################################################
    """
    
    def bounding_box_ci(self, cells=None, add_edge=None):
        """ cell indexes which bound the list of cells
        :cells: list of cells, (with cell.ix,cell.iy) or (ix,iy) tuples
                default: list of all cells in figure
        :add_edge: number of cells to add/subtract (if possible)
                     to enlarge/shrink box
                    default: no change
        :returns: 
                    None,None,None,None if no figure
                    upper left ix,iy  lower right ix,iy
        """
        return self.adw.bounding_box_ci(cells=cells, add_edge=add_edge)
                   
    def get_cell_bounds(self, title=None, cells=None,
                        add_edge=None, display_region=None):
        """ Get cell list bounds
        :title: optional title default: no title
        :cells: list of cells, (with cell.ix,cell.iy) or (ix,iy) tuples
                default: list of all cells in figure
        :add_edge: number of cells to add/subtract (if possible)
                     to enlarge/shrink box
                    default: no change
        :display_region: (MagnifyDisplayRegion) display region
        :returns: xmin,ymin (upper left), xmax,ymax (lower right) display
        """
        return self.adw.get_cell_bounds(title=title, cells=cells, add_edge=add_edge,
                                        display_region=display_region)

    def mark_cell(self, cell,
                  mtype=BrailleCell.MARK_SELECTED):
        """ Mark cell for viewing of history
        :cell: Cell(BrailleCell) or (ix,iy) of cell
        :mtype: Mark type default: MARK_SELECTED
        """
        self.adw.mark_cell(cell, mtype=mtype)

    def refresh_cell(self, cell):
        """ Mark cell dirty, in need of repainting
        :cell: BrailleCell
        """
        return self.adw.refresh_cell(cell)

    def get_cells_over_item(self, item):
        """ Get cells overlapping item
        :item: item(CanvasPanelItem)/id
        :returns: list of overlapping cells (BrailleCell)
        """
        return self.adw.get_cells_over_item(item)

    def update_cell(self, cell, **kwargs):
        """ Update cell, with "inplace" attribute changes 
        :**kwargs: attributes to be changed
        """
        self.adw.update_cell(cell, **kwargs)

    def redraw(self):
        """ Redraw screen
        """
        self.adw.redraw()
                   
    def create_magnification_window(self, mag_info):
        """ Create magnification
        :mag_info: MagnificationInfo containing info
        :returns: instance of AudioDrawWinfow or None if none was created
        """
        return self.adw.create_magnification_window(mag_info)

    def clear_cells(self):
        self.adw.clear_cells()

    def complete_cell(self, cell, color=None):
        """ create/Fill braille cell
            Currently just fill with color letter (ROYGBIV)
        :cell: (ix,iy) cell index or BrailleCell
        :color: cell color default: current color
        :returns: created/modified cell
        """
        return self.adw.complete_cell(cell=cell, color=color)
    
    def add_to_pos_history(self, loc_ixiy):
        """ Accumulate position history
        :loc_ixiy: (ix,iy) of current location
        """
        self.adw.add_to_pos_history(loc_ixiy)
        
    def erase_pos_history(self):
        """ Remove history, undo history marking
        """
        self.adw.erase_pos_history()

    def set_grid_path(self):
        self.adw.set_grid_path()

    def get_grid_path(self):
        return self.adw.get_grid_path()

    def set_look_dist(self, look_dist):
        self.adw.set_look_dist(look_dist=look_dist)

    def get_look_dist(self):
        return self.adw.get_look_dist()

    def get_ix_min(self):
        """ get minimum ix on grid
        :returns: min ix
        """
        return self.adw.get_ix_min()

    def get_ix_max(self):
        """ get maximum ix on grid
        :returns: min ix
        """
        return self.adw.get_ix_max()

    def get_iy_min(self):
        """ get minimum iy on grid
        :returns: min iy
        """
        return self.adw.get_iy_min()

    def get_iy_max(self):
        """ get maximum ix on grid
        :returns: min ix
        """
        return self.adw.get_iy_max()

    def get_mag_info(self):
        """ Get manification info storage
        """
        return self.adw.get_mag_info()

    def get_speaker_control(self):
        """ Get speech control
        """
        return self.adw.get_speaker_control()

    def get_cmd_queue_size(self):
        """ Get current number of entries
        :returns: number of entries
        """
        speaker_control = self.get_speaker_control()
        return speaker_control.get_cmd_queue_size()

    def get_sound_queue_size(self):
        """ Get current number of entries
        :returns: number of entries
        """
        speaker_control = self.get_speaker_control()
        return speaker_control.get_sound_queue_size()

    def get_speech_queue_size(self):
        """ Get current number of entries
        :returns: number of entries
        """
        speaker_control = self.get_speaker_control()
        return speaker_control.get_speech_queue_size()

    def get_win_ullr_at_ixy_canvas(self, ixy):
        """ Get window rectangle for cell at ixy
        :ixy: cell index tupple (ix,iy)
        """
        return self.adw.get_win_ullr_at_ixy_canvas(ixy=ixy)

    def is_at_cell(self, pt=None):
        """ Check if at cell
        :pt: x,y pair location in turtle coordinates
                default: current location
        :returns: True if at cell, else False
        """
        return self.adw.is_at_cell(pt=pt)

    def print_braille(self, title=None, shift_to_edge=None):
        """ Output braille display
        :title: title default: self.title
        :shift_to_edge: shift figure towards edge to ease finding figure
                        default: self.shift_to_edge
        """
        if shift_to_edge:
            shift_to_edge = self.shift_to_edge
        self.adw.print_braille(title=title, shift_to_edge=shift_to_edge)

    def stop_speak_text(self):
        """ Stop ongoing speach, flushing queue
        """
        self.adw.stop_speak_text()

    def create_cell(self, cell_ixy=None, color=None,
                    show=True):
        """ Create new cell ad cell_xy
        :cell_xy: ix,iy tuple default: current location
        :color: color default: curren color
        :show: show cell default:True
        :returns: cell
        """
        return self.adw.create_cell(cell_ixy=cell_ixy, color=color,
                                    show=show)

    def display_cell(self, cell, show_points=False):
        """ Display cell
        :cell: BrailleCell
        :show_points: show points instead of braille
                default: False --> show braille dots
        """
        self.adw.display_cell(cell=cell, show_points=show_points)

    def erase_cell(self, cell):
        """ Erase cell
        :cell: BrailleCell
        """
        self.adw.erase_cell(cell=cell)

    def get_cells(self):
        return self.adw.get_cells()

    def get_cell_at(self, pt=None):
        """ Get cell at location, if one
        :pt: x,y pair location in turtle coordinates
                default: current location
        :returns: cell if at, else None
        """
        return self.adw.get_cell_at(pt=pt)
    def get_cell_center_win(self, ix, iy):
        """ Get cell's window rectangle x, y  upper left, x,  y lower right
        :ix: cell x index
        :iy: cell's  y index
        :returns: window(0-max): (xc,yc) where
            xc,yc are x,y coordinates of cell's center
        """
        return self.adw.get_cell_center_win(ix=ix, iy=iy)

    def get_cell_at_ixy(self, cell_ixy):
        """ Get cell at (ix,iy), if one
        :cell_ixy: (ix,iy)
        :returns: BrailleCell if one, else None
        """
        return self.adw.get_cell_at_ixy(cell_ixy)

    def get_ixy_at(self, pt=None):
        """ Get cell(indexes) in which point resides
        If on an edge returns lower cell
        If on a corner returns lowest cell
        :pt: x,y pair location
                        in win coordinates
                default: current location
        :returns: ix,iy cell pair
                if out of bounds limit to min/max of ix,iy
        """
        return self.adw.get_ixy_at(pt=pt)

    def is_visible(self):
        """ Check on visible mode
        """
        return self.adw.is_visible()

    def count_cells(self, _=None):
        """ report number of cells in figure
        """
        cells = self.adw.cells
        SlTrace.lg(f"count_cells: adw.title: {self.adw.title}")
        SlTrace.lg(f"count_cells, cells: {cells}", "cell_specs")
        ncells = len(cells)
        self.speak_text(f"{ncells} cell"
                            "s" if ncells != 1 else "")
        color_counts = {}
        for cell_ixy in cells:
            cell = cells[cell_ixy]
            color = cell.color_string()
            if color not in color_counts:
                color_counts[color] = 0
            color_counts[color] += 1
        for color in color_counts:
            ncells = color_counts[color]
            self.speak_text(f"{ncells} {color}"
                            "s" if ncells != 1 else "")
            

    def set_cell(self, pt=None, color=None):
        """ Set cell at pt, else current cell
        If no cell at current location create cell
        :pt: at point
            default: current location
        :color: color default: current color
        """
        self.adw.set_cell(pt=pt, color=color)

    def set_visible(self, val=True):
        """ Set cells visible/invisible
        Useful to give sighted a vision
        :val: set visible Default: True
        """
        self.adw.set_visible(val=val)


    def speak_text(self, msg, dup_stdout=True,
                   msg_type=None,
                   rate=None, volume=None):
        """ Speak text, if possible else write to stdout
        :msg: text message, iff speech
        :dup_stdout: duplicate to stdout default: True
        :msg_type: type of speech default: 'REPORT'
            REPORT - standard reporting
            CMD    - command
            ECHO - echo user input
        :rate: speech rate words per minute
                default: 240
        :volume: volume default: .9            
        """
        self.adw.speak_text(msg=msg, msg_type=msg_type,
                            dup_stdout=dup_stdout,
                            rate=rate, volume=volume)

    def mainloop(self):
        self.adw.mainloop()

    def move_cursor(self, x_inc=0, y_inc=0, general_move=False):
        """ Move cursor by cell increments to center of
        cell to maximise chance of seeing cell figures
        :x_inc: x change default: no movement
        :y_inc: y change default: no movement
        :general_move: True - honor skip_space, skip_run
                        default: False
        """
        if general_move:
            self.move_cursor_general(x_inc, y_inc)
        else:
            self.move_cursor_win(x_inc=x_inc, y_inc=y_inc)

    def is_inbounds(self,ix=None, iy=None):
        """ Test if inbounds
        :ix: x index - default: don't test
        :iy: y index - default: don't test
        :returns: True iff in bounds
        """
        if ix > self.get_ix_max():
            return False
        if ix < self.get_ix_min():
            return False
        if iy > self.get_iy_max():
            return False
        if iy < self.get_iy_min():
            return False

        return True

    def move_cursor_general(self, x_inc=0, y_inc=0):
        """ Move cursor by cell increments honor scanning skip_space, skip_run
        :x_inc: x change default: no movement
        :y_inc: y change default: no movement
        """
        cells = self.get_cells()
        ix,iy = self.get_ixy_at()
        ix_end = ix_next = ix + x_inc
        iy_end = iy_next = iy + y_inc
        if not self.is_inbounds(ix=ix_next, iy=iy_next):
            self.announce_can_not_do()
            return

        skip_space = self.is_skip_space()
        skip_run = self.is_skip_run()
        ixy = (ix_next,iy_next)
        cell_first = cells[ixy] if ixy in cells else None
        color_first = cell_first.color_string() if cell_first is not None else None
        loc_list = [(ixy, cell_first)]
        while True:
            ix_next,iy_next = ix_next+x_inc, iy_next+y_inc
            if not self.is_inbounds(ix=ix_next, iy=iy_next):
                break       # Quit  if next cell is out of bounds

            ixy = (ix_next,iy_next)
            cell_next = cells[ixy] if ixy in cells else None
            color_next = cell_next.color_string() if cell_next is not None else None
            if skip_space and cell_first is None and cell_next is None:
                loc_list.append((ixy, cell_next))    # skip spaces
                continue

            if (skip_run and cell_next is not None
                    and cell_first is not None and color_next == color_first):
                loc_list.append((ixy, cell_next))
                continue
            break       # Anything else and we are done

        for loc in loc_list:        # Mark cells we've traversed
            cell = loc[1]
            if not self.is_drawing():
                self.add_to_pos_history(loc[0])   # location history
                self.mark_cell(cell)
        lc = len(loc_list)
        if lc > 1:
            if color_first is not None:
                cstr = color_first + "s"
                self.speak_text(f"{lc} {cstr}")
            else:
                self.speak_text(f"{lc} blanks")
        ix,iy = loc[0]
        self.move_to_ixy(ix=ix, iy=iy)

    def move_cursor_win(self, x_inc=0, y_inc=0):
        """ Move cursor by cell increments to center of
        cell to maximise chance of seeing cell figures
        :x_inc: x change default: no movement
        :y_inc: y change default: no movement
        """
        ix,iy = self.get_ixy_at()
        ix += x_inc
        iy += y_inc
        self.move_to_ixy(ix=ix, iy=iy)
        if self._pendown:
            self.set_cell()
        if SlTrace.trace("mouse_cell"):
            cell = self.get_cell_at()
            SlTrace.lg(f"pos_xy:{self.pos_x}, {self.pos_y}"
                       f" canvas x,y:{self.get_xy_canvas()}"
                       f" cell: {cell}")

    def move_to(self, x,y, quiet=False):
        """ Move to window loc
        Stop at edges, with message
        :x:  win x-coordinate
        :y: win y-coordinate
        :quiet: Don't announce legal move
                default:False
        """
        self.adw.move_to(x=x, y=y, quiet=quiet)


if __name__ == '__main__':
    '''
    from unittest.mock import MagicMock
    
    class AdwFake(MagicMock):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
        def exit(self):
            SlTrace.lg("adw.exit()")
            sys.exit()
        
        def get_ix_min(self):
            return 100
        
        def get_ix_max(self):
            return 0
        
        def bounding_box_ci(self, cells):
            return (100,100, 0, 0)                
    '''
    from wx_audio_draw_window import AudioDrawWindow
    from wx_adw_menus import AdwMenus
    from wx_tk_rpc_user import TkRPCUser
                  
    app = wx.App()
    frame = wx.Frame(None)
    tkr = TkRPCUser(simulated=True)
    adw = AudioDrawWindow(tkr)
   
    fte = AdwFrontEnd(adw)
    menus = AdwMenus(fte, frame=frame)
    fte.do_key_str("c;g")
    
    app.MainLoop()
    