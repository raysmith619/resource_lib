# random_shapes.py    15Nov2022  crs, Author
"""
Simple shapes program to exercise Braille Window 
with audio feedback
"""
import random

from turtle_braille_link import *        # Set link to library
from Lib.pickle import NONE

min_x = x_min()
max_x = x_max()
min_y = y_min()
max_y = y_max()

print(f"min_x={min_x} max_x={max_x}")
print(f"min_y={min_y} max_x={max_y}")

class DEFT:
    def __init__(self):
        self.name = None
        self.x = None 
        self.y = None 
        self.length = None
        self.width = None 
        self.height = None 
        self.color = None
        self.thick = None 
        self.fill = None 
    
class DrawShape:
    color_index = None
    
    def __init__(self, name=None, x=None,  y=None,
                    length=None,
                    width=None, height=None,
                    color=None,
                    thick=2,
                    fill=None):
        """ Draw simple shape
        :name: shape name default: generated
        :x: x-coordinate of center default: generated
        :y: y-coordinate of center default: generated 
        :width: width default: generated
        :height: width default: width 
        :color: color default: generated
        :thick: thickness of line default: 2 
        :fill: figure filled default: generated
        """
        self.deft = deft = DEFT()
        deft.name = name
        deft.x = x 
        deft.y = y 
        deft.length = length
        deft.width = width 
        deft.height = height 
        deft.color = color
        deft.thick = thick 
        deft.fill = fill 

        self.colors = [
            "red", "orange", "yellow",
            "green", "blue", "indigo",
            "violet",
            ]
        self.color_index = 0

        self.figures = {
            "square" : self.do_square,
             "circle" : self.do_circle,
             "triangle" : self.do_triangle,
            }
        
    def draw(self, name=None, x=None,  y=None,
                    length = None,
                    width=None, height=None,
                    color=None,
                    thick=None,
                    fill=False):
        """ Draw simple shape
            defaults use privious value or defaults
        :name: shape name default: generated
        :x: x-coordinate default: generated
        :y: y-coordinate default: generated 
        :width: width default: generated
        :length: generic length
        :height: width default: width 
        :color: color default: generated
        :thick: line width default: previous else 2 
        :fill: filled default: False - not filled
        """
        deft = self.deft
        self.name = deft.name = self.gen_name(name)
        self.length = self.gen_len(length)
        self.width = self.gen_len(width)
        self.height = self.gen_len(height)
        self.x = self.gen_pos(x)
        self.y = self.gen_pos(y) 
        self.color = self.gen_color(color)
        self.thick = deft.thick = self.gen_thick(thick)
        self.fill = deft.fill = self.gen_fill(fill)
        name = self.name
        if name not in self.figures:
            print(f"{name} is not our figure")
            return
        
        fg_draw = self.figures[name]
        fg_draw()

    def gen_name(self, name=None):
        if name is None:
            name = self.name
        if name is None:
            names = list(self.figures)
            name = random.choice(names)
        return name
    
    def gen_pos(self, pos=None):
        """ Generate position
            away from edges 
        :pos: given Position
        """
        if pos is None:
            max_pos = min(max_x,max_y)
            min_pos = max(min_x,min_y)
            buffer = max(self.width//2, self.height//2)
            pos = random.uniform(min_pos+buffer,
                                 max_pos-buffer)
        return pos
    
    def gen_len(self, length=None):
        """ Generate length
            fitting in  
        :length: given length
        """
        if length is None:
            length = self.deft.length
        if length is None:
            length = min((max_x-min_x), (max_y-min_y))
            min_len = .2*length
            max_len = .4*length
            length = random.uniform(min_len, max_len)
        return length

    def gen_color(self, color=None):
        """ Generate color
        :color: figure color default: circlate colors
        """
        if color is None:
            color = self.deft.color
        if color is None:
            color = self.colors[self.color_index
                                %len(self.colors)]
            self.color_index += 1
        return color

    def gen_thick(self, thick=None):
        if thick is None:
            thick = self.deft.thick
        if thick is None: 
            thick = 2
        return thick
    
    def gen_fill(self, fill=None):
        """ Gen figure fill
        :fill: figure fill default: previous fill else random
        """
        if fill is None:
            fill = self.deft.fill
        if fill is None:
            fill = random.choice([True,False])
        return fill
    
    """
    Our builtin drawings
    """
    def do_square(self):
        """ Draw square
        """
        x_start = self.x - self.width/2
        y_start = self.y - self.height/2
        penup()
        color(self.color)
        goto(x_start,y_start)
        width(self.thick)
        pendown()
        for i in range(4):
            forward(self.width)
            left(90)
   
    def do_circle(self):
        """ Draw square
        """
        x_start = self.x
        y_start = self.y
        penup()
        goto(x_start, y_start)
        color(self.color)
        pendown()
        dot(size=self.length)
        penup()
   
    def do_triangle(self):
        """ Draw square
        """
        x_start = self.x - self.width/2
        y_start = self.y - self.height/2
        penup()
        goto(x_start, y_start)
        x2 = x_start + self.width
        y2 = y_start
        x3 = (x_start+x2)/2
        y3 = y_start+self.height
        pensize(self.thick)
        pendown()
        if self.fill:
            begin_fill()
        goto(x2, y2)
        goto(x3, y3)
        goto(x_start,y_start)   # end at beginning
        if self.fill:
            end_fill()
   
ds = DrawShape()
ds.draw("square")
ds.draw("circle")
ds.draw("triangle")
done()
             