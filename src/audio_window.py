#audio_window.py    08Nov2022  crs, Author
"""
Provide graphical window with audio feedback as to cursor position
to facilitate examination by blind people
Uses turtle to facilitate cursor movement within screen
"""
import sys
import tkinter as tk
import turtle as tu
from math import sqrt
import time
from datetime import datetime 

from select_trace import SlTrace
from grid_fill_gobble import GridFillGobble
from grid_path import GridPath
from braille_cell import BrailleCell
from audio_beep import AudioBeep
from Lib.pickle import FALSE, NONE


try:
    import pyttsx3
    pyttsx3_engine = pyttsx3.init()
except:
    pyttsx3_engine = None 

class SpeakText:
    """ Item to speak
    """
    # Speech Types:
    REPORT = "report"
    CMD = "cmd"
    ECHO = "echo"
    
    def __init__(self,  msg,
                 speech_type="report",
                 dup_stdout=True,
                   ):
        
        """ Setup item
        :msg: text of speech
        :speech_type: type of speach default: report
                REPORT: std reporting
                CMD: command
                ECHO: echo input
        :dup_stdout: duplicate text to stdout/console
                default: True - duplicate
        """
        self.msg = msg
        self.speech_type = speech_type
        self.dup_stdout = dup_stdout
            
