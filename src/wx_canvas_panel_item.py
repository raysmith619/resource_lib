# wx_canvas_panel_item.py   29Nov2023  crs, split off
"""
CanvasPanel item which is used to create/recreate display
"""
import wx

from select_trace import SlTrace


def wx_Point(x, y):
    """ Force int args
    :x: x value
    :y: y value
    :returns: wx_Point
    """
    return wx.Point(int(x), int(y))
   
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
        
        if self.canv_type == "create_rectangle":
            self.points = [wx_Point(args[0],args[1]),
                           wx_Point(args[2],args[3])]
        elif self.canv_type == "create_oval":
            self.points = [wx_Point(args[0],args[1]),
                           wx_Point(args[2],args[3])]
        elif self.canv_type == "create_line":
            points = []
            it_args = iter(self.args)
            for arg in it_args:
                if arg is tuple:
                    x,y = arg
                else:
                    x,y = arg,next(it_args)
                pt = wx_Point(x,y)
                points.append(pt)
            self.points = points
        elif self.canv_type == "create_text":
            self.points = [wx_Point(args[0],args[1])]
        else:
            raise Exception(f"draw: unrecognized type: {self.canv_type}")

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
        if self.points is not None:
            st += f" points: {self.points}"
        return st
        

    def draw(self, points=None):
        """ Draw canvas item
        scaled drawings if points is not None
        
        :points: characterizing points for figure
                default: self.points (initialized points)
        """
        if self.deleted:
            return      # Already deleted
        
        if points is None:
            points = self.points
            
        panel = self.canvas_panel
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
            ret = self.create_rectangle_draw(points)
        elif self.canv_type == "create_oval":
            ret = self.create_oval_draw(points)
        elif self.canv_type == "create_line":
            ret = self.create_line_draw(points)
        elif self.canv_type == "create_text":
            ret = self.create_text_draw(points)
        else:
            raise Exception(f"draw: unrecognized type: {self.canv_type}")
        
        return ret

    ###### create_rectangle    
    def create_rectangle_draw(self, points):
        """ Simulate tkinter canvas create_rectangle drawing
        """
        if points is None:
            points = self.points
        if len(points) < 2:
            return
            
        dc = wx.PaintDC(self.canvas_panel.grid_panel)
        dc.SetPen(wx.Pen(self.outline, style=wx.SOLID))
        dc.SetBrush(wx.Brush(self.fill, wx.SOLID))
        dc.DrawRectangle(wx.Rect(points[0], points[1]))
        SlTrace.lg(f"DrawRect: {points[0]},"
                   f"  {points[1]}", "draw_rect")

    ###### create_oval
    def create_oval_draw(self, points=None):
        """ Simulate tkinter canvas create_oval
        :points: wx.Point(x0,y0), wx.Point(x1,y1)
                default: self.points
        """
        if points is None:
            points = self.points
        if len(points) < 2:
            return
        dc = wx.PaintDC(self.canvas_panel.grid_panel)
        dc.SetPen(wx.Pen(self.outline, style=wx.SOLID))
        dc.SetBrush(wx.Brush(self.fill, wx.SOLID))
        dc.DrawEllipse(pt=points[0],
                size=wx.Size(points[1].x-points[0].x,
                            points[1].y-points[0].y))
        
    #### create_line
    def create_line_draw(self, points=None):
        """ Implement tkinter's create_line
        :args: x1,y1,...xn,yn
        :kwargs:  width=, fill=, tags=[]
        """
        if points is None:
            points = self.points
        if len(points) == 0:
            return      # empty list
        
        dc = wx.PaintDC(self.canvas_panel.grid_panel)
        dc.SetPen(wx.Pen(self.fill, style=wx.SOLID, width=self.width))
        dc.DrawLines(points)

    ####### create_text
    def create_text_draw(self, points=None):
        """ Simulate tkinter canvas create_text
        """
        if points is None:
            points = self.points
        if len(points) < 1:
            return
        
        if "font" not in self.kwargs:
            font = wx.Font(10, wx.ROMAN, wx.ITALIC, wx.NORMAL) 
        else:
            font = wx.Font(self.kwargs["font"])
            
        
        dc = wx.PaintDC(self.canvas_panel.grid_panel)
        dc.SetPen(wx.Pen(self.outline, style=wx.SOLID))
        dc.SetBrush(wx.Brush(self.fill, wx.SOLID))
        
        text = self.kwargs["text"]
        dc.SetFont(font)
        title_pt = points[0]
        dc.DrawText(text=text, pt=title_pt)
                
        
    def delete(self):
        """ delete item
        """
        self.deleted = True
    """
    ------------------------ link to canvas_panel
    """
    
    def get_screen_loc(self, panel_loc):
        return self.canvas_panel.get_screen_loc(panel_loc)    
