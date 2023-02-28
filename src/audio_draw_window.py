#audio_draw_window.py    12Dec2022  crs, from audio_window.py
#                        08Nov2022  crs, Author
"""
Provide simple drawing graphical window with audio feedback
to facilitate use and examination by the visually impaired.
Uses turtle to facilitate cursor movement within screen
Adapted from audio_window to concentrate on figure drawing
as well as presentation.
"""
import sys
import tkinter as tk
import turtle as tu
from math import sqrt
import time
from datetime import datetime 

from select_trace import SlTrace
from trace_control_window import TraceControlWindow
from audio_beep import AudioBeep
from grid_fill_gobble import GridFillGobble
from grid_path import GridPath
from braille_cell import BrailleCell
from magnify_info import MagnifyInfo, MagnifySelect, MagnifyDisplayRegion

from speech_maker import SpeechMakerLocal
import pt
from pptx.util import Pt

class MenuDisp:
    """ Menu dispatch table entry
    Supporting multiple mode dispatch (e.g, Dropdown item plus command mode)
    """
    def __init__(self, label, command, underline):
        self.label = label
        self.command = command
        self.underline = underline
        self.shortcut = label[underline].lower()
        
class AudioDrawWindow:


    """
    Menu Processing functions
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
    
    def __init__(self,
        title=None, speech_maker=None,
        win_width=800, win_height=800,
        grid_width=40, grid_height=25,
        x_min=None, y_min=None,
        win_x_min=None, win_y_min=None,
        line_width=1, color="black",
        pos_check_interval= .1,
        pos_rep_interval = .1,
        pos_rep_queue_max = 1,
        visible_figure = True,
        enable_mouse = False,
        pgmExit=None,
        blank_char=",",
        drawing=False,
        show_marked=False,
        shift_to_edge=True,
        silent=False,
        look_dist=2,
        menu_str="",
        key_str="",
        mag_info=None,
        iy0_is_top=False,
                 ):
        """ Setup audio window
        :speech_maker: (SpeechMakerLocal) local access to centralized speech making
        :win_width: display window width in pixels
            default: 800
        :win_height: display window height in pixels
            default: 800
        :x_min: minimum coordinate tu
                default: win_width//2
        :y_min: minimum coordinate tu
                default: -win_height//2
        :win_x_min: minimum window(canvas) x-coordinate
        :win_y_min: minimum window(canvas) y-coordinate
        :grid_width: braille width in cells
            default: 40
        :grid_height: braille width in cells
            default: 25
        :title: window title
        :pos_check_interval: time between checks/reporting on
                cursor position  default: .1 seconds
        :pos_rep_interval: minimum time between reports
                default: .5 seconds
        :pos_rep_queue_max: maximum position report queue maximum
                default: 4
        :visible_figure: figure is visible
                default: True - visible
        :blank_char: replacement for non-trailing blanks
                    default "," to provide a "mostly blank",
                    non-compressed blank character for the
                    braille graphics
                    default: "," dot 2.
        :shift_to_edge: shift picture to edge/top
                    to aid in finding
                    default: True - shift
        :drawing: We're in drawing mode
                 default: False - no drawing
        :show_marked: Make marked cells
                shown even when invisible
                default: True
        :silent: Suppress talking / audio
                default: False
        :menu_str:  Initial menu commands
                    default=None
                    Note that interpretation is case insensitive
                    Format: <Menu Letter><option letters>; as separator
                            e.g. n:sh;d:d  for Navigator silent, help
        :enable_mouse: mouse cursor operation enabled
                    default: False                                        Drawing: start drawing
        :key_str:  Initial key symbol command string
                    Each command separated by ";" to facilitate
                    recognition of multi charater symbols
                    such as "up", "down" Note that
                    interpretation is case insensitive
        :look_dist: Max number of cells to look ahead and report
                    default: 1
        :iy0_is_top: True->cell y index increases downward from top (0)
                    default: False y index increases upward from bottom (0)
        """
        if speech_maker is None:
            raise Exception("AudioDrawWindow with no speech_maker")
        
        self.speech_maker = speech_maker
        # direction for digit pad
        self.iy0_is_top = iy0_is_top
        y_up = -1 if self.iy0_is_top else 1
        y_down = 1 if self.iy0_is_top else -1
        self.digit_dir = {"7":(-1,y_up),   "8":(0,y_up),   "9":(1,y_up),
                          "4":(-1,0),      "5":(0,0),      "6":(1,0),
                          "1":(-1,y_down), "2":(0,y_down), "3":(1,y_down)}
        
        self.speech_maker = speech_maker
        if title is None:
            title = "AudioDrawWindow"
        else:
            self.speak_text(title)
        self.title = title
        control_prefix = "AudioDraw"
        self.win_width = win_width
        self.win_height = win_height
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_height = win_height/self.grid_height
        self.pgmExit = pgmExit
        if win_x_min is None:
            win_x_min = 0
        self.win_x_min = win_x_min
        if win_y_min is None:
            win_y_min = 0
        self.win_y_min = win_y_min
        self.win_x,self.win_y = self.win_x_min,self.win_y_min
        
        if x_min is None:
            if self.iy0_is_top:
                x_min = 0
            else:
                x_min = -win_width//2
        self.x_min = x_min
        self.x_max = x_min + win_width
        if y_min is None:
            if self.iy0_is_top:
                y_min = 0
            else:
                y_min = -win_width//2
        self.y_min = y_min
        self.y_max = y_min + win_height
        self._color = "black"       # Current color
        self._drawing = drawing
        self._show_marked = show_marked
        self._enable_mouse = enable_mouse
        mw = tk.Tk()
        self.title = title
        mw.title(title)
        self.mw = mw
        #mw.withdraw()

        # create the file object
        self.menu_setup()

        
        win_print_frame = tk.Frame(mw)
        win_print_frame.pack(side=tk.TOP)
        win_print_entry = tk.Entry(
                                win_print_frame, width=50)
        win_print_entry.pack(side=tk.TOP)
        self.win_print_entry = win_print_entry
        
        canvas = tk.Canvas(mw, width=self.win_width, height=self.win_height)
        canvas.pack()
        self.canvas = canvas
        self.update()        # Force display
        SlTrace.lg(f"canvas width: {canvas.winfo_width()}")
        SlTrace.lg(f"canvas height: {canvas.winfo_height()}")
        self.visible_figure = visible_figure

        """
        Turtle usage support
        Turtle is used to support cursor movement
        animation is disabled
        pen is up
        turtle is hidden
        """
        if not self.iy0_is_top:     # TBD - we should get rid of turtle
            self.turtle = tu.RawTurtle(canvas)
            #self.turtle.hideturtle()
            self.turtle_screen = self.turtle.getscreen()
            self.turtle_screen.tracer(0)
            #self.turtle.showturtle()
            self.turtle.penup()

        self._cursor_item = None    # position cursor tag
        self.escape_pressed = False # True -> interrupt/flush
        self.cells = {}         # Dictionary of cells by (ix,iy)
        self.set_cell_lims()
        self.do_talking = True      # Enable talking
        self.logging_speech = True  # Output speech to log/screen
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
        self.pos_rep_interval = pos_rep_interval
        self.pos_rep_ix_prev = None    # previous report location 
        self.pos_rep_iy_prev = None
        self.pos_rep_str_prev = None    # previous position report
        self.pos_rep_time = datetime.now()  # Time of last report
        self.pos_check_interval = pos_check_interval
        self._echo_input = True     # True -> speak input
        self._loc_list_first = None     # a,b horiz/vert move targets
        self._loc_list_second = None
        if mag_info is None:
            top_region = MagnifyDisplayRegion(
                x_min=self.win_x_min, y_min=self.win_x_min,
                x_max=self.win_x_min+self.win_width,
                y_max=self.y_min+self.win_height,
                nrows=self.grid_height,
                ncols=self.grid_width,
                
                )
            mag_info = MagnifyInfo(top_region=top_region)
        else:
            if mag_info.description:
                title = mag_info.description
                mw.title(title)
                self.title = title
                self.speak_text(f"Magnification of {title}")
        mag_info.display_window = self    # Magnification setup
        self.mag_info = mag_info
        SlTrace.lg(f"\nAudioDrawWindow() mag_info:\n{mag_info}\n")
        self.mag_selection_tag = None       # mag selection canvas tag, if one
        self.is_selected = False            # Flag as not yet selected
        self.pos_history = []       # position history (ix,iy)
        self._track_goto_cell = True    # True -> mark cells where we have gone
        self.goto_travel_list = []    # Memory of where we have gone
        self.goto_cell_list = []
        self.goto_travel_list_index = None
        self.cell_history = []          # History of all movement
        self._silent = silent       # True - override talking/beeping
        self._audio_beep = False
        self.audio_beep = AudioBeep(self, self.silence)
        self.grid_path = GridPath(self)
        self.running = True         # Set False to stop
        self.mw.focus_force()
        self.motion_level = 0   # Track possible recursive calls
        self.canvas.bind('<Motion>', self.motion)
        self.canvas.bind('<Button-1>', self.on_button_1)
        self.canvas.bind('<B1-Motion>', self.on_button_1_motion)
        self.mw.bind('<KeyPress>', self.on_key_press)
        self._multi_key_progress = False    # True - processing multiple keys
        self._multi_key_cmd = None          # Set if in progress
        self._pendown = False       # True - move marks
        self.blank_char = blank_char
        self.shift_to_edge = shift_to_edge
        self.look_dist = look_dist
        self.menu_str = menu_str
        self.do_menu_str(menu_str)
        self.key_str = key_str
        self.do_key_str(key_str)
        self.pos_check()            # Startup possition check loop
        self.update()     # Make visible

    def silence(self):
        """ Check if silent mode
        """
        return self._silent
    
    def do_menu_str(self, menu_str=None):
        """ Execute initial navigate string, if any
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
            if cmd_type == 'n':
                for c in cmd_letters:
                    self.nav_direct_call(c)
            elif cmd_type == 'd':
                for c in cmd_letters:
                    self.draw_direct_call(c)

    def do_key_str(self, key_str=None):
        """ Execute initial key string, if any
        :nav_str: string default: use self.nav_str
        """
        if key_str is None:
            key_str = self.key_str
        if key_str is None or key_str == "":
            return
         
        syms = key_str.split(";")
        for sym in syms:
            self.key_press(sym)    
            
                
    def speak_text(self, msg, dup_stdout=True,
                   speech_type='REPORT'):
        """ Speak text, if possible else write to stdout
        :msg: text message
        :dup_stdout: duplicate to stdout default: True
        :speech_type: type of speech default: "report"
            REPORT - standard reporting
            CMD    - command
            ECHO
        """
        self.speech_maker.speak_text(msg=msg, msg_type=speech_type, dup_stdout=dup_stdout)

    def speak_text_stop(self):
        """ Stop ongoing speach, flushing queue
        """
        self.speech_maker.speak_text_stop()
        
    def motion(self, event):
        """ Mouse motion in  window
        """
        if not self._enable_mouse:
            return      # Ignore mouse motion 
        
        if self.motion_level > 1:
            SlTrace.lg("Motion Recursion: motion_level({self.motion_Level} > 1")
            self.motion_level = 0
            return
        
        x,y = event.x, event.y
        self.win_x,self.win_y = x,y
        SlTrace.lg(f"motion x={x} y={y}", "aud_motion")
        quiet = self._drawing   # move quietly if drawing
        self.move_to(x,y, quiet=quiet)
        #self.pos_x = x 
        #self.pos_y = y
        #self.pos_check()
        self.motion_level -= 1
        return              # Processed via pos_check()

    def on_button_1(self, event):
        """ Mouse button in window
        """
        x,y = event.x, event.y
        if self.iy0_is_top:
            x,y = x + self.x_min, y + self.y_min
        self.win_x,self.win_y = x,y
        SlTrace.lg(f"motion x={x} y={y}", "aud_motion")
        self.move_to(x,y, quiet=True)
        cell = self.get_cell_at()
        if SlTrace.trace("mouse_cell"):
            SlTrace.lg(f"x:{x},y:{y} pos_xy:{self.pos_x}, {self.pos_y}"
                       f" win x,y:{self.get_point_win()}"
                       f" tur x,y:{self.get_point_tur()}"
                       f" ixy:{self.get_ixy_at()}  cell: {cell}")
        if self._drawing:
            if cell is None:
                new_cell = self.create_cell()
                self.display_cell(new_cell)
        else:
            if cell is not None:
                self.set_visible_cell(cell)
            self.pos_check()
        self.update()

    def on_button_1_motion(self, event):
        """ Motion will button down is
        treated as mouse click at point
        """
        if self._enable_mouse:
            self.on_button_1(event)
        
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
            return                  # Ignore ALT
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
        elif keyslow == "e":            # Erase current position with current color
            self.key_mark(False)
        elif keyslow == "g":
            self.key_goto()             # Goto closest figure
        elif keyslow == "h":
            self.key_help()             # Help message
        elif keyslow == "j":
            self.key_magnify(self.MAG_PARENT)         # Jump to magnify parent
        elif keyslow == "k":
            self.key_magnify(self.MAG_CHILD)          # jump to magnify child
        elif keyslow == "c":            # Change color
            self.key_color_change()
        elif keyslow == "u":            # raise pen - for subsequent not visible
            self.key_pendown(False)
        elif keyslow == "d":
            self.key_pendown()          # lower pen - for subsequent visible
        elif keyslow == "m":            # Mark current position with current color
            self.key_mark()
        elif keyslow == "p":
            self.key_report_pos()       # Report position
        elif keyslow == "r":
            self.key_report_pos_horz()       # Report horizontal position
        elif keyslow == "t":
            self.key_report_pos_vert()       # Report vertical position
        elif keyslow == "z": 
            self.key_clear_display()     # Clear display
        elif keyslow == "w":
            self.key_write_display()     # Write(print) out figure
        elif keyslow == "win_l":
            pass                        # Ignore Win key
        else:
            self.key_unrecognized(keysym)

    """
    keyboard commands
    """
    def key_echo(self,keysym):
        """ Echo key, if appropriate
        :keysym; key symbol
        """
        #self.key_flush(keysym=keysym)
        if self._echo_input:
            self.speech_maker.speak_text(keysym, msg_type='ECHO')

    def key_flush(self, keysym):
        """ Do appropriate flushing
        :keysym: key symbol
        """
        self.escape_pressed = True  # Let folks in prog know
        self.flush_rep_queue()
        self.speak_text_stop() 
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
        self.goto_cell_list.append((ix,iy))
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
                self._color = color
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
        for cell in list(self.cells.values()):
            self.erase_cell(cell)
        del self.cells
        self.cells = {}
        self.pos_history = []
        self.draw_cells(cells=self.cells)
        
    def mark_cell(self, cell,
                  mtype=BrailleCell.MARK_SELECTED):
        """ Mark cell for viewing of history
        :cell: Cell(BrailleCell) or (ix,iy) of cell
        :mtype: Mark type default: MARK_SELECTED
        """
        if isinstance(cell, BrailleCell):
            ixy = (cell.ix,cell.iy) 
        else:
            ixy = cell
        if ixy in self.cells:
            cell = self.cells[ixy]
            cell.mtype = mtype
            self.show_cell(ixy=ixy)
            
    def show_cell(self, ixy=None):
        if ixy in self.cells:
            cell = self.cells[ixy]
            self.set_visible_cell(cell)
            canvas = self.canvas
            for item_id in cell.canv_items:
                item_type = canvas.type(item_id)
                if item_type == "rectangle":
                    canvas.itemconfigure(item_id, fill='dark gray')
                else:
                    canvas.itemconfigure(item_id, fill='')            

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


    def key_mark(self, val=True):
        """ Mark/Erase current location with current color
            if empty create cell, else change current cell
        :val: True - mark location default: True
                False - erase location
        """
        if not self._drawing:
            self.announce_can_not_do("Not drawing", val)
            
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
                pass    # beep ?
            else:
                self.erase_cell(cell)
                del self.cells[(cell.ix,cell.iy)]
                
        
    def key_direction(self, keyslow):
        """ Process key direction command
        :keyslow: key 123 4 6 789
        """
        inc_x, inc_y = self.digit_dir[keyslow]
        self.move_cursor(x_inc=inc_x, y_inc=inc_y)
        
        
        
    def key_goto(self):
        """ Go to closest figure
            go to figure not in one already
            else go one step within current figure, toward
            longest inside path
        """
        dist, dist_x, dist_y, cell = self.distance_from_drawing()
        if dist is None:
            return              # Nowhere
        
        if dist > 0:
            self.goto_cell(ix=cell.ix, iy=cell.iy)
            self.goto_cell_list = []
            start_cell = (cell.ix,cell.iy)
            self.goto_cell_list.append(start_cell)
            gfg = GridFillGobble(self.cells,
                                         start_cell)
            self.goto_travel_list = gfg.find_region(start_cell)
            self.goto_travel_list_index = 0
        else:
            if not self.goto_travel_list:
                return  # No travel list
            
            goto_idx = self.goto_travel_list_index + 1
            goto_idx %= len(self.goto_travel_list)
            self.goto_travel_list_index = goto_idx
            new_cell= self.goto_travel_list[goto_idx]
            self.goto_cell(ix=new_cell[0], iy=new_cell[1])
        
    def trav_len(self, ix, iy, dir_x, dir_y, require_cell=True):
        """ Find the travel length
        This is the number of steps from cell(ix,iy) in 
        direction (dir_x,dir_y) while still in self.cells[]
        traversal is stopped at traversed cells - in
        self.goto_cell_list
        :ix: cell x-index
        :iy: cell y_index
        :dir_x: x change each step
        :dir_y: y change each step
        :require_cell: Require cell in traversal default: True - required
        :returns: steps_forward, steps_backward, -1,-1
                 if cell, itself is not in figure(self.cells)
        """
        if require_cell and (ix,iy) not in self.cells:
            return -1,-1       # Not in figure
        
        if dir_x == 0 and dir_y == 0:
            return 0,0
        
        tlen_forward = 0
        ix_f = ix
        iy_f = iy
        while True:
            ix_f += dir_x
            iy_f += dir_y
            if (ix_f,iy_f) not in self.cells:
                break
            if (ix_f,iy_f) in self.goto_cell_list:
                break
            tlen_forward += 1   # traversal extended

        # Get backend of line
        tlen_backward = 0
        ix_b = ix
        iy_b = iy
        
        while True:
            ix_b -= dir_x
            iy_b -= dir_y
            if (ix_b,iy_b) not in self.cells:
                break
            if (ix_b,iy_b) in self.goto_cell_list:
                break
            tlen_backward += 1   # traversal extended
        return tlen_forward,tlen_backward

    def key_help(self):
        """ Help - list keyboard action
        """
        help_str = """
        h - say this help message
        Up - Move up one row
        Down - Move down one row
        Left - Move left one column
        Right - Move right one column
        DIGIT - direction (from center):
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
        t - Vertical position stuff to Top, to bottom
        u - penup - move with out marking 
        w - write out braille
        z - clear board
        Escape - flush pending report output
        """
        self.speak_text(help_str)
        
    def key_up(self):
        y_inc = -1 if self.iy0_is_top else 1
        self.move_cursor(y_inc=y_inc)
    
    def key_down(self):
        y_inc = 1 if self.iy0_is_top else -1
        self.move_cursor(y_inc=y_inc)
        
    def key_left(self):
        self.move_cursor(x_inc=-1)
        
    def key_right(self):
        self.move_cursor(x_inc=1)

    def key_exit(self):
        self.speak_text("Quitting Program")
        self.update()     # Process any pending events
        self.mw.destroy()
        self.mw.quit()
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
        if self.mag_info is None:
            self.speak_text("Magnification is not enabled")
            return 
        
        if option == self.MAG_PARENT:
            parent = self.mag_info.parent_info
            if parent is None:
                self.speak_text("No magnification parent")
                return 
            display = parent.display_window
        elif option == self.MAG_CHILD:
            children = self.mag_info.child_infos
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
        root = self.mw
        root.focus_force()
        root.lift()
        root.attributes('-topmost', 1)
        
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
                  default: first
        """
        if self._loc_list_first is None:
            return      # No current target
        
        if end_pos == "first":
            self.move_to_ixy(*self._loc_list_first)
        elif end_pos == "second":
            self.move_to_ixy(*self._loc_list_second)
        else:
            self.audio_beep.announce_can_not_do()          


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
        dir_up = (0,-1) if self.iy0_is_top else (0,1)
        dir_down = (0,1) if self.iy0_is_top else (0,-1)
        pos_ixy = self.get_ixy_at()
        msg_top, loc_top_end = self.loc_list_target(pos_ixy,
                                         name="above", dir=dir_up)
        msg_bottom, loc_bottom_end = self.loc_list_target(pos_ixy,
                                         name="below", dir=dir_down)
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
        self._silent = val
                                            
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
                        y_str = f"down {-y_dist}"
                    elif y_dist > 0:
                        y_str = f"up {y_dist}"
                    rep_str = x_str
                    if rep_str != "":
                        rep_str += " "
                    rep_str += y_str
            elif rep_type == "draw":
                cell_ixiy = rep_args[0]
                cell = self.cells[cell_ixiy]
                color = cell._color
                rep_str = color
            elif rep_type == "msg":
                rep_str = rep_args[0]
    
            ix,iy = self.get_ixy_at()
            SlTrace.lg(f"from get_ixy_at(): ix:{ix} iy:{iy}",
                        "pos_tracking")
            if self._audio_beep and not with_voice:
                self.audio_beep.announce_pcell((ix,iy), dly=0)
                self.update()
                if self.grid_path is not None:
                    pcells = self.grid_path.get_next_positions(max_len=self.look_dist)
                    self.update()
                    self.audio_beep.announce_next_pcells(pc_ixys=pcells)
            else:
                if self.rept_at_loc or with_voice:
                    if self.iy0_is_top:
                        rep_str += f" at row {iy+1} column {ix+1}"
                    else:
                        rep_str += f" at row {self.grid_height-iy} column{ix+1}"
                if (force_output
                        or ix != self.pos_rep_ix_prev    # Avoid repeats
                        or iy != self.pos_rep_iy_prev):            
                    self.win_print(rep_str, end= "\n")
                    self.speak_text(rep_str)
                    self.pos_rep_time = datetime.now()  # Time of last report
                    self.pos_rep_ix_prev = ix
                    self.pos_rep_iy_prev = iy
                    self.pos_rep_str_prev = rep_str
                
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
        self.win_print_entry.delete(0, tk.END)
        self.win_print_entry.insert(0, lstr)    
        #time.sleep(.2)
             
    def draw_cells(self, cells=None, show_points=False):
        """ Display braille cells on canvas
        :cells: list or dictionary cells to draw
        :show_points: instead of braille, show sample points
        """
        SlTrace.lg("draw_cells")
        SlTrace.lg(f"win_x_min:{self.win_x_min} win_y_min: {self.win_y_min}")
        if cells is None:
            cells = self.cells
        else:
            if not isinstance(cells, dict):
                cs = {}
                for cell in cells:
                    cs[(cell.ix,cell.iy)] = cell
                cells = cs
                self.cells = cells      # Copy
        min_x, max_y, max_x,min_y = self.bounding_box()
        if min_x is not None:            
            SlTrace.lg(f"Lower left: min_x:{min_x} min_y:{min_y}")
            SlTrace.lg(f"Upper Right: max_x:{max_x} max_y:{max_y}")
        SlTrace.lg(f"{len(cells)} cells")
        for cell in cells.values():
            self.display_cell(cell)
            cell.mtype = cell.MARK_UNMARKED
        self.update()
        if min_x is not None:
            if not self.iy0_is_top:            
                self.set_cursor_pos_tu(x=min_x, y=min_y)
            x,y = self.get_point_win((min_x,min_y))
            self.pos_check(x=x,  y=y)
        self.grid_path = GridPath(self)
        self.pos_history = []       # Clear history
        self.update()
        #self.turtle.penup()
                    
    def print_braille(self, title=None, shift_to_edge=None):
        """ Output braille display
        :title: title default: self.title
        :shift_to_edge: shift figure towards edge to ease finding figure
                        default: self.shift_to_edge
        """
        if title is None:
            title = self.title
        if title is not None:
            print(title)
        if shift_to_edge is None:
            shift_to_edge = self.shift_to_edge
        if shift_to_edge:
            self.find_edges()
            left_edge = self.left_edge
            right_edge = self.right_edge
            top_edge = self.top_edge
            bottom_edge = self.bottom_edge
        else:
            left_edge = 0
            top_edge = self.grid_height-1

        braille_text = ""
        for iy in range(top_edge, bottom_edge):
            line = ""
            for ix in range(left_edge, right_edge):
                cell_ixy = (ix,iy)
                if cell_ixy in self.cells:
                    cell = self.cells[cell_ixy]
                    color = cell.color_string()
                    line += color[0]
                else:
                    line += " "
            line = line.rstrip()
            if self.blank_char != " ":
                line = line.replace(" ", self.blank_char)
            ###print(f"{iy:2}", end=":")
            braille_text += line + "\n"
        SlTrace.lg(braille_text)
        self.mw.clipboard_clear()
        if title is not None:
            self.mw.clipboard_append(f"\n{title}\n")
        self.mw.clipboard_append(braille_text)

    def print_cells(self, title=None):
        """ Display current braille in a window
        """
        if title is not None:
            print(title)
        for ix in range(self.grid_width):
            for iy in range(self.grid_height):
                cell_ixy = (ix,iy)
                if cell_ixy in self.cells:
                    cell = self.cells[cell_ixy]
                    SlTrace.lg(f"ix:{ix} iy:{iy} {cell_ixy}"
                               f" {cell._color}"
                          f" rect: {self.get_cell_rect_tur(ix,iy)}"
                          f"  win rect: {self.get_cell_rect_win(ix,iy)}")
        SlTrace.lg("")

    def find_edges(self):
        """Find  top, left, bottom, right non-blank edges
        so we can shift picture to left,top for easier
        recognition
        """
        left_edge,top_edge, right_edge,bottom_edge = self.bounding_box_ci()
        if bottom_edge is None:
            bottom_edge = self.grid_height-1
                    
        if left_edge > 0:           # Give some space
            left_edge -= 1
        if left_edge > 0:
            left_edge -= 1
        self.left_edge = left_edge
        
        if self.iy0_is_top:
            if top_edge > 0:           # Give some space
                top_edge -= 1
            if bottom_edge  < self.grid_height-1:
                bottom_edge += 1        
        else:
            if top_edge < self.grid_height-1:           # Give some space
                top_edge += 1
            if bottom_edge  > 0:
                top_edge -= 1
        self.top_edge = top_edge
        self.bottom_edge = bottom_edge
        
        self.left_edge = left_edge
        self.right_edge = right_edge
         
        return left_edge, top_edge, right_edge, bottom_edge
        
    def set_cursor_pos_win(self, x=0, y=0, quiet=False):
        """ Set mouse cursor position in win(canvas) coordinates
        :x: x-coordinate (win(canvas)) unless self.iy0_is_top
        :y: y-coordinate (win(canvas)) unless self.iy0_is_top
        :quiet: Don't announce legal moves
                default:False
        """
        if not self.iy0_is_top:
            self.cursor_update()
            return

        """ Set mouse cursor position in turtle coordinates
        :x: x-coordinate (canvas win)
        :y: y-coordinate (canvas win)
        :quiet: Don't announce legal moves
                default: False
        """
        if not self.running:
            return
        
        self.win_x,self.win_y = x,y # All we do is set coordinate memory
        loc_ixiy = self.get_ixy_at()
        self.pos_history.append(loc_ixiy)   # location history
        SlTrace.lg(f"pos_history:{loc_ixiy}", "pos_tracking")
        cell_ixiy = self.get_cell_at()
        if cell_ixiy is not None:
            self.cell_history.append(cell_ixiy)
            if not self._drawing:   # If we're not drawing
                self.mark_cell(cell_ixiy)   # Mark cell if one
        self.cursor_update()

        ###self.turtle_screen.update()
        if not self.mw.winfo_exists():
            return 
        
        self.update()
        if not quiet:
            self.pos_check(force_output=True)



    def set_cursor_pos_tu(self, x=0, y=0, quiet=False):
        """ Set mouse cursor position in turtle coordinates
        :x: x-coordinate (turtle)
        :y: y-coordinate (turtle)
        :quiet: Don't announce legal moves
                default: False
        """
        if not self.running:
            return
        
        self.canvas.bind('<Motion>', None)  # Disable motion events
        self.turtle.goto(x=x, y=y)
        self.turtle.showturtle()
        win_x,win_y = self.get_point_win((x,y))
        self.pos_x,self.pos_y = win_x,win_y
        loc_ixiy = self.get_ixy_at()
        self.pos_history.append(loc_ixiy)   # location history
        SlTrace.lg(f"pos_history:{loc_ixiy}", "pos_tracking")
        cell_ixiy = self.get_cell_at()
        if cell_ixiy is not None:
            self.cell_history.append(cell_ixiy)
            if not self._drawing:   # If we're not drawing
                self.mark_cell(cell_ixiy)   # Mark cell if one
        self.cursor_update()

        ###self.turtle_screen.update()
        if not self.mw.winfo_exists():
            return 
        
        self.update()
        if not quiet:
            self.pos_check(force_output=True)
        self.canvas.bind('<Motion>', self.motion)   # Reenable

    def move_cursor(self, x_inc=0, y_inc=0):
        """ Move cursor by cell increments to center of
        cell to maximise chance of seeing cell figures
        :x_inc: x change default: no movement
        :y_inc: y change default: no movement
        """
        if self.iy0_is_top:
            self.move_cursor_win(x_inc=x_inc, y_inc=y_inc)
            return
        
        tu_x,tu_y = self.get_point_tur((self.pos_x, self.pos_y))
        ix,iy = self.get_ixy_at((tu_x,tu_y))
        ix += x_inc
        iy += y_inc
        win_xc,win_yc = self.get_cell_center_win(ix,iy)
        SlTrace.lg(f"move_cursor: ix={ix}, y={iy}", "move_cursor")
        self.move_to(win_xc,win_yc)
        if self._pendown:
            self.set_cell()

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
            SlTrace.lg(f"{self.win_x},{self.win_y} pos_xy:{self.pos_x}, {self.pos_y}"
                       f" win x,y:{self.get_point_win()}"
                       f" tur x,y:{self.get_point_tur()}"
                       f" ixy:{self.get_ixy_at()}  cell: {cell}")
        

    def move_to(self, x,y, quiet=False):
        """ Move to window loc
        Stop at edges, with message
        :x: turtle x-coordinate iy0_is_top: win x-coordinate
        :y: turtle y-coordinate iy0_is_top: win y-coordinate
        :quiet: Don't announce legal move
                default:False
        """
        if self.iy0_is_top:
            self.set_cursor_pos_win(x=x, y=y, quiet=quiet)
            return
        
        margin = 10
        top_margin = 20     # HACK to determine top before low level check
        bottom_margin = 20   # HACK to determine before low level check
        tu_x, tu_y = self.get_point_tur((x,y))
        if tu_x <= self.x_min + margin:
            self.pos_report("msg", "At left edge", force_output=True)
            x,_ = self.get_point_win((self.x_min + margin + 1, tu_y))
            
        elif tu_x >= self.x_max - margin:
            self.pos_report("msg", "At right edge", force_output=True)
            x,_ = self.get_point_win((self.x_max - margin - 1, tu_y))                               
        if tu_y <= self.y_min + bottom_margin:
            self.pos_report("msg", "At bottom edge", force_output=True)
            _,y = self.get_point_win((tu_x, self.y_min + bottom_margin + 1))
        elif tu_y >= self.y_max - top_margin:
            self.pos_report("msg", "At top edge", force_output=True)
            _,y = self.get_point_win((tu_x, self.y_max - top_margin - 1))
                                           
        self.set_cursor_pos_win(x=x, y=y, quiet=quiet)

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

    def is_inbounds_ixy(self, *ixy):
        """ Check if ixy pair is in bounds
        :ixy: if tuple ix,iy pair default: current location
              else ix,iy indexes
            ix: cell x index default current location
            iy: cell y index default current location
        :returns: True iff in bounds else False
        """
        ix_cur,iy_cur = self.get_ixy_at()
        if len(ixy) ==  0:
            ix,iy = ix_cur,iy_cur
        elif len(ixy) == 1 and isinstance(ixy[0], tuple):
            ix,iy = ixy[0]
        elif len(ixy) == 2:
            ix,iy = ixy
        else:
            raise Exception(f"bad is_inbounds_ixy args: {ixy}")
        if ix is None:
            ix = ix_cur
        if iy is None:
            iy = iy_cur
        if ix < 0 or ix >= len(self.cell_xs):
            return False
         
        if iy < 0 or iy >= len(self.cell_ys):
            return False
        
        return True 
                       
    def set_cell_lims(self):
        """ create cell boundary values bottom through top
         so:
             cell_xs[0] == left edge
             cell_xs[grid_width] == right edge
             if iy0_is_top:
                 cell_ys[0] == top edge
                 cell_ys[grid_height] == bottom edge
             else:  Default
                 cell_ys[0] == bottom edge
                 cell_ys[grid_height] == top edge
             
        """
         
        self.cell_xs = []
        self.cell_ys = []

        for i in range(self.grid_width+1):
            x = int(self.x_min + i*self.win_width/self.grid_width)
            self.cell_xs.append(x)
        if self.iy0_is_top:
            for i in reversed(range(self.grid_height+1)):
                y = int(self.y_min + i*self.win_height/self.grid_height)
                self.cell_ys.append(y)
        else:
            for i in range(self.grid_height+1):
                y = int(self.y_min + i*self.win_height/self.grid_height)
                self.cell_ys.append(y)
            
    def get_ix_min(self):
        """ get minimum ix on grid
        :returns: min ix
        """
        return 0

    def get_ix_max(self):
        """ get maximum ix on grid
        :returns: min ix
        """
        return self.grid_width-1

    def get_iy_min(self):
        """ get minimum iy on grid
        :returns: min iy
        """
        return 0

    def get_iy_max(self):
        """ get maximum ix on grid
        :returns: min ix
        """
        return self.grid_height-1
    
        
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
        if x is None:
            x = self.win_x
        if y is None:
            y = self.win_y
        if x is None:
            return  None,None,None,None # Nothing to report
        
                        # Check/Report on distance from figure
        if (self.cells is None
                 or len(self.cells) == 0):
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
        for cell_ixy in self.cells:
            cell_ix, cell_iy = cell_ixy
            dist = sqrt((cell_ix-pt_ix)**2 + (cell_iy-pt_iy)**2)
            if min_dist is None or dist < min_dist:
                min_dist = dist
                min_dist_x = cell_ix - pt_ix
                min_dist_y = cell_iy - pt_iy
                cell_closest = self.cells[cell_ixy]    # Closest so far
        if min_dist <= 0:
            min_dist = .001     # Saving 0 for in display element
        return min_dist, min_dist_x, min_dist_y, cell_closest

        
        
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
        if self.iy0_is_top:
            return self.distance_from_drawing_win(x=None, y=None)
        
        if x is None:
            x = self.pos_x
        if y is None:
            y = self.pos_y
        if x is None:
            return  None,None,None,None # Nothing to report
        
                        # Check/Report on distance from figure
        if (self.cells is None
                 or len(self.cells) == 0):
            return 999,999,999, None   # Far....p

        tu_x, tu_y = self.get_point_tur((x,y))
        SlTrace.lg(f"distance_from_drawing: x={x} y={y}", "aud_motion")
        
        pt_ixiy = self.get_ixy_at((tu_x,tu_y))
        cell_closest = None         # Set if found
        if pt_ixiy in self.cells:
            cell_closest = self.cells[pt_ixiy]      # We're there
            return 0,0,0, cell_closest        # On drawing
        
        min_dist = None
        min_dist_x = 0      # x,y offset at min dist
        min_dist_y = 0
        pt_ix, pt_iy = pt_ixiy 
        for cell_ixy in self.cells:
            cell_ix, cell_iy = cell_ixy
            dist = sqrt((cell_ix-pt_ix)**2 + (cell_iy-pt_iy)**2)
            if min_dist is None or dist < min_dist:
                min_dist = dist
                min_dist_x = cell_ix - pt_ix
                min_dist_y = cell_iy - pt_iy
                cell_closest = self.cells[cell_ixy]    # Closest so far
        if min_dist <= 0:
            min_dist = .001     # Saving 0 for in display element
        return min_dist, min_dist_x, min_dist_y, cell_closest

    def bounding_box(self):
        """ turtle coordinates which bound displayed figure
        :returns: min_x, max_y, max_x, min_y  (upper left) (lower right)
                    None,None,None,None if no figure
        """
        min_ix, max_iy, max_ix, min_iy = self.bounding_box_ci()
        if min_ix is None:
            return None,None,None,None      # No figure
        
        min_x, max_y, _, _ = self.get_cell_rect_tur(min_ix,max_iy)
        _, _, max_x, min_y = self.get_cell_rect_tur(max_ix,min_iy)
        return min_x,max_y, max_x, min_y
    
    def bounding_box_ci(self, cells=None):
        """ cell indexes which bound the list of cells
        :cells: list of cells, (with cell.ix,cell.iy) or (ix,iy) tuples
                default: list of all cells in figure
        :returns: 
                    None,None,None,None if no figure
                    upper left ix,iy  lower right ix,iy
                    self.iy0_is_top:
                        ix_min, iy_min, ix_max, iy_max  (upper left) (lower right)
                    else:
                        ix_min, iy_max, ix_max, iy_min  (upper left) (lower right)
        """
        if cells is None:
            if not hasattr(self, "cells"):
                return None,None,None,None         # Not yet setup
            cells = list(self.cells.keys())
        
        ix_min, iy_max, ix_max,iy_min = None,None,None,None
        for cell in cells:
            cell_ixy = cell if isinstance(cell, tuple) else (cell.ix,cell.iy)
            cell_ix, cell_iy = cell_ixy
            if ix_min is None or cell_ix < ix_min:
                ix_min = cell_ix
            if ix_max is None or cell_ix > ix_max:
                ix_max = cell_ix
            if iy_min is None or cell_iy < iy_min:
                iy_min = cell_iy
            if iy_max is None or cell_iy > iy_max:
                iy_max = cell_iy

        if ix_min is None:
            ix_min = 0
        if ix_max is None:
            ix_max = self.grid_width-1
        if self.iy0_is_top:                
            if iy_min is None:
                iy_min = 0
            if iy_max is None:
                ix_max = self.grid_height-1
            return ix_min,iy_min, ix_max,iy_max
        else:
            if iy_min is None:
                iy_min = self.grid_width-1
            if iy_max is None:
                ix_max = 0
            return ix_min,iy_max, ix_max,iy_min
            


    def erase_cell(self, cell):
        """ Erase cell
        :cell: BrailleCell
        """
        if cell is None:
            return
        
        # Remove current items, if any
        if cell.canv_items:
            for item_id in cell.canv_items:
                self.canvas.delete(item_id)
        cell.canv_items = []

    def erase_pos_history(self):
        """ Remove history, undo history marking
        """
        canvas = self.canvas
        for cell_ixy in self.pos_history:
            if not cell_ixy in self.cells:
                continue
            cell = self.cells[cell_ixy]
            self.display_cell(cell)
            '''
            for item_id in cell.canv_items:
                item_type = canvas.type(item_id)
                if item_type == "rectangle":
                    canvas.itemconfigure(item_id, fill='')
                    canvas.tag_lower(item_id)
            '''
        self.pos_history = []
        canvas = self.canvas
        if self.mag_selection_tag is not None:
            canvas.itemconfig(self.mag_selection_tag, outline="red")
        self.is_selected = False         # Flag as unselected
            
        self.update()
                
    def display_reposition_hack(self, cx1,cx2,cy1,cy2, force=False):
        """ ###TFD HACK to reposition cell dispaly
            move x1,x2,y1,y2
        """
        if not self.iy0_is_top or force:     # if not using CanvasGrid and not force
            cx1 -= 400
            cx2 -= 400
            cy1 -= 400
            cy2 -= 400

        return cx1,cx2,cy1,cy2
    
    def display_cell(self, cell, show_points=False):
        """ Display cell
        :cell: BrailleCell
        :show_points: show points instead of braille
                default: False --> show braille dots
        """
        self.erase_cell(cell)
        canvas = self.canvas
        ix = cell.ix
        iy = cell.iy
        
        if self.iy0_is_top:
            cx1,cy1,cx2,cy2 = self.get_win_ullr_at_ixy((ix,iy))
        else: 
            cx1,cy1,cx2,cy2 = self.get_cell_rect_win(ix=ix, iy=iy)
            cx1,cy1,cx2,cy2 = self.display_reposition_hack(cx1,cy1,cx2,cy2)
        SlTrace.lg(f"{ix},{iy}: {cell} :{cx1},{cy1}, {cx2},{cy2} ", "display_cell")
        canv_item = canvas.create_rectangle(cx1,cy1,cx2,cy2,
                                 outline="light gray")
        cell.canv_items.append(canv_item)
        self.update()
        color = self.color_str(cell._color)
        if show_points:
            dot_size = 1            # Display cell points
            dot_radius = dot_size//2
            if dot_radius < 1:
                dot_radius = 1
                dot_size = 2
            for pt in cell.points:
                dx,dy = self.get_point_win(pt)
                x0 = dx-dot_radius
                y0 = dy+dot_size 
                x1 = dx+dot_radius 
                y1 = dy
                canv_item = canvas.create_oval(x0,y0,x1,y1,
                                                fill=color)
                cell.canv_items.append(canv_item)
                SlTrace.lg(f"canvas.create_oval({x0},{y0},{x1},{y1}, fill={color})", "aud_create")
            self.update()    # So we can see it now 
            return
            
        dots = cell.dots
        grid_width = cx2-cx1
        grid_height = cy1-cy2       # y increases down
        # Fractional offsets from lower left corner
        # of cell rectangle
        ll_x = cx1      # Lower left corner
        ll_y = cy2
        ox1 = ox2 = ox3 = .3 
        ox4 = ox5 = ox6 = .7
        oy1 = oy4 = .15
        oy2 = oy5 = .45
        oy3 = oy6 = .73
        dot_size = .25*grid_width   # dot size fraction
        dot_radius = dot_size//2
        dot_offset = {1: (ox1,oy1), 4: (ox4,oy4),
                      2: (ox2,oy2), 5: (ox5,oy5),
                      3: (ox3,oy3), 6: (ox6,oy6),
                      }
        for dot in dots:
            offsets = dot_offset[dot]
            off_x_f, off_y_f = offsets
            dx = ll_x + off_x_f*grid_width
            dy = ll_y + off_y_f*grid_height
            x0 = dx-dot_radius
            y0 = dy+dot_size 
            x1 = dx+dot_radius 
            y1 = dy
            canv_item = canvas.create_oval(x0,y0,x1,y1,
                                            fill=color)
            cell.canv_items.append(canv_item) 
            SlTrace.lg(f"canvas.create_oval({x0},{y0},{x1},{y1}, fill={color})", "aud_create")
        self.update()
        pass
                
    def get_cell_center_win(self, ix, iy):
        """ Get cell's window rectangle x, y  upper left, x,  y lower right
        :ix: cell x index
        :iy: cell's  y index
        :returns: window(0-max): (xc,yc) where
            xc,yc are x,y coordinates of cell's center
        """
        x1,y1, x2,y2 = self.get_cell_rect_win(ix,iy)
        return (x1+x2)/2, (y1+y2)/2 
                
    def get_cell_rect_win(self, ix, iy):
        """ Get cell's window rectangle x, y  upper left, x,  y lower right
        :ix: cell x index
        :iy: cell's  y index
        :returns: window(0-max): (x1,y1,x2,y2) where
            x1,y1 are lower left coordinates
            x2,y2 are upper right coordinates
        """
        if self.iy0_is_top:
            win_x1,win_y1,win_x2,win_y2 = self.get_win_ullr_at_ixy((ix,iy))
            return (win_x1,win_y1,win_x2,win_y2)
        else:
            tu_x1,tu_y1,tu_x2,tu_y2 = self.get_cell_rect_tur(ix,iy)
            win_x1 = tu_x1 + self.win_width//2
            win_y1 = self.win_height//2 - tu_y1
            win_x2 = tu_x2 + self.win_width//2
            win_y2 = self.win_height//2 - tu_y2
            return (win_x1,win_y1,win_x2,win_y2)
        
                    
        
    def get_cell_rect_tur(self, ix, iy):
        """ Get cell's turtle rectangle x, y  upper left, x,  y lower right
        :ix: cell x index
        :iy: cell's  y index
        :returns: (min_x,max_y, max_x,min_y)
        """
        if ix is None or ix < 0:
            SlTrace.lg(f"ix:{ix} < 0")
            ix = 0
        max_ix = len(self.cell_xs)-1
        if ix+1 > max_ix:
            SlTrace.lg(f"ix:{ix+1} >= {len(self.cell_xs)}")
            ix = max_ix-1
        if iy is None or iy < 0:
            SlTrace.lg(f"iy:{iy} < 0", "aud_move")
            iy = 0
        max_iy = len(self.cell_ys)-1
        if iy+1 > max_iy:
            SlTrace.lg(f"iy:{iy+1} >= {len(self.cell_ys)}")
            iy = max_iy-1
        x1 = self.cell_xs[ix]
        x2 = self.cell_xs[ix+1]
        if self.iy0_is_top:
            y1 = self.cell_ys[iy+1]
            y2 = self.cell_ys[iy]
        else:
            y1 = self.cell_ys[iy]
            #SlTrace.lg(f"get_cell_rect_tur:iy={iy} {len(self.cell_ys)}")
            y2 = self.cell_ys[iy+1]
            
        return (x1,y1,x2,y2)
        
        
    def get_ixy_at(self, pt=None):
        """ Get cell(indexes) in which point resides
        If on an edge returns lower cell
        If on a corner returns lowest cell
        :pt: x,y pair location
                    iy0_is_top:
                        in win coordinates
                    else:
                        in turtle coordinates
                default: current location
        :returns: ix,iy cell pair
                if out of bounds limit to min/max of ix,iy
        """
        if self.iy0_is_top:
            if pt is None:
                pt = (self.win_x, self.win_y)
            x,y = pt
            ix = int((x-self.win_x_min)/self.win_width*self.grid_width)
            iy = int((y-self.win_y_min)/self.win_height*self.grid_height)
            ix = int((x)/self.win_width*self.grid_width)        # TFD
            iy = int((y)/self.win_height*self.grid_height)      # TFD
            return (ix,iy)
        
        if pt is None:
            pt = self.get_point_tur()
        tu_x,tu_y = pt
        ix = int((tu_x-self.x_min)/self.win_width*self.grid_width)
        if self.iy0_is_top:
            iy = int((self.y_max-tu_y)/self.win_height*self.grid_height)
        else:
            iy = int((tu_y-self.y_min)/self.win_height*self.grid_height)
            
        if ix < self.get_ix_min():
            ix = self.get_ix_min()
        if ix > self.get_ix_max():
            ix = self.get_ix_max()
        if iy < self.get_iy_min():
            iy = self.get_iy_min()
        if iy > self.get_iy_max():
            iy = self.get_iy_max()
            
        return (ix,iy)

    def get_cell_at(self, pt=None):
        """ Get cell at location, if one
        :pt: x,y pair location in turtle coordinates
                default: current location
        :returns: cell if at, else None
        """
        cell_ixy = self.get_ixy_at(pt)
        if cell_ixy is None:
            return None 
        
        if cell_ixy in self.cells:
            return self.cells[cell_ixy]
        
        return None

    def get_win_ullr_at_ixy(self, ixy):
        """ Get window rectangle for cell at ixy
        :ixy: cell index tupple (ix,iy)
        """
        ix,iy = ixy
        if self.iy0_is_top:
            x_left = int(ix*(self.win_width/self.grid_width))
            x_right = int((ix+1)*(self.win_width/self.grid_width))
            y_top = int(iy*(self.win_height/self.grid_height))
            y_bottom = int((iy+1)*(self.win_height/self.grid_height))
            return (x_left,y_top, x_right,y_bottom)
        
        x_left = int(ix*(self.win_width/self.grid_width) + self.win_x_min)
        x_right = int((ix+1)*(self.win_width/self.grid_width) + self.win_x_min)
        y_top = int((iy*(self.win_height/self.grid_height) + self.win_y_min))
        y_bottom = int((iy+1)*(self.win_height/self.grid_height) + self.win_y_min)
        return (x_left,y_top, x_right,y_bottom)
        
        
    def get_cell_at_ixy(self, cell_ixy):
        """ Get cell at (ix,iy), if one
        :cell_ixy: (ix,iy)
        :returns: BrailleCell if one, else None
        """
        if cell_ixy in self.cells:
            return self.cells[cell_ixy]
        
        return None
        
                
    def get_point_win(self, pt=None):
        """ Get point in window coordinates
        :pt: (x,y) point in turtle coordinates
                default: current location
        :returns: (x,y) window coordinates
        """
        if self.iy0_is_top:
            if pt is None:
                pt = (self.win_x,self.win_y)
                return pt 
            
        if pt is None:
            pt = self.get_point_tur()
        tu_x,tu_y = pt
        
        win_x = tu_x + self.win_width//2
        win_y = self.win_height//2 - tu_y
        return (win_x,win_y)
        
    def get_point_tur(self, pt=None):
        """ Get point in turtle coordinates
        :pt: (x,y) point in window coordinates
                default: current location
        :returns: (x,y) in turtle coordinates
        """
        if pt is None:
            pt = (self.pos_x, self.pos_y)
        win_x,win_y = pt
        if win_x is None:
            win_x = self.win_width//2
            win_y = self.win_height//2
        tu_x = win_x - self.win_width//2 
        tu_y = self.win_height//2 - win_y 
        return (tu_x,tu_y)

    def is_at_cell(self, pt=None):
        """ Check if at cell
        :pt: x,y pair location in turtle coordinates
                default: current location
        :returns: True if at cell, else False
        """
        if self.get_cell_at(pt) is None:
            return False 
        
        return True

    def set_cell(self, pt=None, color=None):
        """ Set cell at pt, else current cell
        If no cell at current location create cell
        :pt: at point
            default: current location
        :color: color default: current color
        """
        if not self.is_at_cell(pt):
            self.create_cell(color=color)
        self.change_cell(pt=pt, color=color)

    def change_cell(self, pt=None, color=None):
        """ Change cell at pt if None current pt
        :pt: location default: current
        :color: color default: current color
        :returns: updated cell
        """
        if color is None:
            color = self._color
        cell = self.get_cell_at(pt=pt)
        if cell is None:
            cell = self.create_cell(pt=pt, color=color)
        if cell is not None:
            cell.color_cell(color=color)
            self.display_cell(cell)
        self.update()
        return cell
                
    def color_str(self, color=None):
        """ Return color string
        :color: color specification str or tuple
        """
        color_str = color
        if (color_str is None
             or (isinstance(color_str, tuple)
                  and len(color_str) == 0)
             ):
            color_str = self._color
        if isinstance(color_str,tuple):
            if len(color_str) == 1:
                color_str = color_str[0]
            else:
                color_str = "pink"  # TBD - color tuple work
        return color_str

    def set_visible(self, val=True):
        """ Set cells visible/invisible
        Useful to give sighted a vision
        :val: set visible Default: True
        """
        SlTrace.lg(f"set_visible:{val}")
        for cell in self.cells.values():
            self.set_visible_cell(cell, val)
                
    def set_visible_cell(self, cell, val=True):
        """ Set cells visible/invisible
        Useful to give sighted a vision
        :cell: figure cell
        :val: set visible Default: True
        """
        canvas = self.canvas
        for item_id in cell.canv_items:
            if val:
                canvas.itemconfigure(item_id, state='normal')            
            else:
                if (self._show_marked
                     and cell.mtype !=cell.MARK_UNMARKED): 
                    canvas.itemconfigure(item_id, state='normal')            
                else:
                    canvas.itemconfigure(item_id, state='hidden')
        if not val:
            if cell.mtype != cell.MARK_UNMARKED:
                self.show_cell((cell.ix,cell.iy))   # force view                            

    """
    Setup menus
    """
    def pgm_exit(self):
        if self.pgmExit is not None:
            self.pgmExit()
        else:
            self.speech_maker.quit()
            sys.exit()    
        
    def File_Open_tbd(self):
        print("File_Open_menu to be determined")

    def File_Save_tbd(self):
        print("File_Save_menu to be determined")

    def add_menu_command(self, label=None, call_back=None):
        """ Add simple menu command to top menu
        :label: command label
        :call_back: function to be called when selected
        """
        self.menubar.add_command(label=label, command=call_back)

    def command_proc(self):
        """ Setup command processing options / action
        """

    def cursor_update(self):
        """ Update cursor (current position) display
        """
        if self._cursor_item is not None:
            self.canvas.delete(self._cursor_item)
            self._cursor_item = None
        rd = 5
        if self.iy0_is_top:
            pos_x = self.win_x 
            pos_y = self.win_y
        else:
            pos_x = self.pos_x
            pos_y = self.pos_y
        
        x0 = pos_x-rd
        x1 = pos_x+rd
        y0 = pos_y-rd
        y1 = pos_y+rd
        x0,x1,y0,y1 = self.display_reposition_hack(x0,x1,y0,y1)
        self._cursor_item = self.canvas.create_oval(x0,y0,x1,y1,
                                                    fill="red")
        self.update()

    def on_alt_a(self, event):
        """ keep from key-press
        """
        SlTrace.lg("on_alt_a")

    def on_alt_m(self, event):
        """ keep from key-press
        """
        SlTrace.lg("on_alt_m")

    def on_alt_n(self, event):
        """ keep from key-press
        """
        SlTrace.lg("on_alt_n")

    def on_alt_f(self, event):
        """ keep from key-press
        """
        SlTrace.lg("on_alt_f")

    def trace_menu(self):
        TraceControlWindow(tcbase=self.mw)
            
    def menu_setup(self):
        # creating a menu instance
        self.mw.bind('<Alt-a>', self.on_alt_f)  # Keep this from key cmds
        self.mw.bind('<Alt-d>', self.on_alt_f)  # Keep this from key cmds
        self.mw.bind('<Alt-f>', self.on_alt_f)  # Keep this from key cmds
        self.mw.bind('<Alt-n>', self.on_alt_n)  # Keep this from key cmds
        self.mw.bind('<Alt-M>', self.on_alt_m)  # Keep this from key cmds
        self.mw.bind('<Alt-m>', self.on_alt_m)  # Keep this from key cmds
        self.mw.bind('<Alt-N>', self.on_alt_n)  # Keep this from key cmds
        self.mw.bind('<Alt-n>', self.on_alt_n)  # Keep this from key cmds
        
        menubar = tk.Menu(self.mw)
        self.menubar = menubar      # Save for future reference
        self.mw.config(menu=menubar)
        
        self.Properties = None
        self.LogFile = None
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.File_Open_tbd)
        filemenu.add_command(label="Save", command=self.File_Save_tbd)
        filemenu.add_separator()
        filemenu.add_command(label="Log", command=self.LogFile)
        filemenu.add_command(label="Properties", command=self.Properties)
        filemenu.add_separator()
        ###filemenu.add_comand(label="Cmd", command=self.command_proc)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.pgm_exit, underline=1)
        menubar.add_cascade(label="File", menu=filemenu)
            
        mag_menu = tk.Menu(menubar, tearoff=0)
        self.mag_menu_setup(mag_menu)
        menubar.add_cascade(label="Magnify", menu=mag_menu)
        
        nav_menu = tk.Menu(menubar, tearoff=0)
        self.nav_menu_setup(nav_menu)
        menubar.add_cascade(label="Navigate", menu=nav_menu)
        
        draw_menu = tk.Menu(menubar, tearoff=0)
        self.draw_menu_setup(draw_menu)
        menubar.add_cascade(label="Draw", menu=draw_menu)
        
        aux_menu = tk.Menu(menubar,tearoff=0)
        aux_menu.add_command(label="Trace", command=self.trace_menu,
                             underline=0)
        menubar.add_cascade(label="Auxiliary", menu=aux_menu)

    def draw_menu_setup(self, draw_menu):
        self.draw_menu = draw_menu
        self.draw_dispatch = {}
        self.draw_menu_add_command(label="Help", command=self.draw_help,
                             underline=0)
        self.draw_menu_add_command(label="drawing", command=self.start_drawing,
                             underline=0)
        self.draw_menu_add_command(label="stop_drawing", command=self.stop_drawing,
                             underline=0)
         
    def draw_menu_add_command(self, label, command, underline):
        """ Setup menu commands, setup dispatch for direct call
        :label: add_command label
        :command: command to call
        :underline: short-cut index in label
        """
        self.draw_menu.add_command(label=label, command=command,
                                  underline=underline)
        menu_de = MenuDisp(label=label, command=command,
                              underline=underline)
        
        self.draw_dispatch[menu_de.shortcut] = menu_de

    def draw_direct_call(self, short_cut):
        """ Short-cut call direct to option
        :short_cut: one letter option for call 
        """
        if short_cut not in self.draw_dispatch:
            raise Exception(f"draw option:{short_cut} not recognized")
        menu_de = self.draw_dispatch[short_cut]
        menu_de.command()

    def draw_help(self):
        """ Help for drawing
        """
        """ Help - list command (Alt-d) commands
        """
        help_str = """
        Help - list drawing setup commands (Alt-d) commands
        h - say this help message
        d - Start/enable drawing
        s - stop/disable drawing
        Escape - flush pending report output
        """
        
    def start_drawing(self):
        """ Start/enable drawing
        """
        self._drawing = True 

    def stop_drawing(self):
        """ Stop/disable drawing
        """
        self._drawing = False 

    """ Magnify support package
    """
        
    def mag_menu_setup(self, mag_menu):
        self.mag_menu = mag_menu
        self.mag_dispatch = {}
        self.mag_menu_add_command(label="Help", command=self.mag_help,
                             underline=0)
        self.mag_menu_add_command(label="Remove Pos History", command=self.erase_pos_history,
                             underline=0)
        self.mag_menu_add_command(label="Select", command=self.mag_select,
                             underline=0)
        self.mag_menu_add_command(label="Expand Right", command=self.mag_expand_right,
                             underline=7)
        self.mag_menu_add_command(label="Expand Top", command=self.mag_expand_top,
                             underline=7)
        self.mag_menu_add_command(label="View", command=self.mag_view,
                             underline=0)
         
    def mag_menu_add_command(self, label, command, underline):
        """ Setup menu commands, setup dispatch for direct call
        :label: add_command label
        :command: command to call
        :underline: short-cut index in label
        """
        self.mag_menu.add_command(label=label, command=command,
                                  underline=underline)
        menu_de = MenuDisp(label=label, command=command,
                              underline=underline)
        
        self.mag_dispatch[menu_de.shortcut] = menu_de

    def mag_direct_call(self, short_cut):
        """ Short-cut call direct to option
        :short_cut: one letter option for call 
        """
        if short_cut not in self.mag_dispatch:
            raise Exception(f"mag option:{short_cut} not recognized")
        magde = self.mag_dispatch[short_cut]
        magde.command()

    """ Magnify menu commands
    """
                           
    def mag_help(self):
        """ Help for Alt-m commands
        """
        """ Help - list command (Alt-m) commands
        """
        help_str = """
        Help - list magnify commands (Alt-m) commands
        h - say this help message
        t - expand magnify selected region left/right
        s - select/mark magnify region
        t - expand magnify selected region up/down top/bottom
        v - view region (make new window)
        """
        self.speak_text(help_str)
        
    def mag_select(self):
        """ Select magnification region
            -rectangle including all figure cells traveled so far
            :returns: True if some selected else False
        """
        if self.mag_info is None:
            SlTrace.lg("Magnification is not enabled")
            return False
        
        ix_min, iy_min, ix_max, iy_max = self.bounding_box_ci(cells=self.pos_history)
        if (ix_min is None or iy_min is None
                or ix_max is None or   iy_max is None):
            self.speak_text(f"Bad selection:"
                            f" indexs: {ix_min}, {iy_min}, {ix_max}, {iy_max}")
            return False
        
        SlTrace.lg(f"select: ix_min:{ix_min} iy_min:{iy_min}"
                   f" ix_max:{ix_max} iy_max:{iy_max}")
        select = MagnifySelect(ix_min=ix_min, iy_min=iy_min,
                               ix_max=ix_max, iy_max=iy_max)
        self.mag_info.select = select
        self.show_selection(self.mag_info)
        self.is_selected = True
        return True

    def mag_expand_right(self):
        """ Expand selection region right and left by 20%
        """
    
    def mag_expand_top(self):
        """ Expand selection region top and bottom by 20%
        """
        
    def mag_view(self):
        """ View selected region, creating a new AudioDrawWindow
        """
        if self.mag_info is None or self.mag_info.base_canvas is None:
            SlTrace.lg("Magnification is not enabled")
            return
        
        # Select again, in case of change.  Doesn't hurt.
        if not self.mag_select():
            self.speak_text("No history to select")
            return
        
        display_region = self.mag_info.display_region
        if display_region.ncols is None:
            display_region.ncols = self.grid_width
        if display_region.nrows is None:
            display_region.nrows = self.grid_height
           
        SlTrace.lg(f"view select: {self.mag_info}")    
        self.mag_info.base_canvas.create_magnification_window(self.mag_info)

    def show_selection(self, mag_info):
        """ Display selected region
        :ix_min: minimum ix index
        :iy_min: minimum iy index
        :ix_max: maximum iy index
        :iy_max: maximum iy index
        """
        select = mag_info.select
        canvas = self.canvas
        if self.mag_selection_tag is not None:
            canvas.delete(self.mag_selection_tag)
            self.mag_selection_tag = None
        ix_min,iy_min = select.ix_min,select.iy_min
        ul_cx1,ul_cy1,ul_cx2,ul_cy2 = self.get_cell_rect_win(ix=ix_min, iy=iy_min)
        ul_cx1,ul_cy1,ul_cx2,ul_cy2 = self.display_reposition_hack(ul_cx1,ul_cy1,ul_cx2,ul_cy2)

        ix_max,iy_max = select.ix_max,select.iy_max
        lr_cx1,lr_cy1,lr_cx2,lr_cy2 = self.get_cell_rect_win(ix=ix_max, iy=iy_max)
        lr_cx1,lr_cy1,lr_cx2,lr_cy2 = self.display_reposition_hack(lr_cx1,lr_cy1,lr_cx2,lr_cy2)
        # HACK to take line outside grid
        #self.mag_selection_tag = canvas.create_rectangle(ul_cx1,ul_cy1, lr_cx2,lr_cy2,
        #                         outline="dark blue", width=2)
        self.mag_selection_tag = canvas.create_rectangle(ul_cx1,ul_cy1, lr_cx2,lr_cy2,
                                 outline="dark blue", width=4)
        

        
    """ End of Magnify support
    """



    """ Navigate support package
    """
        
    def nav_menu_setup(self, nav_menu):
        self.nav_menu = nav_menu
        self.nav_dispatch = {}
        self.nav_menu_add_command(label="Help", command=self.nav_help,
                             underline=0)
        self.nav_menu.add_command(label="add At loc", command=self.nav_add_loc,
                             underline=0)
        self.nav_menu_add_command(label="b-remove At loc", command=self.nav_no_add_loc,
                             underline=0)
        self.nav_menu_add_command(label="echo input on", command=self.nav_echo_on,
                             underline=0)
        self.nav_menu_add_command(label="echo off", command=self.nav_echo_off,
                             underline=5)
        
        self.nav_menu_add_command(label="visible cells", command=self.nav_make_visible,
                             underline=0)
        self.nav_menu_add_command(label="invisible cells", command=self.nav_make_invisible,
                             underline=0)
        self.nav_menu_add_command(label="marked", command=self.nav_show_marked,
                             underline=0)
        self.nav_menu_add_command(label="noisy", command=self.make_noisy,
                             underline=0)
        self.nav_menu_add_command(label="silent", command=self.make_silent,
                             underline=0)
        self.nav_menu_add_command(label="talking", command=self.nav_make_talk,
                             underline=0)
        self.nav_menu_add_command(label="log talk", command=self.nav_logt,
                             underline=0)
        self.nav_menu_add_command(label="no log talk", command=self.nav_no_logt,
                             underline=10)
        self.nav_menu_add_command(label="position", command=self.nav_say_position,
                             underline=0)
        self.nav_menu_add_command(label="redraw figure", command=self.nav_redraw,
                             underline=2)
        self.nav_menu_add_command(label="audio beep", command=self.nav_audio_beep,
                             underline=1)
        self.nav_menu_add_command(label="q no audio beep",
                             command=self.nav_no_audio_beep,
                             underline=0)
        self.nav_menu_add_command(label="x enable mouse navigation",
                             command=self.nav_enable_mouse,
                             underline=0)
        self.nav_menu_add_command(label="y disable mouse navigation",
                             command=self.nav_disable_mouse,
                             underline=0)
         
    def nav_menu_add_command(self, label, command, underline):
        """ Setup menu commands, setup dispatch for direct call
        :label: add_command label
        :command: command to call
        :underline: short-cut index in label
        """
        self.nav_menu.add_command(label=label, command=command,
                                  underline=underline)
        menu_de = MenuDisp(label=label, command=command,
                              underline=underline)
        
        self.nav_dispatch[menu_de.shortcut] = menu_de

    def nav_direct_call(self, short_cut):
        """ Short-cut call direct to option
        :short_cut: one letter option for call 
        """
        if short_cut not in self.nav_dispatch:
            raise Exception(f"nav option:{short_cut} not recognized")
        navde = self.nav_dispatch[short_cut]
        navde.command()
                           
                           
    def nav_help(self):
        """ Help for Alt-n commands
        """
        """ Help - list command (Alt-n) commands
        """
        help_str = """
        Help - list navigate commands (Alt-n) commands
        h - say this help message
        a - Start reporting position
        b - remove 
        z - stop reporting position
        e - echo input on
        o - echo off
        v - visible cells
        i - invisible cells
        r - redraw figure
        s - silent speech
        t - talking speech
        l - log speech
        m - show marked(even if invisible)
        n - no log speech
        p - report position
        u - audio beep
        d - no audio beep
        Escape - flush pending report output
        """
        self.speak_text(help_str)
        
    def nav_enable_mouse(self):
        self._enable_mouse = True 
    
    def nav_disable_mouse(self):
        self._enable_mouse = False 
                
        
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
        self.set_audio_beep()
        self.nav_echo_off()
        
    def nav_no_audio_beep(self):
        """ Use audio beeps to aid positioning
        """
        self.set_audio_beep(False)

    def set_audio_beep(self, set=True): 
        """ Set/Clear use audio_beep to aid positioning
        :set: True set flag
        """
        self._audio_beep = set
               
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
        self.draw_cells()    

    def nav_say_position(self):
        self.pos_report(force_output=True)

    def set_show_marked(self,val=True):
        """ Show marked "invisible" cells
        """
        self._show_marked = val

    """ End of Navigate support
    """

    def announce_can_not_do(self, msg=None, val=None):
        """ Announce we can't do something
        """
        if self.audio_beep:
            self.audio_beep.announce_can_not_do(msg=msg, val=val)
        else:
            self.say_text(msg)
    
    def braille_for_color(self, color):
        """ Return dot list for color
        :color: color string or tuple
        :returns: list of dots 1,2,..6 for first
                letter of color
        """
        
        if color is None:
            color = self._color
        if color is None:
            color = ("black")
        color = BrailleCell.color_str(color)
        c = color[0]
        dots = BrailleCell.braille_for_letter(c)
        return dots
    
    def braille_for_letter(self, c):
        """ convert letter to dot number seq
        :c: character
        :returns: dots tupple (1,2,3,4,5,6)
        """
        return BrailleCell.braille_for_letter(c)

    def create_cell(self, cell_ixy=None, color=None,
                    show=True):
        """ Create new cell ad cell_xy
        :cell_xy: ix,iy tuple default: current location
        :color: color default: curren color
        :show: show cell default:True
        :returns: cell
        """
        if cell_ixy is None:
            cell_ixy = self.get_ixy_at()
        if color is None:
            color = self._color
        dots = self.braille_for_color(color)
        bc = BrailleCell(ix=cell_ixy[0], iy=cell_ixy[1],
                         dots=dots, color=color)
        if cell_ixy in self.cells:
            del self.cells[cell_ixy]
        self.cells[cell_ixy] = bc
        if show:
            self.update()
        return bc
            
    def complete_cell(self, cell, color=None):
        """ create/Fill braille cell
            Currently just fill with color letter (ROYGBIV)
        :cell: (ix,iy) cell index or BrailleCell
        :color: cell color default: current color
        :returns: created/modified cell
        """
        if color is None:
            color = self._color
        dots = self.braille_for_color(color)
        bc = BrailleCell(ix=cell[0],iy=cell[1], dots=dots, color=color)
        self.cells[cell] = bc
        return bc

    def update(self):
        """ Update display
        """
        self.mw.update()

    def update_idle(self):
        """ Update pending
        """
        self.mw.update_idletasks()
        
if __name__ == "__main__":
    SlTrace.clearFlags()
    menu_str = "n:sh;d:d"
    key_str = (
                "d"
                ";c;g;9;9;9;9"
                ";c;r;7;7;7;7"
                ";c;v;2;2;2;c;r;2;2;c;o;2;2;2"
                  ";u;8;8;8;8;8;8;8;8;d"
                ";c;o;1;1;1;1"
                ";c;b;3;3;3;3"
                ";c;g;6;6;c;i;6;6;6;c;v;6;6;6"
                ";w"
            )
    aw = AudioDrawWindow(title="AudioDrawWindow Self-Test",
                         menu_str=menu_str,
                         key_str=key_str)

    aw.do_menu_str("n:nu;d:s")
    aw.do_key_str("u")
    
    
    
    
    aw.mw.mainloop()
    
