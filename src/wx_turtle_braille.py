#wx_turtle_braille.py       02Nov2023  crs from turtle_braille.property
#                           27Feb2023  crs from turtle_braille.py
#                           21Feb2023  crs  From turtle_braille.py
#                           16Apr2022  crs  Author
"""
# Using tk.Canvas scanning
Turtle augmented with braille graphics output
turtle commands create Turtle output plus approximate braille
output
Adjusted tu use CanvasGrid with canvas scanning
"""
from turtle import *

from select_trace import SlTrace
SlTrace.clearFlags()
import wx_braille_display


bd = wx_braille_display.BrailleDisplay(win_width=None,
                    win_height=None,
                    grid_width=32,
                    grid_height=25)


"""
External functions 
Some day may model after turtle's _make_global_funcs
"""


def mainloop():
    bd.mainloop()

def done():
    bd.done()
    
### special functions
def set_blank(blank_char):
    """ Set blank replacement
    :blank_char: blank replacement char
    :returns: previous blank char
    """
    ret = bd.set_blank(blank_char)
    return ret

"""
Screen size function to facilitate general
possitioning
"""
def x_min():
    return bd.x_min

def x_max():
    return bd.x_max
def y_min():
    return bd.y_min

def y_max():
    return bd.y_max



    
if __name__ == '__main__':
    from wx_turtle_braille_link import *
    #from turtle_braille import *    # Get graphics stuff
    #tum.points_window = True
    #tum.print_cells = True
    w,h = screensize()
    print(f"w:{w}, h:{h}")
    set_blank(" ")
    penup()
    goto(-w/2+50,h/2-100)
    pendown()
    width(40)
    color("green")
    pendown()
    forward(200)
    right(90)
    forward(200)
    right(90)
    forward(200)
    right(90)
    forward(200)
    penup()
    done()    
            
