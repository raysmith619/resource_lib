# dm_heading.py    22Mar2021  crs  drawing objects
"""
Heading marker
"""
from tkinter import *

from select_trace import SlTrace

from dm_marker import DmMarker

""" Support for Heading marker
"""
class DmHeading(DmMarker):    
    def __init__(self, drawer,
                **kwargs
                  ):
        """ Setup heading
        :drawer: drawing control
        :kwargs: basic DmMarker args
        """
        super().__init__(drawer, draw_type=super().DT_HEADING, **kwargs)
        
    def __str__(self):
        return super().__str__()

    def get_next_loc(self):
        """ Get next location  - unchanged
        """
        return self.get_loc()
    def draw(self):
        """ Draw line
        """
        self.drawer.set_heading(self.heading)