class AudioWindow:


    """
    Menu Processing functions
    """

    
    def __init__(self, title,
        win_width=800, win_height=800,
        grid_width=40, grid_height=25,
        x_min=None, y_min=None,
        line_width=1, color="black",
        pos_check_interval= .1,
        pos_rep_interval = .1,
        pos_rep_queue_max = 4,
        visible_figure = True,
        pgmExit=None,
                 ):
        """ Setup audio window
        :win_width: display window width in pixels
            default: 800
        :win_height: display window height in pixels
            default: 800
        :x_min: minimum coordinate tu
                default: win_width//2
        :y_min: minimum coordinate tu
                default: -win_height//2
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
        """
        self.win_width = win_width
        self.win_height = win_height
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_height = win_height/self.grid_height
        self.pgmExit = pgmExit
        if x_min is None:
            x_min = -win_width//2
        self.x_min = x_min
        self.x_max = x_min + win_width
        if y_min is None:
            y_min = -win_width//2
        self.y_min = y_min
        self.y_max = y_min + win_height
        
        mw = tk.Tk()
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
        self.mw.update()        # Force display
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
        self.turtle = tu.RawTurtle(canvas)
        #self.turtle.hideturtle()
        self.turtle_screen = self.turtle.getscreen()
        self.turtle_screen.tracer(0)
        self.turtle.showturtle()
        self.turtle.penup()

        self.speak_text_lines = []  # pending speak lines (SpeakText)       
        self.escape_pressed = False # True -> interrupt/flush
        self.cells = []
        self.set_cell_lims()
        self.do_talking = True      # Enable talking
        self.speak_text_line_after = None
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
        if pyttsx3_engine:
            self.pos_rep_interval = .1
        self.pos_rep_time = datetime.now()  # Time of last report
        self.pos_check_interval = pos_check_interval
        if pyttsx3_engine:
            self.pos_check_interval = .01
        self._echo_input = True     # True -> speak input
        self._track_goto_cell = True    # True -> mark cells where we have gone
        self.goto_travel_list = []    # Memory of where we have gone
        self.goto_cell_list = []
        self.goto_travel_list_index = None
        self.cell_history = []          # History of all movement
        self._audio_beep = False
        self.audio_beep = AudioBeep(self)
        self.grid_path = GridPath(goto_path=self.cell_history)
        self.running = True         # Set False to stop
        self.mw.focus_force()
        self.canvas.bind('<Motion>', self.motion)
        self.canvas.bind('<Button-1>', self.on_button_1)
        self.canvas.bind('<B1-Motion>', self.on_button_1_motion)
        self.mw.bind('<KeyPress>', self.on_key_press)

        self.pos_check()            # Startup possition check loop
        mw.update()     # Make visible

                
    def speak_text(self, msg, dup_stdout=True,
                   speech_type="report"):
        """ Speak text, if possible else write to stdout
        :msg: text message
        :dup_stdout: duplicate to stdout default: True
        :speech_type: type of speech default: "report"
            report - standard reporting
            cmd    - command
        """
        if self.logging_speech:
            SlTrace.lg(msg)
        self.add_speak_text_lines(msg.split("\n"))
        if self.speak_text_line_after is not None:
            self.mw.after_cancel(self.speak_text_line_after)
            self.speak_text_line_after = None
        self.speak_text_line_after = self.mw.after(0,
                                     self.speak_text_line)

    def add_speak_text_lines(self, lines):
        """ Add lines to be spoken
        :lines: list of lines
        """
        for line in lines:
            text_line = SpeakText(line)
            self.speak_text_lines.append(text_line)
                
    def speak_text_line(self):
        """ Called to speak pending line
        """
        if len(self.speak_text_lines) == 0:
            return
            
        speak_text = self.speak_text_lines.pop(0)
        if self.do_talking:
            if pyttsx3_engine:
                if speak_text.speech_type == SpeakText.REPORT:
                    pyttsx3_engine.say(speak_text.msg)
                    pyttsx3_engine.setProperty('rate',240)
                    pyttsx3_engine.setProperty('volume', 0.9)
                    pyttsx3_engine.runAndWait()
                elif speak_text.speech_type == SpeakText.ECHO:
                    pyttsx3_engine.say(speak_text.msg)
                    pyttsx3_engine.setProperty('rate',240)
                    pyttsx3_engine.setProperty('volume', 0.9)
                    pyttsx3_engine.runAndWait()
                else:
                    raise Exception(f"Unrecognized speech_type"
                                    f" {speak_text.speech_type}")
                
            else:
                SlTrace.lg(f":{speak_text.msg}")
        if len(self.speak_text_lines) > 0:
            self.speak_text_line_after = self.mw.after(
                                100, self.speak_text_line)
        else:
            if self.speak_text_line_after is not None:
                self.mw.after_cancel(self.speak_text_line_after)
                self.speak_text_line_after = None

    def speak_text_stop(self):
        """ Stop ongoing speach, flushing queue
        """
        self.speak_text_lines = []
        
    def motion(self, event):
        """ Mouse motion in  window
        """
        x,y = event.x, event.y
        SlTrace.lg(f"motion x={x} y={y}", "aud_motion")
        self.move_to(x,y)
        #self.pos_x = x 
        #self.pos_y = y
        #self.pos_check()
        return              # Processed via pos_check()

    def on_button_1(self, event):
        """ Mouse button in window
        """
        x,y = event.x, event.y
        SlTrace.lg(f"motion x={x} y={y}", "aud_motion")
        self.move_to(x,y)
        cell = self.get_cell_at()
        if cell is not None:
            self.set_visible_cell(cell)
        self.pos_check()

    def on_button_1_motion(self, event):
        """ Motion will button down is
        treated as mouse click at point
        """
        self.on_button_1(event)
        
    def on_key_press(self, event):
        keysym = event.keysym
        keyslow = keysym.lower()
        if keysym == 'Alt_L':
            return                  # Ignore ALT
        self.key_echo(keysym)
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
        elif keyslow == "c":
            self.key_color_cell()
        elif keyslow == "g":
            self.key_goto()             # Goto closest figure
        elif keyslow == "h":
            self.key_help()             # Help message
        elif keyslow == "p":
            self.key_report_pos() 
        else:
            self.speak_text(f"Don't understand {keysym}")

    """
    keyboard commands
    """
    def key_echo(self,keysym):
        """ Echo key, if appropriate
        :keysym; key symbol
        """
        self.key_flush(keysym=keysym)
        if self._echo_input:
            self.speak_text(keysym, speech_type=SpeakText.ECHO)

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

    def mark_cell(self, cell):
        """ Mark cell for viewing of history
        :cell: Cell(BrailleCell) or (ix,iy) of cell
        """
        if isinstance(cell, BrailleCell):
            ixy = (cell.ix,cell.iy) 
        else:
            ixy = cell
        if ixy in self.cells:
            cell = self.cells[ixy]
            canvas = self.canvas
            for item_id in cell.canv_items:
                item_type = canvas.type(item_id)
                if item_type == "rectangle":
                    canvas.itemconfigure(item_id, fill='dark gray')            
            
        
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
        g - Go to closest figure
        p - Report/Say current position
        Escape - flush pending report output
        """
        self.speak_text(help_str)
        
    def key_up(self):
        self.move_cursor(y_inc=1)
    
    def key_down(self):
        self.move_cursor(y_inc=-1)
        
    def key_left(self):
        self.move_cursor(x_inc=-1)
        
    def key_right(self):
        self.move_cursor(x_inc=1)

    def key_exit(self):
        self.speak_text("Quitting Program")
        self.mw.update()     # Process any pending events
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
        self.mw.update()

    def key_talk(self, val=True):
        """ Enable / Disable talking
        """
        self.do_talking = val
        SlTrace.lg(f"do_talking:{self.do_talking}")

    def key_report_pos(self):
        """ Report current position with voice
        """
        self.pos_check(force_output=True, with_voice=True) 
                            
    def key_space(self):
        """ repeat last key cmd
        """
    def key_tab(self):
        """ repeat last key cmd 4 times
        """
    
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
        
        if len(self.pos_rep_queue) == 0:
            return          # Nothing to report
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
    
            ix,iy = self.get_point_cell()
            if self._audio_beep and not with_voice:
                self.audio_beep.announce_pcell((ix,iy))
                if self.grid_path is not None:
                    pcells = self.grid_path.find_predictive_list(goto_path=self.cell_history)
                    self.audio_beep.announce_pcells(pc_ixys=pcells)
            else:
                if self.rept_at_loc or with_voice:
                    rep_str += f" at row{self.grid_height-iy} column{ix+1}"
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
        """ Do position checkng followed by report queue processing
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

        if x is None:
            x = self.pos_x
        if y is None:
            y = self.pos_y
        if x is None:
            return  None,None,None, None # No drawing/location
        
        tu_x, tu_y = self.get_point_tur((x,y))        
        cell_ixiy = self.get_point_cell((tu_x,tu_y))
        SlTrace.lg(f"motion: x:{x}, y:{y} ix,iy: {cell_ixiy}", "aud_motion")
        if cell_ixiy in self.cells:
            if force_output:
                self.pos_rep_force_output = True
                self.pos_rep_queue = []
            self.pos_rep_queue.append(("draw", cell_ixiy))
            return 0,dist_x,dist_y      # Force "on figure"
        
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
        :cells: cells to draw
        :show_points: instead of braille, show sample points
        """
        if cells is None:
            cells = self.cells
        self.cells = cells      # Copy
        for ix in range(self.grid_width):
            for iy in range(self.grid_height):
                cell_ixy = (ix,iy)
                if cell_ixy in self.cells:
                    self.display_cell(self.cells[cell_ixy],
                                      show_points=show_points)
        self.mw.update()
        min_x, max_y, max_x,min_y = self.drawing_bounding_box()
        if min_x is not None:            
            SlTrace.lg(f"Lower left: min_x:{min_x} min_y:{min_y}")
            SlTrace.lg(f"Upper Right: max_x:{max_x} max_y:{max_y}")
            self.set_cursor_pos_tu(x=min_x, y=min_y)
            x,y = self.get_point_win((min_x,min_y))
            self.pos_check(x=x,  y=y)
        self.grid_path = GridPath(goto_path=self.cell_history)
        self.audio_beep.set_cells(cells)
        self.mw.update()
        #self.turtle.penup()
        
    def set_cursor_pos_win(self, x=0, y=0):
        """ Set mouse cursor position in win(canvas) coordinates
        :x: x-coordinate (win(canvas))
        :y: y-coordinate (win(canvas))
        """
        tu_x,tu_y = self.get_point_tur((x,y))
        self.set_cursor_pos_tu(x=tu_x, y=tu_y)

    def set_cursor_pos_tu(self, x=0, y=0):
        """ Set mouse cursor position in turtle coordinates
        :x: x-coordinate (turtle)
        :y: y-coordinate (turtle)
        """
        if not self.running:
            return
        
        self.canvas.bind('<Motion>', None)  # Disable motion events
        self.turtle.showturtle()
        self.turtle.goto(x=x, y=y)
        win_x,win_y = self.get_point_win((x,y))
        self.pos_x,self.pos_y = win_x,win_y
        cell_ixiy = self.get_cell_at()
        if cell_ixiy is not None:
            self.cell_history.append(cell_ixiy)
            self.mark_cell(cell_ixiy)         # Mark cell if one

        self.turtle_screen.update()
        if not self.mw.winfo_exists():
            return 
        
        self.mw.update()
        self.pos_check(force_output=True)
        self.canvas.bind('<Motion>', self.motion)   # Reenable

    def move_cursor(self, x_inc=0, y_inc=0):
        """ Move cursor by cell increments to center of
        cell to maximise chance of seeing cell figures
        :x_inc: x change default: no movement
        :y_inc: y change default: no movement
        """
        tu_x,tu_y = self.get_point_tur((self.pos_x, self.pos_y))
        ix,iy = self.get_point_cell((tu_x,tu_y))
        ix += x_inc
        iy += y_inc
        win_xc,win_yc = self.get_cell_center_win(ix,iy)
        SlTrace.lg(f"move_cursor: ix={ix}, y={iy}", "move_cursor")
        self.move_to(win_xc,win_yc)
        

    def move_to(self, x,y):
        """ Move to window loc
        Stop at edges, with message
        """
        margin = 10
        top_margin = 20     # HACK to determine top before low level check
        bottom_margin = 20   # HACK to determine before low level check
        tu_x, tu_y = self.get_point_tur((x,y))
        if tu_x <= self.x_min + margin:
            self.pos_report("msg", "At left edge")
            return
        elif tu_x >= self.x_max - margin:
            self.pos_report("msg", "At right edge")
            return                               
        if tu_y <= self.y_min + bottom_margin:
            self.pos_report("msg", "At bottom edge")
            return
        elif tu_y >= self.y_max - top_margin:
            self.pos_report("msg", "At top edge")
            return                               
        self.set_cursor_pos_win(x,y)
        
    def set_cell_lims(self):
        """ create cell boundary values bottom through top
         so:
             cell_xs[0] == left edge
             cell_xs[grid_width] == right edge
             cell_ys[0] == bottom edge
             cell_ys[grid_height] == top edge
        """
         
        self.cell_xs = []
        self.cell_ys = []

        for i in range(self.grid_width+1):
            x = int(self.x_min + i*self.win_width/self.grid_width)
            self.cell_xs.append(x)
        for i in range(self.grid_height+1):
            y = int(self.y_min + i*self.win_height/self.grid_height)
            self.cell_ys.append(y)

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
        
        pt_ixiy = self.get_point_cell((tu_x,tu_y))
        cell_closest = None         # Set if found
        if pt_ixiy in self.cells:
            cell_closest = self.cells[pt_ixiy]      # We're there
            return 0,0,0, cell_closest        # On drawing
        
        min_dist = None
        min_dist_x = 0      # x,y offset at min dist
        min_dist_y = 0
        pt_ix, pt_iy = pt_ixiy 
        for cell_ixiy in self.cells:
            cell_ix, cell_iy = cell_ixiy
            dist = sqrt((cell_ix-pt_ix)**2 + (cell_iy-pt_iy)**2)
            if min_dist is None or dist < min_dist:
                min_dist = dist
                min_dist_x = cell_ix - pt_ix
                min_dist_y = cell_iy - pt_iy
                cell_closest = self.cells[cell_ixiy]    # Closest so far
        if min_dist <= 0:
            min_dist = .001     # Saving 0 for in display element
        return min_dist, min_dist_x, min_dist_y, cell_closest

    def drawing_bounding_box(self):
        """ turtle coordinates which bound displayed figure
        :returns: min_x, max_y, max_x, min_y  (upper left) (lower right)
                    None,None,None,None if no figure
        """
        min_ix, max_iy, max_ix, min_iy = self.drawing_bounding_box_ci()
        if min_ix is None:
            return None,None,None,None      # No figure
        
        min_x, max_y, _, _ = self.get_cell_rect_tur(min_ix,max_iy)
        _, _, max_x, min_y = self.get_cell_rect_tur(max_ix,min_iy)
        return min_x,max_y, max_x, min_y
    
    def drawing_bounding_box_ci(self):
        """ cell indexes which bound displayed figure
        :returns: min_ix, max_iy, max_ix, min_iy  (upper left) (lower right)
                    None,None,None,None if no figure
        """
        if not hasattr(self, "cells"):
            return None,None,None,None         # Not yet setup
        
        min_ix, max_iy, max_ix,min_iy = None,None,None,None
        for cell_ixiy in self.cells:
            cell_ix, cell_iy = cell_ixiy
            if min_ix is None or cell_ix < min_ix:
                min_ix = cell_ix
            if max_ix is None or cell_ix > max_ix:
                max_ix = cell_ix
            if min_iy is None or cell_iy < min_iy:
                min_iy = cell_iy
            if max_iy is None or cell_iy > max_iy:
                max_iy = cell_iy
        return min_ix, max_iy, max_ix,min_iy

    
    def display_cell(self, cell, show_points=False):
        """ Display cell
        :cell: BrailleCell
        :show_points: show points instead of braille
                default: False --> show braille dots
        """
        canvas = self.canvas
        # Remove current items, if any
        for item_id in cell.canv_items:
            self.canvas.delete(item_id)
        cell.canv_items = []
        ix = cell.ix
        iy = cell.iy 
        cx1,cy1,cx2,cy2 = self.get_cell_rect_win(ix=ix, iy=iy)
        ###TFD HACK to reposition cell dispaly
        cx1 -= 400
        cx2 -= 400
        cy1 -= 400
        cy2 -= 400
        canv_item = canvas.create_rectangle(cx1,cy1,cx2,cy2,
                                 outline="light gray")
        cell.canv_items.append(canv_item)
        self.mw.update()
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
            self.mw.update()    # So we can see it now 
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
            self.mw.update()
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
        if ix < 0:
            SlTrace.lg(f"ix:{ix} < 0")
            ix = 0
        max_ix = len(self.cell_xs)-1
        if ix+1 > max_ix:
            SlTrace.lg(f"ix:{ix+1} >= {len(self.cell_xs)}")
            ix = max_ix-1
        if iy < 0:
            SlTrace.lg(f"iy:{iy} < 0", "aud_move")
            iy = 0
        max_iy = len(self.cell_ys)-1
        if iy+1 > max_iy:
            SlTrace.lg(f"iy:{iy+1} >= {len(self.cell_ys)}")
            iy = max_iy-1
        x1 = self.cell_xs[ix]
        x2 = self.cell_xs[ix+1]
        y1 = self.cell_ys[iy]
        #SlTrace.lg(f"get_cell_rect_tur:iy={iy} {len(self.cell_ys)}")
        y2 = self.cell_ys[iy+1]
        return (x1,y1,x2,y2)
        
        
    def get_point_cell(self, pt=None):
        """ Get cell(indexes) in which point resides
        If on an edge returns lower cell
        If on a corner returns lowest cell
        :pt: x,y pair location in turtle coordinates
                default: current location
        :returns: ix,iy cell pair
        """
        if pt is None:
            pt = self.get_point_tur()
        tu_x,tu_y = pt
        ix = int((tu_x-self.x_min)/self.win_width*self.grid_width)
        iy = int((tu_y-self.y_min)/self.win_height*self.grid_height)
        return (ix,iy)

    def get_cell_at(self, pt=None):
        """ Get cell at location, if one
        :pt: x,y pair location in turtle coordinates
                default: current location
        :returns: cell if at, else None
        """
        cell_ixiy = self.get_point_cell(pt)
        if cell_ixiy is None:
            return None 
        
        if cell_ixiy in self.cells:
            return self.cells[cell_ixiy]
        
        return None
        
    def get_point_win(self, pt=None):
        """ Get point in window coordinates
        :pt: (x,y) point in turtle coordinates
                default: current location
        :returns: (x,y) window coordinates
        """
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
                canvas.itemconfigure(item_id, state='hidden')            

    """
    Setup menus
    """
    def pgm_exit(self):
        if self.pgmExit is not None:
            self.pgmExit()
        else:
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

    def on_alt_c(self, event):
        """ keep from key-press
        """
        SlTrace.lg("on_alt_c")

    def on_alt_f(self, event):
        """ keep from key-press
        """
        SlTrace.lg("on_alt_f")
    
    def menu_setup(self):
        # creating a menu instance
        self.mw.bind('<Alt-f>', self.on_alt_f)  # Keep this from key cmds
        self.mw.bind('<Alt-c>', self.on_alt_c)  # Keep this from key cmds
        
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
        
        cmd_menu = tk.Menu(menubar, tearoff=0)
        cmd_menu.add_command(label="Help", command=self.cmd_help,
                             underline=0)
        cmd_menu.add_command(label="add At loc", command=self.cmd_add_loc,
                             underline=0)
        cmd_menu.add_command(label="z-remove At loc", command=self.cmd_no_add_loc,
                             underline=0)
        cmd_menu.add_command(label="echo input on", command=self.cmd_echo_on,
                             underline=0)
        cmd_menu.add_command(label="echo off", command=self.cmd_echo_off,
                             underline=5)
        
        cmd_menu.add_command(label="visible cells", command=self.cmd_make_visible,
                             underline=0)
        cmd_menu.add_command(label="invisible cells", command=self.cmd_make_invisible,
                             underline=0)
        cmd_menu.add_command(label="silent", command=self.cmd_make_silent,
                             underline=0)
        cmd_menu.add_command(label="talking", command=self.cmd_make_talk,
                             underline=0)
        cmd_menu.add_command(label="log talk", command=self.cmd_logt,
                             underline=0)
        cmd_menu.add_command(label="no log talk", command=self.cmd_no_logt,
                             underline=0)
        cmd_menu.add_command(label="position", command=self.cmd_say_position,
                             underline=0)
        cmd_menu.add_command(label="redraw figure", command=self.cmd_redraw,
                             underline=2)
        cmd_menu.add_command(label="audio beep", command=self.cmd_audio_beep,
                             underline=1)
        cmd_menu.add_command(label="no audio beep",
                             command=self.cmd_no_audio_beep,
                             underline=9)
        
        menubar.add_cascade(label="Command", menu=cmd_menu)


    def cmd_help(self):
        """ Help for Alt-c commands
        """
        """ Help - list command (Alt-c) commands
        """
        help_str = """
        Help - list command (Alt-c) commands
        h - say this help message
        a - Start reporting position
        z - stop reporting position
        e - echo input on
        o - echo off
        v - visible cells
        i - invisible cells
        r - redraw figure
        s - silent speech
        t - talking speech
        l - log speach
        n - no log speach
        p - report position
        u - audio beep
        d - no audio beep
        Escape - flush pending report output
        """
        self.speak_text(help_str)

    def cmd_echo_on(self):
        self._echo_input = True 
    
    def cmd_echo_off(self):
        self._echo_input = False 
                
    def cmd_add_loc(self):
        """ Add At location info to report
        """
        self.key_set_rept_at()
        
    def cmd_audio_beep(self):
        """ Use audio beeps to aid positioning
        """
        self.set_audio_beep()
        
    def cmd_no_audio_beep(self):
        """ Use audio beeps to aid positioning
        """
        self.set_audio_beep(False)

    def set_audio_beep(self, set=True): 
        """ Set/Clear use audio_beep to aid positioning
        :set: True set flag
        """
        self._audio_beep = set
               
    def cmd_no_add_loc(self):
        """ Remove At location info to report
        """
        self.key_set_rept_at(False)
        
    def cmd_logt(self):
        """ Log talking
        """
        self.key_log_speech()

    def cmd_no_logt(self):
        self.key_log_speech(False)

    def cmd_make_invisible(self):
        self.key_visible(False) 
        
    def cmd_make_visible(self):
        self.key_visible()

    def cmd_make_silent(self):
        self.key_talk(False)

    def cmd_make_talk(self):
        self.key_talk()
    
    def cmd_redraw(self):
        self.draw_cells()    

    def cmd_say_position(self):
        self.pos_report(force_output=True)
        
if __name__ == "__main__":
    aw = AudioWindow(title="AudioWindow Self-Test")

    
    
    
    
    aw.mw.mainloop()
    
