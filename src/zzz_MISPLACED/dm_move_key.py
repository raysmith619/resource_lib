# dm_move_key.py    10Mar2021  crs  drawing objects
"""
General move
"""
from tkinter import *

from select_trace import SlTrace
from select_error import SelectError

from dm_move import DmMove

""" Support for moves based on keys
"""
class DmMoveKey(DmMove):    
    def __init__(self, drawer, draw_type=DmMove.DT_MOVE_KEY,
                 keysym=None, **kwargs
                  ):
        """ Setup basic marker state
        :drawer: drawing control
        :kwargs: basic DmMarker args
        """
        super().__init__(drawer, draw_type=draw_type, **kwargs)
        self.keysym = keysym
        if self.keysym == "Up":
            self.heading=90
        elif self.keysym == "Down":
            self.heading=270
        elif self.keysym == "Left":
            self.heading=180
        elif self.keysym == "Right":
            self.heading=0
        else:
            raise SelectError(f"Unhandled keysym:{self.keysym}")

    def __str__(self):
        str_str = self.__class__.__name__
        str_str += f" {self.keysym}"
        str_str += f" {super().__str__()}"
        return str_str

    def draw(self):
        """ Move
        """
        self.add_move()

if __name__ == "__main__":
    root = Tk()
 