# wx_canvas_panel_item.py   29Nov2023  crs, split off
"""
CanvasPanel item which is used to create/recreate display
"""
import wx

from select_trace import SlTrace
   
class CanvasPanelItem:
    """ Item to display canvas panel item
    """
    def __init__(self, canvas_panel,
                 canv_type,
                 args=None, kwargs=None):
        self.canvas_panel = canvas_panel
        self.canv_id = canvas_panel.get_id()
        self.canv_type = canv_type
        self.deleted = False
        self.tags = set()
        if "tags" in kwargs:
            self.tags = set(kwargs["tags"])
        self.args = args
        self.kwargs = kwargs
        
    def __str__(self):
        st = "CanvasPanelItem:"
        st += f"[{self.canv_id}]"
        st += f"{self.canv_type}"
        if self.canvas_panel.orig_pos != (0,0):
            st += f" orig: {self.canvas_panel.orig_pos}"
        st += f" orig: {self.canvas_panel.orig_size}"
        if self.args:
            st += f" args: {self.args}"
        if self.kwargs:
            st += f" kwargs: {self.kwargs}"
        return st
        

    def draw(self):
        """ Draw canvas item
        """
        # Get current panal position and size
        # and calculate adjustments
        if self.deleted:
            return      # Already deleted
        
        panel = self.canvas_panel
        self.pos_adj = panel.cur_pos-panel.orig_pos
        self.orig_size = panel.orig_size
        self.cur_size = panel.cur_size
        self.size_factor = (self.cur_size.x/self.orig_size.x,
                                   self.cur_size.y/self.orig_size.y)

        self.fill = panel.color
        if "fill" in self.kwargs:
            self.fill = self.kwargs["fill"]

        self.outline = "black"        
        if "outline" in self.kwargs:
            self.outline = self.kwargs["outline"]
            
        self.width = 2
        if "width" in self.kwargs:
            self.width = self.kwargs["width"]

        if "tags" in self.kwargs:
            self.tags = self.kwargs["tags"]
        
        if self.canv_type == "create_rectangle":
            ret = self.create_rectangle_draw()
        elif self.canv_type == "create_oval":
            ret = self.create_oval_draw()
        elif self.canv_type == "create_line":
            ret = self.create_line_draw()
        else:
            raise Exception(f"draw: unrecognized type: {self.canv_type}")
        
        return ret
    
    def create_rectangle_draw(self):
        """ Simulate tkinter canvas create_rectangle drawing
        """
            
        cx1,cy1,cx2,cy2 = self.args
        cx1_adj = int(cx1 * self.size_factor[0])
        cx2_adj = int(cx2 * self.size_factor[0])
        cy1_adj = int(cy1 * self.size_factor[1])
        cy2_adj = int(cy2 * self.size_factor[1])
         
        dc = wx.PaintDC(self.canvas_panel.grid_panel)
        dc.SetPen(wx.Pen(self.outline, style=wx.SOLID))
        dc.SetBrush(wx.Brush(self.fill, wx.SOLID))
        dc.DrawRectangle(wx.Rect(wx.Point(cx1_adj,cy1_adj),
                                 wx.Point(cx2_adj,cy2_adj)))
        SlTrace.lg(f"DrawRect: {wx.Point(cx1_adj,cy1_adj)},"
                   f"  {wx.Point(cx2_adj,cy2_adj)}", "draw_rect")

    def create_oval_draw(self):
        """ Simulate tkinter canvas create_oval
        """
        x0,y0,x1,y1 = self.args
        x0_adj = int(x0 * self.size_factor[0])
        x1_adj = int(x1 * self.size_factor[0])
        y0_adj = int(y0 * self.size_factor[1])
        y1_adj = int(y1 * self.size_factor[1])
        
        
        
        dc = wx.PaintDC(self.canvas_panel.grid_panel)
        dc.SetPen(wx.Pen(self.outline, style=wx.SOLID))
        dc.SetBrush(wx.Brush(self.fill, wx.SOLID))
        dc.DrawEllipse(x=x0_adj, y=y0_adj, width=x1_adj-x0_adj, height=y1_adj-y0_adj)
        

    def create_line_draw(self):
        """ Implement tkinter's create_line
        :args: x1,y1,...xn,yn
        :kwargs:  width=, fill=, tags=[]
        """
        if len(self.args) == 0:
            return      # empty list
        
        dc = wx.PaintDC(self.canvas_panel.grid_panel)
        dc.SetPen(wx.Pen(self.fill, style=wx.SOLID, width=self.width))
        points = []
        it_args = iter(self.args)
        for arg in it_args:
            if arg is tuple:
                x,y = arg
            else:
                x,y = arg,next(it_args)
            x_adj = int(x * self.size_factor[0])
            y_adj = int(y * self.size_factor[1])
            points.append(wx.Point(x_adj,y_adj))
        dc.DrawLines(points)
        
    def delete(self):
        """ delete item
        """
        self.deleted = True    
            
