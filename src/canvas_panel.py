# canvas_panel.py 08Nov2023  crs
"""
Support for very limited list of tkinter Canvas type actions
on wxPython Panel  Our attempt here was to ease a port
from tkinter Canvas use to wxPython.
"""
import wx

from select_trace import SlTrace 

class Modified_Region:
    """ Modified region original attriburtes
    """
    def __init__(self, master, pos, size, color, style):
        self.master = master
        self.pos = pos
        self.size = size
        self.color = color
        self.style = style
        
    def restore(self):
        """ Restore region """
        dc = wx.PaintDC(self.master)
        dc.SetBrush(wx.Brush(self.color, self.style))
        dc.SetPen(wx.Pen(self.color, self.style))
        dc.DrawRectangle(pt=self.pos, sz=self.size)
    
class CanvasPanelItem:
    """ Item to display canvas panel item
    """
    def __init__(self, canvas_panel,
                 canv_type, args=None, kwargs=None):
        self.canvas_panel = canvas_panel
        self.canv_id = canvas_panel.get_id()
        self.canv_type = canv_type
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
         
        dc = wx.PaintDC(self.canvas_panel)
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
        
        
        
        dc = wx.PaintDC(self.canvas_panel)
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
        
        dc = wx.PaintDC(self.canvas_panel)
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
            
            

class CanvasPanel(wx.Panel):
    """ Panel in which we can do tkinter like things
    """
    def __init__(self, *args, **kw):
        super(CanvasPanel, self).__init__(*args, **kw)
        self.SetBackgroundColour("green")
        '''
        sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        sizer_v = wx.BoxSizer(wx.VERTICAL)

        sizer_h.Add(self, 1, wx.EXPAND)
        sizer_v.Add(sizer_h, proportion=1, flag=wx.EXPAND)
        # only set the main sizer if you have more than one
        self.SetSizer(sizer_v)
        '''
        self.Show()
        self.can_id = 0
        self.items_by_id = {}   # Item's index in items[]
        self.items = []         # Items in order drawn
        self.prev_reg = None    # Previously displayed
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Show()
        self.color = "green"
        self.on_paint_skip = 1 # debug - update only every nth
        self.on_paint_count = 0 # count paints

    def get_id(self):
        """ Get unique id
        """
        self.can_id += 1
        return self.can_id
    
    def create_rectangle(self, cx1,cy1,cx2,cy2,
                                **kwargs):
        """ Implement creat_rectangle
            supporting: fill, outline, width
        """
        """_summary_

        Returns:
            _type_: _description_
        """
        item = CanvasPanelItem(self, "create_rectangle",
                               args=[cx1,cy1,cx2,cy2],
                               kwargs=kwargs)
        self.items_by_id[item.canv_id] = len(self.items)    # next index
        self.items.append(item)
        return item.canv_id
    
    def create_oval(self, x0,y0,x1,y1,
                        **kwargs):
        """ Implement create_oval
            supporting fill, outline, width
        """
        item = CanvasPanelItem(self, "create_oval",
                               args=[x0,y0,x1,y1],
                               kwargs=kwargs)
        self.items_by_id[item.canv_id] = len(self.items)    # next index
        self.items.append(item)
        return item.canv_id

    def create_line(self, *args, **kwargs):
        """ Implement tkinter's create_line
        :args: x1,y1,...xn,yn
        :kwargs:  width=, fill=, tags=[]
        """
        item = CanvasPanelItem(self, "create_line",
                               args=args,
                               kwargs=kwargs)
        self.items_by_id[item.canv_id] = len(self.items)    # next index
        self.items.append(item)
        return item.canv_id
        

    def delete(self, id_tag):
        """ Delete object in panel
        :id_tag: if str: "all" - all items, else tag
                else id
        """
        if  type(id_tag) == str:
            if id_tag == "all":
                "TBD delete all"
        else:
            self.delete_id(id_tag)

    def delete_id(self, id):
        """ Delete item
        :id:
        """

    def OnSize(self, e):
        self.Refresh()
            
    def OnPaint(self, e):
        self.on_paint_count += 1
        #if self.on_paint_count % self.on_paint_skip != 0:
        #    return
        
        SlTrace.lg("\nOnPaint", "paint")
        style = wx.SOLID
        dc = wx.PaintDC(self)
        dc.SetPen(wx.Pen(self.color))
        dc.SetBrush(wx.Brush(self.color, style))
        
        if self.on_paint_count == 1:
            self.orig_pos = self.GetPosition()  # After setup
            self.orig_size = self.GetSize()
            self.cur_pos = self.prev_pos = self.orig_pos
            self.cur_size = self.prev_size = self.orig_size
        else:
            self.cur_pos = self.GetPosition()  # New rectangle
            self.cur_size = self.GetSize()

        dc.DrawRectangle(self.prev_pos, self.prev_size) # clear previous rectangle
        dc.DrawRectangle(self.cur_pos, self.cur_size)   # clear new rectangle
        self.Show()
        for item in self.items:
            SlTrace.lg(f"item: {item}", "item")
            item.draw()
            self.Show()

        self.prev_pos = self.cur_pos
        self.prev_size = self.cur_size



