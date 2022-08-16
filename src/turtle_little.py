#turtle_little.py    17Jul2022  crs  From turtle_braille
"""
Light weight(we hope) interface to provide a subset
of turtle capability, printing output to character based
output to stdout
"""
from math import sin, cos, pi, fmod
import turtle as tu

from select_trace import SlTrace
SlTrace.clearFlags()
from turtle_little_display import TurtleLittleDisplay
    
class TurtleLittle():
    """ Character based output to service those who don't 
    have access to turtle
    """
    def __init__(self, title=None,
                 win_width=800, win_height=800,
                 cell_width=40, cell_height=25,
                 print_cells=False
                 ):
        """ Setup display
        :title: title for display(s)
                If title is present and ends with "-"
                descriptive suffixes are generated for the
                different output
                default: Descriptive title(s) are generated
        :win_width: display window width in pixels
                    default: 800
        :win_height: display window height in pixels
                    default: 800
        :cell_width: braille width in cells
                    default: 40
        :cell_height: braille width in cells
                    default: 25
        :print_cells: print cells in formatted way
                    default: False - no print
        """
        self.title = title
        self.win_width = win_width
        self.win_height = win_height
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.print_cells = print_cells
        bd = TurtleLittleDisplay(win_width=self.win_width,
                            win_height=self.win_height,
                            grid_width=self.cell_width,
                            grid_height=self.cell_height)
        self.bd = bd 

    def filling(self):
        return self.bd.filling()

    def begin_fill(self):
        return self.bd.begin_fill()

    def end_fill(self):
        return self.bd.end_fill()
        
    def dot(self, size=None, *color):
        return self.bd.dot(size, *color)
                        
    def forward(self, length):
        return self.bd.forward(length)
    def fd(self, length):
        return self.forward(length)

    def goto(self, x, y=None):
        return self.bd.goto(x, y=y)
    def setpos(self, x, y=None):
        return self.goto(x, y=None)
    def setposition(self, x,  y=None):
        return self.goto(x, y=None)
        
    def backward(self, length):
        return self.bd.backward(length)                
    def bk(self, length):
        return self.backward(length)    
    def back(self, length):
        return self.backward(length)
    
    def right(self, angle):
        return self.bd.right(angle)
    def rt(self, angle):
        return self.right(angle)

    def pendown(self):
        return self.bd.pendown()

    def penup(self):
        return self.bd.penup()
        
    def speed(self, speed):
        return self.bd.speed(speed)    

    def left(self, angle):
        return self.bd.left(angle)

    def lt(self, angle):
        return self.bd.left(angle)

    def color(self, *args):
        return self.bd.color(*args)

    def pensize(self, width=None):
        return self.bd.pensize(width=width)
    def width(self, width=None):
        return self.pensize(width=width)

    def braille_draw(self, title=None):
        """ Draw steps in braille
            1. create screen with drawing
            2. create braille output
        """
        self.bd.display()
        

        
    def mainloop(self):
        title = self.title
        if title is None:
            title = "Grid Display -"
        self.bd.display(title=title,
                   print_cells=self.print_cells)
        self.bd.mainloop()        

    def done(self):
        return self.mainloop()
    

"""
External functions 
Some day may model after turtle's _make_global_funcs
"""
tum = TurtleLittle()


def backward(length):
    return tum.backward(length)

def color(*args):
    return tum.color(*args)

def dot(size=None, *color):
    return tum.dot(size, *color)

def filling():
    return tum.filling()

def begin_fill():
    return tum.begin_fill()

def end_fill():
    return tum.end_fill()

def forward(length):
    return tum.forward(length)

def goto(x, y=None):
    return tum.goto(x, y=y)
def setpos(x, y=None):
    return tum.setpos(x, y=y) 
def setposition(x, y=None):
    return tum.setposition(x, y=y) 

def left(angle):
    return tum.left(angle)

def pendown():
    return tum.pendown()

def penup():
    return tum.penup()

def right(angle):
    return tum.right(angle)

def speed(speed):
    return tum.speed(speed)

def mainloop():
    return tum.mainloop()
def done():
    return tum.done()

def pensize(width=None):
    return tum.pensize(width)
def width(width=None):
    return tum.pensize(width)

if __name__ == '__main__':
    #from turtle_braille import *    # Get graphics stuff
    #tum.points_window = True
    #tum.print_cells = True
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
            
