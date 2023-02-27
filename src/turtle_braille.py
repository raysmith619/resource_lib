#turtle_braille_new.py    21Feb2023    crs  From turtle_braille.py
#                       16Apr2022    crs  Author
"""
Turtle augmented with braille graphics output
turtle commands create Turtle output plus approximate braille
output
Adjusted tu use CanvasGrid with canvas scanning
"""
from turtle import *

from select_trace import SlTrace
SlTrace.clearFlags()
from braille_display_2 import BrailleDisplay


bd = BrailleDisplay(win_width=None,
                    win_height=None,
                    grid_width=32,
                    grid_height=25)


"""
External functions 
Some day may model after turtle's _make_global_funcs
"""


def mainloop():
    return bd.mainloop()
def done():
    return bd.done()
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


""" Link to turtle functions
"""

def filling():
    return bd.filling()

def begin_fill():
    return bd.begin_fill()

def end_fill():
    return bd.end_fill()
    
def dot(size=None, *color):
    return bd.dot(size, *color)
                    
def forward(length):
    return bd.forward(length)
def fd(length):
    return bd.forward(length)

def goto(x, y=None):
    return bd.goto(x, y=y)
def setpos(x, y=None):
    return bd.goto(x, y=None)
def setposition(x,  y=None):
    return bd.goto(x, y=None)


def setheading(angle): 
    return bd.setheading(angle)   
def seth(self, angle): 
    return setheading(angle)   
    
def backward(length):
    return bd.backward(length)                
def bk(length):
    return bd.backward(length)    
def back(length):
    return bd.backward(length)

def circle(radius, extent=None, steps=None):
    return bd.circle(radius, extent=extent, steps=steps)

def right(angle):
    return bd.right(angle)
def rt(angle):
    return bd.right(angle)

def pendown():
    return bd.pendown()

def penup():
    return bd.penup()
    
def speed(speed):
    return bd.speed(speed)    

def left(angle):
    return bd.left(angle)

def lt(angle):
    return bd.left(angle)

def color(*args):
    return bd.color(*args)

def pensize(width=None):
    return bd.pensize(width=width)
def width(width=None):
    return bd.pensize(width=width)

    # screen functions
    
def screensize(canvwidth=None, canvheight=None, bg=None):
    return bd.screensize(canvwidth=canvwidth,
                          canvheight=canvheight, bg=bg)




    
if __name__ == '__main__':
    from turtle_braille_link_2 import *
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
            
