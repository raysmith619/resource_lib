# dm_circle.py    26Feb2021  crs  drawing objects
"""
Circle marker
"""
from tkinter import *

from select_trace import SlTrace

from dm_marker import DmMarker

""" Support for circle marker turtle style
"""
class DmCircle(DmMarker):    
    def __init__(self, drawer, **kwargs
                  ):
        """ Setup basic marker state
        :drawer: drawing control
        :kwargs: basic DmMarker args
        """
        super().__init__(drawer, draw_type=super().DT_CIRCLE, **kwargs)

    def __str__(self):
        return super().__str__()

    def draw(self):
        """ Draw circle
        """
        super().draw()      # Ground work
        self.add_circle()
    
    def add_circle(self, x1=None, y1=None,
                     length=None, heading=None,
                     color=None, width=None,
                     **kwargs):
        """ Add circle turtle style
        Note: create_oval does not support rotation.
            TBD: Create circle as a polygon then rotate
            points based on heading.
            
        :x1: x origin coordinate default: self.x_cor
        :y1: y origin coordinate default: self.y_cor
        :length: length of line default: self.side (diameter)
        :color: line color default: from kwargs['fill'], else self.color
        :width: line width default: from kwargs['width'], else self.line_width
        :heading: heading in deg default: self.heading (of bounding box)
        :kwargs: additional parameters
                defaults: color - self.color, else black
                        width - self.line_width, else 1
        """
        corners = self.get_square(x1=x1, y1=y1,
                     length=length, heading=heading)
        ptxy = []
        for x,y in corners:
            ptxy.extend([x,y])
        ###self.create_polygon(*ptxy, width=1, fill="", outline="red")    # TFD - bounding box 
        sq_x0, sq_y0 = corners[3]
        sq_x1, sq_y1 = corners[1]
        cx, cy = (sq_x0+sq_x1)/2, (sq_y0+sq_y1)/2
        radius = self.side/2
        ov_x0 = cx-radius
        ov_y0 = cy+radius
        ov_x1 = cx+radius
        ov_y1 = cy-radius
        self.args_to_kwargs(color=color, width=width, dkwargs=kwargs)
        kwargs["fill"] = ""     # Over ride inside
        if "outline" not in kwargs:
            kwargs["outline"] = self.color
        self.create_oval(ov_x0, ov_y0, ov_x1, ov_y1, **kwargs)
        SlTrace.lg(f"create_oval: {ov_x0:.0f}, {ov_y0:.0f},"
                   f" {ov_x1:.0f}, {ov_y1:.0f}, {kwargs}", "draw_action")

if __name__ == "__main__":
    from dm_drawer import DmDrawer
    
    root = Tk()
    
    drawer = DmDrawer(root)
    drawer.color_current = "w"
    
    ncircle = 8
    ncircle = 7
    colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
    dms = []
    
    dm_base = DmCircle(drawer, heading=0, color="pink", line_width=20,
                     side=200)
    beg=3
    for i in range(beg, beg+ncircle):
        ang =  i*360/ncircle
        icolor = i % len(colors)
        color = colors[icolor]   
        dm = dm_base.change(heading=ang, color=color, line_width=(i+1)*2,
                     side=(i+1)*20)
        dms.append(dm)
        
    for dm in dms:
        SlTrace.lg(f"\ndm:{dm}")
        dm.draw() 
    
    mainloop()       
