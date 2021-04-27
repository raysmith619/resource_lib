# dm_square.py    26Feb2021  crs  drawing objects
"""
Square marker
"""
from tkinter import *

from select_trace import SlTrace

from dm_marker import DmMarker

""" Support for square marker turtle style
"""
class DmSquare(DmMarker):    
    def __init__(self, drawer, **kwargs
                  ):
        """ Setup basic marker state
        :drawer: drawing control
        :kwargs: basic DmMarker args
        """
        super().__init__(drawer, draw_type=super().DT_SQUARE, **kwargs)

    def __str__(self):
        return super().__str__()

    def draw(self):
        """ Draw square
        """
        super().draw()      # Ground work
        self.add_square()

if __name__ == "__main__":
    from dm_drawer import DmDrawer
    
    root = Tk()
    
    drawer = DmDrawer(root)
    nsquare = 8
    nsquare = 7
    colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
    dms = []
    
    dm_base = DmSquare(drawer, heading=0, color="pink", line_width=20,
                     side=200)
    beg=0
    for i in range(beg, beg+nsquare):
        ang =  i*360/nsquare
        icolor = i % len(colors)
        color = colors[icolor]   
        dm = dm_base.change(heading=ang, color=color, line_width=(i+1)*2,
                     side=(i+1)*20)
        dms.append(dm)
        
    for dm in dms:
        SlTrace.lg(f"\ndm:{dm}")
        dm.draw() 
    
    mainloop()       