class CanvasFrame(wx.Frame):
    def __init__(self, title=None, size=None, panel=None):
        """Constructor"""
        wx.Frame.__init__(self, None, title=title,
                          size=size)
        
        if panel is None:
            panel = CanvasPanel(self)
        self.panel = panel1 = panel
        self.SetBackgroundColour("green")

        sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        sizer_v = wx.BoxSizer(wx.VERTICAL)

        sizer_h.Add(panel1, 1, wx.EXPAND)
        sizer_v.Add(sizer_h, proportion=1, flag=wx.EXPAND)
        # only set the main sizer if you have more than one
        self.SetSizer(sizer_v)
        
        self.Show()



    def create_rectangle(self, cx1,cy1,cx2,cy2,
                                **kwargs):
        return self.panel.create_rectangle(cx1,cy1,cx2,cy2,
                                **kwargs)

    
    def create_oval(self, x0,y0,x1,y1,
                        **kwargs):
        """ Implement create_oval
            supporting fill, outline, width
        """
        return self.panel.create_oval(x0,y0,x1,y1, **kwargs)

    def create_line(self, x0,y0,x1,y1, **kwargs):
        """ Implement tkinter's create_line
        :args: x1,y1,...xn,yn
        :kwargs:  width=, fill=, tags=[]
        """
        return self.panel.create_line(x0,y0,x1,y1, **kwargs)


    def delete(self, id_tag):
        """ Delete object in panel
        :id_tag: if str: "all" - all items, else tag
                else id
        """
        return self.panel.delete(id_tag)

if __name__ == "__main__":
    app = wx.App()
    mytitle = "wx.Frame & wx.Panels"
    width = 400
    height = 500
    frame = CanvasFrame(title=mytitle, size=wx.Size(width,height))
    #frame.SetInitialSize(wx.Size(400,400))
    frame.Show()
    canv_pan = frame
    canv_pan.Show()
    canv_pan.create_rectangle(50,100,200,200, fill="red")
    canv_pan.create_rectangle(150,150,300,300, fill="blue")
    canv_pan.create_oval(50,200,100,300, fill="orange")
    canv_pan.create_oval(150,300,250,350, fill="purple")
    nrow = 5
    ncol = 6
    for row in range(1,nrow+1):     # Horizontal lines
        y = (row-1)*height/nrow
        canv_pan.create_line(0,y, width, y, fill="grey")
        
    for col in range(1,ncol+1):     # Vertical lines
        x = (col-1)*width/ncol
        canv_pan.create_line(x,0, x, height, fill="purple")
    
    canv_pan.Show()
    app.MainLoop()