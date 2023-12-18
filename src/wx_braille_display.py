# wx_braille_display.py      25Oct2023  crs, from braille_display.py
#                            26Feb2023  crs, add self.x_min, self.y_min
#                            21Feb2023  crs, From braille_display.py
#                            19Apr2022  crs  Author
"""
Display graphics on window    Uses tk.Canvas scanning
Supports simple graphical point, line specification
Supports display of 6-point cells
on grid_width by grid_height grid
Supports writing out braille stream
Uses CanvasGrid for canvas scanning
"""
import os
import re
import wx
import __main__
import datetime
import multiprocessing as mp
import threading as th
import turtle as tur
#import tkinter as tk            # Best approach

from select_trace import SlTrace
from wx_speaker_control import SpeakerControlLocal
from braille_cell import BrailleCell
from wx_canvas_grid import CanvasGrid
from magnify_info import MagnifyInfo

        
class BrailleDisplay:
    """ Create and display graphics using Braille
    """
    

    def __init__(self, title="Braille Display",
                 tu=None,       # Not used
                 win_width=800, win_height=800,
                 grid_width=40, grid_height=25,
                 use_full_cells= True,
                 x_min=None, y_min=None,
                 line_width=1, color="black",
                 color_bg = None,
                 color_fill = None,
                 point_resolution=None,
                 blank_char=",",
                 shift_to_edge=True,
                 braille_print=True,
                 braille_window=True,
                 print_cells=False,
                 tk_items=False,
                 canvas_items=False,
                 silent=False,
                 ):
        """ Setup display
        :title: display screen title
        :tu: turtle instance    NOT USED
            default: create one
        :win_width: display window width in pixels
            default: 800
        :win_height: display window height in pixels
            default: 800
        :grid_width: braille width in cells
            default: 40
        :grid_height: braille width in cells
            default: 25
        :color: drawing color
                default: turtle default
        :color_fill: fill color
                default: drawing color
        :color_bg: background color
                default: turtle default
        :use_full_cells: Use full cells for point/lines
            e.g. place color letter in cell
            default: True - usefull cells
        :x_min: x value for left side default: -win_width/2
        :y_min:  y value for bottom default: -win_height/2
        :line_width: line width
        :point_resolution: Distance between points below
            with, no difference is recognized
            default: computed so as to avoid gaps
                    between connected points
                    conservative to simplify/speed
                    computation
        :blank_char: replacement for non-trailing blanks
                    default "," to provide a "mostly blank",
                    non-compressed blank character for the
                    braille graphics
                    default: "," dot 2.
        :shift_to_edge: shift picture to edge/top
                    to aid in finding
                    default: True - shift
        :braille_print:  Print text picture targeted for embosser
                    default: True
        :braille_window: Create interactive braille_window
                    default: True
        :print_cells: Print text representation of display cells
                    default: False,
        :tk_items: Print list of tkinter canvas items default: False
        :canvas_items: print whole canvas item info default: False
        :silent: starting val default: False
        """
        self.display_depth = 0
        if title is None:
            title = "Braille Display"
        self.title = title
        if win_width is None:
            win_width = 800
        self.win_width = win_width
        if win_height is None:
            win_height = 800
        if x_min is None:
            x_min = -win_width/2
        self.x_min = x_min
        self.x_max = x_min + win_width
        if y_min is None:
            y_min = -win_height/2
        self.y_min = y_min
        self.y_max = y_min + win_height
        
        self.win_height = win_height
        self.grid_width = grid_width
        self.cell_width = win_width/self.grid_width
        self.grid_height = grid_height
        self.cell_height = win_height/self.grid_height
        self._braille_window = braille_window
        self._braille_print = braille_print
        self._print_cells = print_cells
        self.tu_screen = tur.Screen()
        self.tu_canvas = self.tu_screen.getcanvas()
        self.blank_char = blank_char
        shift_to_edge = False               # TFD
        self.shift_to_edge = shift_to_edge
        self.tk_items = tk_items
        self.canvas_items = canvas_items
        self.app = wx.App()
        
    def color_str(self, color):
        """ convert turtle colors arg(s) to color string
        :color: turtle color arg
        """
        return BrailleCell.color_str(color)

    def display(self, braille_window=True, braille_print=True,
               braille_title=None,
               print_cells=False, title=None,
               points_window=False,
               tk_items=False,
               canvas_items=False,
               silent=False):
        """ display grid
        :braille_window: True - make window display of braille
                        default:True
        :braille_print: True - print braille
                        default: True
        :braille_title: Printed title in braille text output
                        default: Use default title
        :print_cells: True - print out non-empty cells
                        default: False
        :title: text title to display
                    default:None - no title
        :points_window: make window showing display points
                        instead of braille dots
                    default: False - display dots
        :tk_items: True - display tkinter obj in cell
                    default: self.tk_items - False
        :canvas_items: print whole canvas item info
                    default: self.canvas_items - False
        :silent: quiet mode default: False
        """
        SlTrace.lg("self.display()")
        self.display_depth += 1
        if self.display_depth > 1:
            self.display_depth -= 1
            return
        
        file_base_name = os.path.basename(__main__.__file__)
        current_time = str(datetime.datetime.now())
        mt = re.match(r'(.*):\d+\.\d+$', current_time)
        if mt is not None:
            current_time = mt.group(1)  # Ignore seconds
        username = os.getlogin()
        self.braille_title = f"File: {file_base_name}"
        self.braille_title += f"  Date: {current_time}"
        if username is not None and username != "":
            self.braille_title += f"  User: {username}"
        SlTrace.lg(f"braille_title: {self.braille_title}")
        if self.braille_title is not None:
            title = self.braille_title
        if title is None:
            title = "Audio Feedback -"
        tib = title
        if tib is not None and tib.endswith("-"):
            tib += " Braille Window"

        """ Create CanvasGrid from turtle screen canvas
        """
        ###wxport### geometry = f"{self.win_width}x{self.win_width}"
        ###wxport### mw.geometry(geometry)
        self.speaker_control = SpeakerControlLocal()   # local access to speech engine
        self.canvas_grid = CanvasGrid(base=self.tu_canvas,
                            app=self.app,
                            pgmExit=self.exit,
                            speaker_control = self.speaker_control,
                            width=self.win_width, height=self.win_height,
                            g_xmin = self.x_min,g_ymin=self.y_min,
                            g_nrows=self.grid_height,
                            g_ncols=self.grid_width)
        #mw.withdraw()
        self.aud_win = self.canvas_grid.create_audio_window(title=tib,
                                                            silent=silent)
        self.aud_win.find_edges()

        
        if braille_print:
            if self.braille_title is not None:
                tib = self.braille_title
            else:
                tib = title
            if tib is not None and tib.endswith("-"):
                tib += " Braille Print Output"
            self.aud_win.print_braille(title=tib)
        if print_cells:
            tib = title
            if tib is None:
                tib = "Print Cells"
            if tib is not None and tib.endswith("-"):
                tib += " Braille Cells"
            self.aud_win.print_cells(title=tib)
        if tk_items:
            tib = "tk_items - " + title
            if tib is not None and tib.endswith("-"):
                tib += " Tk Cells"
            self.canvas_grid.show_canvas_items(title=tib)
        if canvas_items:
            tib = "canvas_items - " + title
            if tib is not None and tib.endswith("-"):
                tib += " Canvas items"
            self.canvas_grid.show_canvas(title=tib)
        SlTrace.lg("End of display")
        self.display_depth -= 1
        
        
        
    def snapshot(self, title=None, clear_after=False):
        """ Take snapshot of current braille_screen
        :title: title of snapshot
        :clear_after: clear braille screen after snapshot
        """

    def exit(self, rc=0):
        """ Main program  exit
        """
        SlTrace.lg("BrailleDisplay.exit")
        SlTrace.onexit()    # Force logging quit
        os._exit(rc)

    """ Turtle "Shaddow" Functions
    """
    def tk_updates(self):
        """ Update tk stuff, but don't block
        """
        #tur.update()
        wx.CallLater(100, self.tk_updates)    #loop
    
    def mainloop(self):
        title = self.title
        if title is None:
            title = "Braille Display -"
        self.display()
        #tur.speed(0)    # Turn off animation
        #self.tk_updates()        
        self.app.MainLoop()
        SlTrace.lg("After app.MainLoop()")
                
    def done(self):
        self.mainloop()

    # Special functions
    def set_blank(self, blank_char):
        """ Set blank replacement
        :blank_char: blank replacement char
        :returns: previous blank char
        """
        ret = self.blank_char
        self.blank_char = blank_char
        return ret

        
