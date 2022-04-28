#turtle_braille.py    16Apr2022  crs  Author
"""
Turtle augmented with braille graphics output
turtle commands create Turtle output plus approximate braille
output
"""
from math import sin, cos, pi, fmod
import turtle as tu

from select_trace import SlTrace
from braille_display import BrailleDisplay
SlTrace.lg("braille_display")
SlTrace.clearFlags()

class TurtleStep:
    def __init__(self, tb,
                 cmd=None, colors=None, length=None,
                 angle=None,
                 x=None, y=None,
                 size=None,
                 init=False):
        """ Do turtle step for braille display
        :tb: TurtleBraille to use
        :cmd: command
        :colors: turtle color arg
        :length: length
        :angle: angle if one
        Current settings, not usually set
        :x: current x location
        :y: current y location
        :init: initialize with out ref to tb
        """
        if init:
            self.tb = tb
            self.cmd = cmd
            self.colors = colors
            self.length = length
            self.angle = angle
            self.x = x
            self.y = y
            self.size = size 
            return 
        
        self.tb = tb 
        tstp = self.tstp = tb.tstp # local copy
        self.cmd = cmd
        if colors is None:
            colors = tstp.colors
        self.colors = colors
        tstp.colors = colors
        self.length = length
        self.angle = angle
        self.size = size
        if x is not None:
            tstp.x = x
        if y is not None:
            tstp.y = y
        if angle is not None:
            tstp.angle = angle

    def do_step(self):
        """ Execute turtle step
        """
        if self.cmd == "color":
            self.color(colors=self.colors)
        elif self.cmd == "forward":
            self.forward(length=self.length)
        elif self.cmd == "backward":
            self.backward(length=self.length)
        elif self.cmd == "right":
            self.right(angle=self.angle)
        elif self.cmd == "left":
            self.left(angle=self.angle)
        elif self.cmd == "dot":
            self.dot(size=self.size)
        else:
            SlTrace.lg(f"Command {self.cmd} is not yet implemented")
    
    """ step commands
    """
    def color(self, colors):
        """ Make color
        """
        self.tb.bd.add_color(colors=colors)

    def dot(self, size):
        """ Make dot
        :size: of dot
        """
        self.tb.bd.add_dot(size=size)
        
                
    def forward(self, length):
        """ Make step forward, updating location
        """
        tstp = self.tstp
        x1 = tstp.x
        y1 = tstp.y
        angle = tstp.angle
        rangle = angle/180*pi
        x2 = x1 + length*cos(rangle)
        y2 = y1 + length*sin(rangle)
        self.tb.bd.add_line(p1=(x1,y1), p2=(x2,y2))
        tstp.x = x2
        tstp.y = y2

    
    def backward(self, length):
        """ Make step backward, updating location
        """
        self.forward(length=-length)

    
    def left(self, angle):
        """ Turtle left
        """
        angle = fmod(self.tstp.angle + angle, 360)
        self.tstp.angle = angle

    
    def right(self, angle):
        """ Turtle right
        """
        angle = fmod(self.tstp.angle - angle, 360)
        self.tstp.angle = angle
            
            
    def __str__(self):
        st = f"{self.cmd}"
        if self.colors is not None:
            st += f"{self.colors}"
        if self.length is not None:
            st +=  f" length:{self.length}"
        if self.angle is not None:
            st += f" angle:{self.angle}"
        return st    
    
class TurtleBraille():
    """ Parallel braille graphics output which attemps to aid
    blind people "see" simple graphics turtle output
    """
    def __init__(self, win_width=800, win_height=800,
                 cell_width=40, cell_height=25):
        """ Setup display
        :win_width: display window width in pixels
            default: 800
        :win_height: display window height in pixels
            default: 800
        :cell_width: braille width in cells
            default: 40
        :cell_height: braille width in cells
            default: 25
        """
        
        self.win_width = win_width
        self.win_height = win_height
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.tu = tu.Turtle()
        self.screen = tu.Screen()
        self.steps = []
        self.tstp = TurtleStep(tb=self, init=True,
                    colors="black",
                    angle=0,
                    x=0, y=0)
        bd = BrailleDisplay(win_width= self.win_width,
                            win_height=self.win_height,
                            cell_width=self.cell_width,
                            cell_height=self.cell_height)
        self.bd = bd 
        
    def prev_step(self):
        """ previous step, if one, else default step
        :returns: previous step, if one, else default
        """
        st = TurtleStep(self)
        return st

    def dot(self, size=None, colors=None):
        step = self.prev_step()
        step.cmd = "dot"
        step.size = size
        step.colors = colors
        self.steps.append(step)
        self.tu.dot(size)
                        
    def forward(self, length):
        step = self.prev_step()
        step.cmd = "forward"
        step.length = length
        self.steps.append(step)
        self.tu.forward(length)

    def fd(self, length):
        return self.forward(length)

    def backward(self, length):
        step = self.prev_step()
        step.cmd = "backward"
        step.length = length
        self.steps.append(step)
        self.tu.backward(length)
                
    def bk(self, length):
        return self.backward(length)
    
    def back(self, length):
        return self.backward(length)
    
    def right(self, angle):
        step = self.prev_step()
        step.cmd = "right"
        step.angle = angle
        step.length = None
        self.steps.append(step)
        self.tu.right(angle)

    def rt(self, angle):
        return self.right(angle)
    
    def left(self, angle):
        step = self.prev_step()
        step.cmd = "left"
        step.heading = angle + step.heading
        step.length = 0
        self.steps.append(step)
        self.tu.left(angle)

    def lt(self, angle):
        return self.left(angle)

    def color(self, colors):
        step = self.prev_step()
        step.cmd = "color"
        step.colors = colors
        self.steps.append(step)
        self.tu.color(colors)
    
    def mainloop(self):
        """ For now, just list steps 
        """
        nstep = 0
        for step in self.steps:
            nstep += 1
            print(f"{nstep:3}: {step}")
        self.done()

    def list_steps(self):
        """ List steps
        """
        ns = 0
        for step in self.steps:
            ns += 1
            print(f"{ns:3}: {step}")

    def braille_draw(self):
        """ Draw steps in braille
            1. create screen with drawing
            2. create braille output
        """
        for step in self.steps:
            step.do_step()
        self.bd.braille_display()
        if SlTrace.trace("cell"):
            self.bd.print_cells()
        SlTrace.lg("Graphics Printout")
        self.bd.braille_print()
        

        
    def done(self):
        if SlTrace.trace("steps"):
            self.list_steps()
        self.braille_draw()
        self.screen.mainloop()

"""
External functions 
Some day may model after turtle's _make_global_funcs
"""
tum = TurtleBraille()

def forward(length):
    return tum.forward(length)

def backward(length):
    return tum.backward(length)

def dot(size=None, color=None):
    return tum.dot(size, color)

def right(angle):
    return tum.right(angle)

def left(angle):
    return tum.left(angle)

def color(color):
    return tum.color(color)

def done():
    return tum.done()
        
if __name__ == '__main__':
    #from turtle_braille import *    # Get graphics stuff
    
    color("green")
    forward(200)
    right(90)
    forward(200)
    right(90)
    forward(200)
    right(90)
    forward(200)
    done()    
            