# canvas_panel.py 08Nov2023  crs
"""
Support for very limited list of tkinter Canvas type actions
on wxPython Panel  Our attempt here was to ease a port
from tkinter Canvas use to wxPython.
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
            
            

class CanvasPanel(wx.Panel):
    """ Panel in which we can do tkinter like things
    """
    def __init__(self, frame, app=None, color=None,
                key_press_proc=None,
                *args, **kw):
        """
        :frame: parent frame
        :app: wx.App, default create
        :color: background color default: :" light gray"
        :key_press: function(sym) to execute
                    keyboard command
                    default: echo sym
        """
        self.frame = frame
        if app is None:
            app = wx.App()
        self.app = app
        super().__init__(frame, *args, **kw)
        
        self.with_alt = False   # Check next key
        if key_press_proc is None:
            key_press_proc = self.key_press
        self.key_press_proc = key_press_proc
        if color is None:
            color = "light gray"
        self.SetBackgroundColour(color)
        self.color = color
        self.frame_size = frame.GetSize()
        self.text_entry_panel = wx.Panel(self)
        self.grid_panel = wx.Panel(self)
        self.entry = wx.TextCtrl(self.text_entry_panel,
                                 size=wx.Size(300,20),
                                 style=wx.TE_PROCESS_ENTER)
        sizer_v = wx.BoxSizer(wx.VERTICAL)
        sizer_v.Add(self.text_entry_panel, 0, wx.ALIGN_CENTER_HORIZONTAL)
        sizer_v.Add(self.grid_panel, 1, wx.EXPAND)
        self.SetSizer(sizer_v)
    
        self.Show()
        self.can_id = 0
        self.items_by_id = {}   # Item's index in items[]
        self.items = []         # Items in order drawn
        self.prev_reg = None    # Previously displayed
        self.grid_panel.Bind(wx.EVT_PAINT, self.OnPaint)
        self.grid_panel.Bind(wx.EVT_SIZE, self.OnSize)
        self.grid_panel.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.grid_panel.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)
        self.Show()
        self.on_paint_skip = 1 # debug - update only every nth
        self.on_paint_count = 0 # count paints
        frame.SetSize(self.frame_size)
        panel_size = frame.GetClientSize()
        frame.Show()
        self.SetSize(panel_size)
        self.Refresh()
        self.Update()
        self.Show()
        wx.CallLater(0, self.SetSize, (self.frame.GetSize()))
        self.Show()

    def set_key_press_proc(self, proc):
        """ Set key press processing function to facilitating 
        setting/changing processing function to after initial
        setup
        :proc: key processing function type proc(keysym)
        """
        self.key_press_proc = proc
        
    def get_id(self):
        """ Get unique id
        """
        self.can_id += 1
        return self.can_id

    def no_call(self):
        """ Just a nothing call
        """
        return
    
    def after(self, delay, callback=None):
        """ Call after delay
        :delay: delay in milliseconds
        :callback: function to call
            default: no function, just delay
        """
        if callback is None:
            callback = self.no_call
        wx.CallLater(delay, callback)
            
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
        

    def delete(self, *id_tags):
        """ Delete object(s) in panel
        :id_tags: if str: "all" - all items, else tag
                else id
        """
        for id_tag in id_tags:
            self.delete_id(id_tag)

    def delete_id(self, id_tag):
        """ Delete items having id or tag
        :id_tag: id or tag
        """
        for item in self.items:
            if type(id_tag) == int:
                if id_tag == item.canv_id:
                    item.deleted = True
                    break   # id is unique
            
                if id_tag in item.tags:
                    item.deleted = True

    def OnSize(self, e):
        self.Refresh()
        self.Update()
        SlTrace.lg(f"\nOnSize paint count:{self.on_paint_count}", "paint")
        size = self.GetSize()
        SlTrace.lg(f"panel size: {size}", "paint")
        e.Skip()
            
    def OnPaint(self, e):
        
        self.on_paint_count += 1
        SlTrace.lg(f"\nOnPaint {self.on_paint_count}", "paint")
        size = self.GetSize()
        SlTrace.lg(f"panel size: {size}", "paint")
        style = wx.SOLID
        dc = wx.PaintDC(self.grid_panel)
        dc.SetPen(wx.Pen(self.color))
        dc.SetBrush(wx.Brush(self.color, style))
        
            
        if self.on_paint_count == 1:
            self.orig_pos = self.GetPosition()  # After setup
            self.orig_size = self.GetSize()
            self.cur_pos = self.prev_pos = self.orig_pos
            self.cur_size = self.prev_size = self.orig_size
            if self.orig_size[0] < 50:
                self.orig_size = self.frame.GetClientSize()
                SlTrace.lg(f"use client size: {self.orig_size}", "paint")
                self.cur_size = self.orig_size
                SlTrace.lg(f"Set cur size: {self.cur_size}", "paint")

            SlTrace.lg(f"First Paint size: {self.orig_size}")
            SlTrace.lg(f"Frame size: {self.frame.GetSize()}")
            self.Refresh()  # Force second repaint
            self.Update()
            SlTrace.lg(f"Refresh Paint panel size: {self.GetSize()}", "paint")
            SlTrace.lg(f"Frame size: {self.frame.GetSize()}", "paint")
            self.Show()
            self.Hide()
            self.Show()
            SlTrace.lg(f"First Paint size: {self.GetSize()}", "paint")
            SlTrace.lg(f"Frame size: {self.frame.GetSize()}", "paint")
            return
                
        else:
            self.cur_size = self.GetSize()
            if self.cur_size[0] < 50:
                self.prev_size = self.cur_size = self.frame.GetClientSize()
                SlTrace.lg(f"use client size: {self.cur_size}", "paint")
                SlTrace.lg(f"Set cur size: {self.cur_size}", "paint")
            SlTrace.lg(f"Further Paint size: {self.GetSize()}", "paint")
            SlTrace.lg(f"Frame size: {self.frame.GetSize()}", "paint")
            pass

        dc.DrawRectangle(self.prev_pos, self.prev_size) # clear previous rectangle
        dc.DrawRectangle(self.cur_pos, self.cur_size)   # clear new rectangle
        self.Show()
        for item in self.items:
            SlTrace.lg(f"item: {item}", "item")
            item.draw()
            self.Show()

        self.prev_pos = self.cur_pos
        self.prev_size = self.cur_size

    def on_key_down(self, e):
        SlTrace.lg(f"on_key_down:{e}")
        if e.GetKeyCode() == wx.WXK_ALT:
            if not self.with_alt:
                SlTrace.lg("wx.WXK_ALT")
                self.with_alt = True
            #e.DoAllowNextEvent()
            #e.Skip()
            return
        
        if self.with_alt:
            SlTrace.lg(f"ALT-{e.GetKeyCode()}")
            self.with_alt = False
            e.Skip()
            return
        
        SlTrace.lg(f"GetUnicodeKey:{e.GetUnicodeKey()}")
        SlTrace.lg(f"GetRawKeyCode:{e.GetRawKeyCode()}")
        SlTrace.lg(f"GetKeyCode:{e.GetKeyCode()}")
        keysym = self.get_keysym(e)
        self.key_press_proc(keysym)

    def on_char_hook(self, e):
        SlTrace.lg(f"\non_char_hook:{e}")
        SlTrace.lg(f"GetUnicodeKey:{e.GetUnicodeKey()}")
        SlTrace.lg(f"GetRawKeyCode:{e.GetRawKeyCode()}")
        SlTrace.lg(f"GetKeyCode:{e.GetKeyCode()}")
        SlTrace.lg(f"chr(GetKeyCode){chr(e.GetKeyCode())}"
                   f" {ord(chr(e.GetKeyCode()))}")
        if e.GetUnicodeKey() != 0:
            e.Skip()    # Pass on regular keys
            return
        
        keysym = self.get_keysym(e)
        self.key_press_proc(keysym)
        

    def key_press(self, keysym):
        """ default/null simulated key event
        :keysym: Symbolic key value/string
        """
        SlTrace.lg(keysym)
        return

    def get_keysym(self, e):
        """ Convert key symbol to keysym(tkinter style)
        :e: key event
        :returns: keysym(tkinter) string
        """
        unicode = e.GetUnicodeKey()
        raw_key_code = e.GetRawKeyCode()
        key_code = e.GetKeyCode()
        ch = chr(unicode)  # lazy - accept all single char

        if (key_code >= wx.WXK_NUMPAD0 and
            key_code <= wx.WXK_NUMPAD9):
            return str(key_code-wx.WXK_NUMPAD0)        
        if key_code == wx.WXK_ALT:
            return 'Alt_L'
        if key_code == wx.WXK_ESCAPE:
            return 'Escape'
        if key_code == wx.WXK_UP:
            return 'Up'
        if key_code == wx.WXK_DOWN:
            return 'Down'
        if key_code == wx.WXK_LEFT:
            return 'Left'
        if key_code == wx.WXK_RIGHT:
            return 'Right'
        if key_code == wx.WXK_WINDOWS_LEFT:
            return 'win_l'

        if len(ch) == 1:
            return ch
        
        return '???'    # Unrecognized

if __name__ == "__main__":
    SlTrace.clearFlags()
    app = wx.App()
    mytitle = "wx.Frame & wx.Panels"
    width = 400
    height = 500
    frame = wx.Frame(None, title=mytitle, size=wx.Size(width,height))
    #frame = CanvasFrame(None, title=mytitle, size=wx.Size(width,height))
    #frame.SetInitialSize(wx.Size(400,400))
    frame.Show()
    canv_pan = CanvasPanel(frame, app=app)
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
        
    def test_msg_before(msg="Before delay"):
        SlTrace.lg(msg)
        
    def test_msg_after(msg="After delay"):
        SlTrace.lg(msg)
    
    SlTrace.setFlags("stdouthasts,decpl=2")    
    delay = 3000    # milliseconds
    SlTrace.lg(f"Delay {delay} milliseconds")
    canv_pan.after(0, test_msg_before)
    canv_pan.after(delay, test_msg_after)
 
    app.MainLoop()
    