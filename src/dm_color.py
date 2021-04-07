# dm_color.py    18Mar2021  crs  drawing objects
"""
General move
"""
from tkinter import *

from select_trace import SlTrace

from dm_marker import DmMarker

""" Support for Color set/change
"""
class DmColor(DmMarker):    
    def __init__(self, drawer, draw_type=DmMarker.DT_COLOR, **kwargs
                  ):
        """ Setup basic marker state
        :drawer: drawing control
        :kwargs: basic DmMarker args
        """
        super().__init__(drawer, draw_type=draw_type, **kwargs)

    def __str__(self):
        str_str = self.__class__.__name__
        return str_str

    def draw(self):
        """ Set color
        """
        self.drawer.set_color(self.color)

if __name__ == "__main__":
    root = Tk()
 