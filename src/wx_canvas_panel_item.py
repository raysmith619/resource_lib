# wx_canvas_panel_item.py   29Nov2023  crs, split off
"""
CanvasPanel item which is used to create/recreate display
"""
import wx

from select_trace import SlTrace


def wx_Point(x, y=None):
    """ Force int args
    :x: x value
    :y: y value
    :returns: wx_Point
    """
    if y is None:
        return x
    
    return wx.Point(int(x), int(y))
   
class CanvasPanelItem:
    """ Item to display canvas panel item
    """
    CANV_ID = 0
    
    def __init__(self, canvas_panel,
                 canv_type,
                 *args,
                 desc = None, **kwargs):
        self.canvas_panel = canvas_panel
        CanvasPanelItem.CANV_ID += 1
        self.canv_id = CanvasPanelItem.CANV_ID
        self.canvas_panel.items_by_id[self.canv_id] = self
        self.canv_type = canv_type
        self.desc = desc
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
        elif self.canv_type == "create_cursor":
            self.points = [wx_Point(args[0],args[1]),
                           wx_Point(args[2],args[3])]
        elif self.canv_type == "create_composite":
            self.points = []
            self.comp_parts = []        # list of composite part items
            
        else:
            raise Exception(f"draw: unrecognized type: {self.canv_type}")

    def add(self, part):
        """ Add another composite part
        :part: id/CanvasPanelItem
        """
        if not isinstance(part, CanvasPanelItem):
            part = self.canvas_panel.items_by_id[part]
        self.points.extend(part.points)     # Accumulate points of components            
        self.comp_parts.append(part)
        
    def refresh(self):
        """ Set item to be redrawn
        """
        rect = self.bounding_rect()
        self.canvas_panel.refresh_rectangle(rect)
        
    def update(self, **kwargs):
        """ Change zero or more of items keyword values
        :**kwrgs: keyword  args to change
        """
        for kw in kwargs:
            self.kwargs[kw] = kwargs[kw]
            
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
        

    def draw(self, points=None, rect=None):
        """ Draw canvas item
        scaled drawings if points is not None
        
        :points: characterizing points for figure
                default: self.points (initialized points)
        :rect: limit drawing to those within this rectangle
                default: no limitation - draw item
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
        
        if self.canv_type == "create_composite":
            ret = self.create_composite_draw(points, rect=rect)
        elif self.canv_type == "create_rectangle":
            ret = self.create_rectangle_draw(points, rect=rect)
        elif self.canv_type == "create_oval":
            ret = self.create_oval_draw(points, rect=rect)
        elif self.canv_type == "create_line":
            ret = self.create_line_draw(points, rect=rect)
        elif self.canv_type == "create_text":
            ret = self.create_text_draw(points, rect=rect)
        elif self.canv_type == "create_cursor":
            ret = self.create_cursor_draw(points, rect=rect)
        else:
            raise Exception(f"draw: unrecognized type: {self.canv_type}")
        
        return ret

    def get_parts(self):
        """ Get parts (non composites), self if not composite
        :returns: list of composite parts
        """
        if self.canv_type != "create_composite":
            return [self]
        
        parts = []
        for part in self.comp_parts:
            parts.extend(part.get_parts())
        return parts
        
    def bounding_rect(self):
        """ Get item's bounding rectangle NOT FOR COMPOSITE
        :returns: wx.Rect bounding rectangle
        """
        if self.canv_type == "create_rectangle":
            brect = wx.Rect(self.points[0], self.points[1])
        elif self.canv_type == "create_oval":
            brect = wx.Rect(wx.Point(self.points[0].x,self.points[0].y),
                            wx.Point(self.points[1].x, self.points[1].y))
        elif self.canv_type == "create_line":
            brect = wx.Rect(self.points[0], self.points[1])
        elif self.canv_type == "create_text":
            if len(self.points) >= 2:
                brect = wx.Rect(self.points[0], self.points[1])
            elif len(self.points) == 1:
                brect = wx.Rect(self.points[0], self.points[0])
        elif self.canv_type == "create_cursor":
            brect = wx.Rect(wx.Point(self.points[0].x,self.points[0].y),
                            wx.Point(self.points[1].x, self.points[1].y))
        else:
            raise Exception(f"draw: unrecognized type: {self.canv_type}")
        return brect
         
    ###### create_composite    
    def create_composite_draw(self, points=None, rect=None):
        """ draw composite figure
        :points: accumulated points from all components
        :rect: rectangle if not overlapping don't draw
                default: always draw
        """
        if points is None:
            points = self.points
        if len(points) == 0:
            return      # empty list

        for part in self.comp_parts:
            part.draw(rect=rect)
         
    ###### create_rectangle    
    def create_rectangle_draw(self, points, rect=None):
        """ Simulate tkinter canvas create_rectangle drawing
        :points: points deternining figure
                default: use items points
        :rect: rectangle if not overlapping don't draw
                default: always draw
        """
        if points is None:
            points = self.points
        if len(points) < 2:
            return
        
        brect = wx.Rect(points[0], points[1])
        if rect is not None and not brect.Intersects(rect):
            return
             
        dc = wx.PaintDC(self.canvas_panel.grid_panel)
        dc.SetPen(wx.Pen(self.outline, style=wx.SOLID))
        dc.SetBrush(wx.Brush(self.fill, wx.SOLID))
        dc.DrawRectangle(brect)
        SlTrace.lg(f"DrawRect: {self.fill} {points[0]},"
                   f"  {points[1]}", "draw_rect")
        pass
    ###### create_oval
    def create_oval_draw(self, points=None, rect=None):
        """ Simulate tkinter canvas create_oval
        :points: wx.Point(x0,y0), wx.Point(x1,y1)
                default: self.points
        :rect: rectangle if not overlapping don't draw
                default: always draw
        """
        if points is None:
            points = self.points
        if len(points) < 2:
            return
        brect = wx.Rect(wx.Point(points[0].x,points[0].y), wx.Point(points[1].x,points[1].y))
        if rect is not None and not brect.Intersects(rect):
            return
        
        dc = wx.PaintDC(self.canvas_panel.grid_panel)
        dc.SetPen(wx.Pen(self.outline, style=wx.SOLID))
        dc.SetBrush(wx.Brush(self.fill, wx.SOLID))
        size=wx.Size(points[1].x-points[0].x,
                            points[1].y-points[0].y)
        dc.DrawEllipse(pt=points[0], size=size)
        SlTrace.lg(f"DrawElipse: {self.fill} {points[0]} {size}", "draw_oval")
        
    #### create_line
    def create_line_draw(self, points=None, rect=None):
        """ Implement tkinter's create_line
        :args: x1,y1,...xn,yn
        :kwargs:  width=, fill=, tags=[]
        :rect: rectangle if not overlapping don't draw TBD
                default: always draw
        """
        if points is None:
            points = self.points
        if len(points) == 0:
            return      # empty list
        
        dc = wx.PaintDC(self.canvas_panel.grid_panel)
        dc.SetPen(wx.Pen(self.fill, style=wx.SOLID, width=self.width))
        dc.DrawLines(points)

    ####### create_text
    def create_text_draw(self, points=None, rect=None):
        """ Simulate tkinter canvas create_text
        :rect: rectangle if not overlapping don't draw TBD
                default: always draw
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
                
    ###### create_cursor
    def create_cursor_draw(self, points=None, rect=None):
        """ Create cursor - oval create_oval
        :points: wx.Point(x0,y0), wx.Point(x1,y1)
                default: self.points
        :rect: rectangle if not overlapping don't draw
                default: always draw
        """
        if points is None:
            points = self.points
        if len(points) < 2:
            return
        brect = wx.Rect(wx.Point(points[0].x,points[0].y), wx.Point(points[1].x,points[1].y))
        if rect is not None and not brect.Intersects(rect):
            return
        
        dc = wx.PaintDC(self.canvas_panel.grid_panel)
        dc.SetPen(wx.Pen(self.outline, style=wx.SOLID))
        dc.SetBrush(wx.Brush(self.fill, wx.SOLID))
        size=wx.Size(points[1].x-points[0].x,
                            points[1].y-points[0].y)
        dc.DrawEllipse(pt=points[0], size=size)
        SlTrace.lg(f"DrawCursor: {self.fill} {points[0]} {size}", "draw_cursor")
        
        
    def delete(self):
        """ delete item
        """
        self.deleted = True
    """
    ------------------------ link to canvas_panel
    """
    
    def get_screen_loc(self, panel_loc):
        return self.canvas_panel.get_screen_loc(panel_loc)    
