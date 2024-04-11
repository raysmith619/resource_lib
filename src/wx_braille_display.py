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
import sys
import re
import wx
import time
import datetime

from select_trace import SlTrace
from wx_speaker_control import SpeakerControlLocal
from braille_cell import BrailleCell
from tk_canvas_grid import TkCanvasGrid
from magnify_info import MagnifyInfo
from wx_audio_draw_window import AudioDrawWindow
from braille_error import BrailleError
from wx_tk_rem_user import TkRemUser
        
class BrailleDisplay:
    """ Create and display graphics using Braille
    """
    

    def __init__(self, tkr=None,
                 title="Braille Display",
                 display_list=None,
                 win_width=800, win_height=800,
                 grid_width=40, grid_height=25,
                 use_full_cells= True,
                 x_min=None, y_min=None,
                 line_width=1, color="black",
                 color_bg = None,
                 color_fill = None,
                 point_resolution=None,
                 blank_char=",",
                 shift_to_edge=None,
                 braille_print=True,
                 braille_window=True,
                 print_cells=False,
                 tk_items=False,
                 canvas_items=False,
                 silent=False,
                 ):
        """ Setup display
        :tkr: Access to tkinter from remote user
        :title: display screen title
        :display_list: list of (ix,iy,color) to display
            default: none
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
                    default: False - no shift
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
        if tkr is None:
            SlTrace.lg("No link to remote")
            tkr =  TkRemUser(remote=False)
        self.tkr = tkr
        self.display_list = display_list
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
        self.blank_char = blank_char
        if shift_to_edge is None:
            shift_to_edge = False               # TFD
        self.shift_to_edge = shift_to_edge
        self.tk_items = tk_items
        self.canvas_items = canvas_items
        self.app = wx.App()
    
    
    def MainLoop(self):
        """ Just an inclosed access to wx loop
        """
        self.app.MainLoop()
     
    def color_str(self, color):
        """ convert turtle colors arg(s) to color string
        :color: turtle color arg
        """
        return BrailleCell.color_str(color)

    def display(self,
                display_list=None,
                braille_window=True, braille_print=True,
                braille_title=None,
                print_cells=False, title=None,
                points_window=False,
                tk_items=False,
                canvas_items=False,
                silent=False):
        """ display grid
        :display_list: list of (ix,iy,color) cells to display
                default: self.display_list else none
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
        if display_list is None:
            display_list = self.display_list
        self.display_list = display_list
        self.braille_title = braille_title
        if hasattr(sys.modules, '__main__'):        
            pgm_file = sys.modules['__main__'].__file__
            file_base_name = os.path.basename(pgm_file)
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

        self.speaker_control = SpeakerControlLocal()   # local access to speech engine
        self.adw = AudioDrawWindow(
                            self.tkr,
                            display_list=self.display_list,
                            app=self.app,
                            title=title,
                            speaker_control=self.speaker_control,
                            iy0_is_top=True,
                            pgmExit=self.exit,
                            ###x_min=self.x_min, y_min=self.y_min,
                            ###x_max=self.x_max, y_max=self.y_max,
                            silent=silent)

        
        if braille_print:
            if self.braille_title is not None:
                tib = self.braille_title
            else:
                tib = title
            if tib is not None and tib.endswith("-"):
                tib += " Braille Print Output"
            self.adw.print_braille(title=tib)
        if print_cells:
            tib = title
            if tib is None:
                tib = "Print Cells"
            if tib is not None and tib.endswith("-"):
                tib += " Braille Cells"
            self.adw.print_cells(title=tib)
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

        
        
if __name__ == "__main__":
    import argparse
    from braille_cell_text import BrailleCellText
    from wx_braille_cell_list import BrailleCellList
    
    spokes_picture="""
    ,,,,,,,,,,,iii
    ,,,,,,,,,,iiiii
    ,,,,,,,,,,iiiii,,,,,,vvv
    ,,,,,,,,,,iiiii,,,,,vvvvv
    ,,,,,,,,,,,,ii,,,,,,vvvvv
    ,,,bb,,,,,,,,i,,,,,,vvvvv
    ,,bbbbb,,,,,,i,,,,,vv
    ,,bbbbb,,,,,,i,,,,vv
    ,,bbbbbbb,,,,ii,,vv
    ,,,,,,,,bbbb,,i,vv,,,,,,,,rr
    ,,,,,,,,,,bbbbivv,,,,,,,,rrrr
    ,,,,,,,,,,,,,bvvrrrrrrrrrrrrr
    ,,,,,,,,,,ggggyoo,,,,,,,,rrrr
    ,,,,,,,,gggg,,y,oo,,,,,,,,rr
    ,,ggggggg,,,,yy,,oo
    ,,ggggg,,,,,,y,,,,oo
    ,,ggggg,,,,,,y,,,,,oo
    ,,,gg,,,,,,,,y,,,,,,ooooo
    ,,,,,,,,,,,,yy,,,,,,ooooo
    ,,,,,,,,,,yyyyy,,,,,ooooo
    ,,,,,,,,,,yyyyy,,,,,,ooo
    ,,,,,,,,,,yyyyy
    ,,,,,,,,,,,yyy
    """
    spokes_bct = BrailleCellText(text=spokes_picture)
    spokes_cells = spokes_bct.get_cells()
    spokes_bcs = BrailleCellList(spokes_cells).to_string()
    
    parser = argparse.ArgumentParser()
    args = parser.parse_args()             # or die "Illegal options"
    SlTrace.lg(f"args: {args}\n")


    bd = BrailleDisplay(display_list=spokes_bcs)
    bd.display(title="Selftest")
    bd.MainLoop()

