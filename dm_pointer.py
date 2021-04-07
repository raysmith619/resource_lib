# dm_pointer.py    27Feb2021  crs  drawing objects
"""
Line marker
"""
from tkinter import *

from select_trace import SlTrace

from dm_marker import DmMarker

""" Support for line marker
"""
class DmPointer(DmMarker):    
    def __init__(self, drawer, plen=None,
                **kwargs
                  ):
        """ Setup pointer (marker showing current point,direction)
        :drawer: drawing control
        :plen: pointer line length
            default=5
        :kwargs: basic DmMarker args
        """
        super().__init__(drawer, draw_type=super().DT_POINTER, **kwargs)
        if plen is None:
            plen = self.line_width
            if self.line_width > 2:
                self.line_width = self.line_width/2
        self.plen = plen
        
    def __str__(self):
        return super().__str__()

    def draw(self):
        """ Draw line
        """
        # Use square as basis, pointer bysects square
        # from center of left vertical to center
        corners = self.get_square(x1=self.x_cor, y1=self.y_cor,
                     color=self.color, width=self.side)
        x1 = (corners[0][0] + corners[3][0])/2
        y1 = (corners[0][1] + corners[3][1])/2
        x2 = (corners[0][0] + corners[1][0]
               + corners[2][0] + corners[3][0])/4
        y2 = (corners[0][1] + corners[1][1]
               + corners[2][1] + corners[3][1])/4
        _,_,_,_,k2args = self.to_line_args()
        self.create_line(x1,y1,x2,y2, arrow=LAST, **k2args)
        

if __name__ == "__main__":
    
    from dm_drawer import DmDrawer
    
    root = Tk()
    
    drawer = DmDrawer(root)
    nsquare = 8
    nsquare = 7
    colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
    dms = []
    side = 100
    beg=0
    extent = side*nsquare
    x_beg = -extent/2
    y_beg = x_beg
    for i in range(beg, beg+nsquare):
        ang =  i*360/nsquare
        icolor = i % len(colors)
        color = colors[icolor]
        dm = DmPointer(drawer, heading=ang, color=color,
                            x_cor=x_beg+i*side,
                            y_cor=y_beg+i*side,
                            )
        dms.append(dm)
        
    for dm in dms:
        SlTrace.lg(f"\ndm:{dm}")
        dm.draw() 
    
    mainloop()       