'''    
    """ Turtle "Shaddow" Functions No longer needed
    """
    
    
    def filling(self):
        return self.tu.filling()
    
    def begin_fill(self):
        return self.tu.begin_fill()
    
    def end_fill(self):
        return self.tu.end_fill()
        
    def dot(self, size=None, *color):
        return self.tu.dot(size, *color)
                        
    def forward(self, length):
        return self.tu.forward(length)
    def fd(self, length):
        return self.forward(length)
    
    def goto(self, x, y=None):
        return self.tu.goto(x, y=y)
    def setpos(self, x, y=None):
        return self.goto(x, y=None)
    def setposition(self, x,  y=None):
        return self.goto(x, y=None)
    
    def heading(self):
        return self.tu.heading()
        
    def backward(self, length):
        return self.tu.backward(length)                
    def bk(self, length):
        return self.backward(length)    
    def back(self, length):
        return self.backward(length)
    
    def circle(self, radius, extent=None, steps=None):
        return self.tu.circle(radius, extent=extent, steps=steps)
    
    def right(self, angle):
        return self.tu.right(angle)
    def rt(self, angle):
        return self.right(angle)
    
    def pendown(self):
        return self.tu.pendown()
    
    def penup(self):
        return self.tu.penup()
        
    def speed(self, speed):
        return self.tu.speed(speed)    
    
    def left(self, angle):
        return self.tu.left(angle)
    
    def lt(self, angle):
        return self.tu.left(angle)
    
    def color(self, *args):
        return self.tu.color(*args)

    def fillcolor(self, *args):
        return self.tu.fillcolor(*args)
    
    def pensize(self, width=None):
        return self.tu.pensize(width=width)
    def width(self, width=None):
        return self.tu.width(width=width)

    def setheading(self, angle): 
        return self.tu.setheading(angle)   
    def seth(self, angle): 
        return self.setheading(angle)   
        
        # screen functions
        
    
    def update(self):
        self.mw.update()

    # screen functions
    def screensize(self, canvwidth=None, canvheight=None, bg=None):
        return self.screen.screensize(canvwidth=None,
                                       canvheight=None, bg=None)
    '''    
        
if __name__ == "__main__":
    import wx_square_loop_colors
    #import braille_display_test2

