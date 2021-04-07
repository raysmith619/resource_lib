# dm_line.py    26Feb2021  crs  drawing objects
"""
Line marker
"""
from tkinter import *

from select_trace import SlTrace

from dm_marker import DmMarker

""" Support for line marker
"""
class DmLine(DmMarker):    
    def __init__(self, drawer, **kwargs
                  ):
        """ Setup basic marker state
        :drawer: drawing control
        :kwargs: basic DmMarker args
        """
        super().__init__(drawer, draw_type=super().DT_LINE, **kwargs)

    def __str__(self):
        return super().__str__()

    def draw(self):
        """ Draw line
        """
        super().draw()      # Ground work
        self.add_line()

if __name__ == "__main__":
    from dm_drawer import DmDrawer
    
    root = Tk()
    
    drawer = DmDrawer(root)
    nline = 8
    colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
    dmls = []
    
    dml_base = DmLine(drawer, heading=0, color="pink", line_width=20,
                     side=200)
    
    for i in range(0, nline):
        ang =  i*360/nline
        icolor = i % len(colors)
        color = colors[icolor]   
        dml = dml_base.change(heading=ang, color=color, line_width=(i+1)*2,
                     side=(i+1)*20)
        dmls.append(dml)
        
    for dml in dmls:
        SlTrace.lg(f"dml:{dml}")
        dml.draw() 
    
    mainloop()       
