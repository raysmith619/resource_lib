# dm_pen.py    18Mar2021  crs  drawing objects
"""
General move
"""
from tkinter import *

from select_trace import SlTrace

from dm_marker import DmMarker

""" Support for pen set/change
"""
class DmPen(DmMarker):
        
    def __init__(self, drawer, draw_type=DmMarker.DT_PEN,
                 pen_desc="down", **kwargs
                  ):
        """ Setup basic state
        :drawer: drawing control
        :kwargs: basic DmMarker args
        """
        super().__init__(drawer, draw_type=draw_type, **kwargs)
        self.pen_desc = pen_desc

    def __str__(self):
        str_str = self.__class__.__name__
        str_str += f"_{self.pen_desc}" 
        return str_str

    def is_visible(self):
        """ Return True if this is a "visible" marker
        suitable for duplicating/repeating
        OVERRIDDEN if not a visible marker
        """
        return False 

    def draw(self):
        """ Set color
        """
        self.drawer.set_pen(self.pen_desc)

if __name__ == "__main__":
    root = Tk()
 