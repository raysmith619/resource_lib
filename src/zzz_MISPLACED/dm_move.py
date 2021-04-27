# dm_move.py    10Mar2021  crs  drawing objects
"""
General move
"""
from tkinter import *

from select_trace import SlTrace

from dm_marker import DmMarker, tp

""" Support for line marker
"""
class DmMove(DmMarker):    
    def __init__(self, drawer, draw_type=DmMarker.DT_MOVE, **kwargs
                  ):
        """ Setup basic marker state
        :drawer: drawing control
        :kwargs: basic DmMarker args
        """
        super().__init__(drawer, draw_type=draw_type, **kwargs)

    def __str__(self):
        str_str = self.__class__.__name__
        str_str += f" heading={self.heading:.1f}"
        str_str += f" x={self.x_cor:.0f} y={self.y_cor:.0f}"
        str_str += f" to={tp(self.get_next_loc())}"
        return str_str

    def is_visible(self):
        """ Return True if this is a "visible" marker
        suitable for duplicating/repeating
        OVERRIDDEN if not a visible marker
        """
        return False 

    def get_side(self):
        """ Always give default, don't change it
        """
        return self.drawer.get_side()
    
    def draw(self):
        """ Draw line
        """
        self.add_move()

if __name__ == "__main__":
    root = Tk()
 