#turtle_braille_old.py    16Apr2022  crs  Author
"""
Turtle augmented with braille graphics output
turtle commands create Turtle output plus approximate braille
output
"""

from select_trace import SlTrace
SlTrace.clearFlags()
from braille_display import BrailleDisplay
    
class TurtleBraille():
    """ Parallel braille graphics output which attemps to aid
    blind people "see" simple graphics turtle output
    """
    def __init__(self, title=None,
                 win_width=800, win_height=800,
                 cell_width=40, cell_height=25,
                 braille_window=True,
                 braille_print=True,
                 points_window=False,
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
        :braille_window: display a braille window
                    default: True
        :braille_print: print display braille to output
                    default: True
        :points_window: display window showing where
                        display points were found/calculated
                    default: False
        :print_cells: print cells in formatted way
                    default: False - no print
        """
        self.title = title
        self.win_width = win_width
        self.win_height = win_height
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.braille_window = braille_window
        self.braille_print = braille_print
        self.points_window = points_window
        self.print_cells = print_cells
        bd = BrailleDisplay(win_width=self.win_width,
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
    
    def circle(self, radius, extent=None, steps=None):
        return self.bd.circle(radius, extent=extent, steps=steps)

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

    # screen functions
    
    def screensize(self, canvwidth=None, canvheight=None, bg=None):
        return self.bd.screensize(canvwidth=canvwidth,
                              canvheight=canvheight, bg=bg)

    def braille_draw(self, title=None):
        """ Draw steps in braille
            1. create screen with drawing
            2. create braille output
        """
        self.bd.display()

        
    def mainloop(self):
        title = self.title
        if title is None:
            title = "Braille Display -"
        self.bd.display(title=title,
                   braille_window=self.braille_window,
                   points_window=self.points_window,
                   braille_print=self.braille_print,
                   print_cells=self.print_cells)
        self.bd.mainloop()        
    def done(self):
        return self.mainloop()

    ### special functions
    def set_blank(self, blank_char):
        """ Set blank replacement
        :blank_char: blank replacement char
        :returns: previous blank char
        """
        return self.bd.set_blank(blank_char)


"""
External functions 
Some day may model after turtle's _make_global_funcs
"""
tum = TurtleBraille()


def backward(length):
    return tum.backward(length)

def color(*args):
    return tum.color(*args)
    
def circle(self, radius, extent=None, steps=None):
    return tum.circle(radius, extent=extent, steps=steps)

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

def screensize(canvwidth=None, canvheight=None, bg=None):
    return tum.screensize(canvwidth=canvwidth,
                          canvheight=canvheight, bg=bg)
### special functions
def set_blank(blank_char):
    """ Set blank replacement
    :blank_char: blank replacement char
    :returns: previous blank char
    """
    ret = tum.set_blank(blank_char)
    return ret

"""
Screen size function to facilitate general
possitioning
"""
def x_min():
    return tum.bd.x_min

def x_max():
    return tum.bd.x_max
def y_min():
    return tum.bd.y_min

def y_max():
    return tum.bd.y_max


    
if __name__ == '__main__':
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
            
