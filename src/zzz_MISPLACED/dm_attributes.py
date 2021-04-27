# dm_attributes.py    20Mar2021  crs  drawing objects
"""
General move
"""
from tkinter import *

from select_trace import SlTrace

from dm_marker import DmMarker

""" Support for general attributes
"""
class DmAttributes(DmMarker):
    DT_ATTRIBUTES = "dt_attributes"    
    def __init__(self, drawer, draw_type=DT_ATTRIBUTES,
                 marker_type=None, shape_type=None,
                 copy_mode=None,
                 pen_desc=None,
                  **kwargs
                  ):
        """ Setup basic state
        :drawer: drawing control
        :marker_type: marker type:line, shape, image
        :shape_type: shape type: line, square, triangle, circle
        :copy_mode: copy/move mode : "copy" - add new copies marker
                                    "move" - move marker to destination
        :pen_desc: pen setting pen_down, pen_up
        :
        :kwargs: basic DmMarker args
        """
        super().__init__(drawer, draw_type=draw_type, **kwargs)
        self.marker_type = marker_type
        self.shape_type = shape_type
        self.pen_desc = pen_desc
        self.copy_mode = copy_mode
        
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
        if self.marker_type is not None:
            self.drawer.set_marker_type(self.marker_type)
        if self.shape_type is not None:
            self.drawer.set_shape_type(self.shape_type)

if __name__ == "__main__":
    root = Tk()
 