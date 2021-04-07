# dm_size.py    10Mar2021  crs  drawing objects
"""
General move
"""
from tkinter import *

from select_trace import SlTrace

from dm_marker import DmMarker, tp

""" Support for line marker
"""
class DmSize(DmMarker):    
        
    def __init__(self, drawer, draw_type=DmMarker.DT_SIZE,
                 **kwargs
                  ):
        """ Setup basic state
        :drawer: drawing control
        :kwargs: basic DmMarker args
        """
        super().__init__(drawer, draw_type=draw_type, **kwargs)

    def __str__(self):
        str_str = self.__class__.__name__
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
        self.drawer.set_size(side=self.side,
                                 line_width=self.line_width)

if __name__ == "__main__":
    root = Tk()
 