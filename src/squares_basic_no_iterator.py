# squares_basic_no_iterator.py   25Feb2024  crs, Author
"""
Squares picture to investigate efficient partial window update
simplistic
no update region iterator
"""
import wx

# Poor person's logger/tracer
class SlTrace:
    @staticmethod
    def lg(msg, flag="OK"):
        if flag:
            print(msg)
    @staticmethod
    def clearFlags():
        pass

def wx_Point(x, y=None):
    """ Force int args
    :x: x value
    :y: y value
    :returns: wx_Point
    """
    if y is None:
        return x
    
    return wx.Point(int(x), int(y))

    
SlTrace.clearFlags()
#SlTrace.setFlags("paint")
app = wx.App()

class MyFrame(wx.Frame):
    
    def __init__(self, title=None, size=None,
                 width=800, height=800, ncol=25, nrow=25,
                 colors=None):
        
        self.icolor = -1          # Current colors index
        self.panel_items = []       # [(type_str, bounding_rect)]
        self.outline = True
        self.ncol = ncol
        self.nrow = nrow
        if size is None:
            size = wx.Size(width,height)
        super().__init__(None, title=title, size=size)
        if colors is None:
            colors = ["red","orange","yellow",
            "green","blue", "indigo",
            "violet", "white"]
        self.colors = colors
        color = "black"
        if len(colors) > 0:
            color = colors[0]
        self.color = color       
        self.fill = self.color
        self.style = wx.SOLID

        self.sq_width = width/ncol
        self.sq_height = height/nrow
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Refresh()
        self.Update()       # Force first OnPaint
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_left_down_win)
        self.Show()

		
    def OnPaint(self, e): 
        self.dc = wx.PaintDC(self)
        color = self.color
        self.dc.SetPen(wx.Pen(color))
        self.dc.SetBrush(wx.Brush(self.color,  self.style))
        for icol in range(self.ncol):
            for irow in range(self.nrow):
                self.icolor = (self.icolor+1)%len(self.colors) # Wrap arround
                color = self.colors[self.icolor]
                x1 = icol*self.sq_width
                y1 = irow*self.sq_height
                x2 = x1 + self.sq_width
                y2 = y1 + self.sq_height
                brect = wx.Rect(wx_Point(x1,y1), wx_Point(x2,y2))
                self.add_rect(brect=brect, color=color)


    def add_rect(self, brect, color="black"):
        """ Add new rectangle
        :brect: wx.Rect
        :color: color default: black
        """
        self.panel_items.append(("create_rectangle", brect))
        self.dc.SetPen(wx.Pen(color))
        self.dc.SetBrush(wx.Brush(color,  self.style))
        self.dc.DrawRectangle(brect)
        
                    
    def get_panel_items(self, loc):
        """ Get overlapping items
        :loc: wx.Rect location
        :returns: list of panel_items (type, brect)
        """
        items = []
        for item in self.panel_items:
            item_brect = item[1]
            if item_brect.Contains(loc):
                items.append(item)
        return items

    def item_bounding_rect(self, item):
        """ Get item bounding rectangle
        :item: (type, brect)
        :returns: wx.Rect bounding rectangle
        """
        return item[1]
    
    ci = 0
    def on_mouse_left_down_win(self, e):
        """ Process mouse left down event
        Create point to exercise scaling
        :x,y: grid relative location 
        """
        x,y = e.Position
        SlTrace.lg(f"mouse:{x},{y}")
        self.icolor += 1
        color = self.colors[self.icolor%len(self.colors)]
        screen_pt = wx.Point(x,y)
        sz = 5
        for item in self.get_panel_items(screen_pt):
            chg_rect = self.item_bounding_rect(item)
            item_type, item_brect = item
            if item_type == "create_rectangle":
                SlTrace.lg(f"item: {item}")
                brect = item_brect
                self.add_rect(brect=brect, color="blue")
                frame.Refresh(rect=brect)
        '''
        canv_pan.create_point(screen_pt.x,screen_pt.y,
                                radius=4, fill=color)
        canv_pan.create_text(screen_pt.x+1,screen_pt.y+2, text=f"{x},{y}")
        SlTrace.lg(f" mouse:{x},{y} create_point({screen_pt.x},{screen_pt.y})")
        SlTrace.lg(f"panel.sfx,sfy: {canv_pan.sfx},{canv_pan.sfy})")
        '''

mytitle = "Squares Basic Partial Window Update"

#frame = MyFrame(title=mytitle,nrow=10,ncol=10)
#frame = MyFrame(title=mytitle,nrow=100,ncol=100)
#frame = MyFrame(title=mytitle,nrow=200,ncol=200)
frame = MyFrame(title=mytitle)
        
app.MainLoop()
