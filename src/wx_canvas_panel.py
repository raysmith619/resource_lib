# wx_canvas_panel.py 28Nov2023  crs, rename canvas_panel.py
#                    08Nov2023  crs
"""
Support for very limited list of tkinter Canvas type actions
on wxPython Panel  Our attempt here was to ease a port
from tkinter Canvas use to wxPython.
"""
import wx
from select_trace import SlTrace, SelectError 
from wx_canvas_panel_item import CanvasPanelItem            

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
        self.mouse_left_down_proc = self.mouse_left_down_def
        self.mouse_motion_proc = self.mouse_motion_def
        self.mouse_b1_motion_proc = self.mouse_b1_motion_def
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
        self.grid_panel_offset = 53 # menu + text TBD
        self.Show()
        self.can_id = 0
        self.items_by_id = {}   # Item's index in items[]
        self.items = []         # Items in order drawn
        self.prev_reg = None    # Previously displayed
        self.grid_panel.Bind(wx.EVT_PAINT, self.OnPaint)
        self.grid_panel.Bind(wx.EVT_SIZE, self.OnSize)
        self.grid_panel.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.grid_panel.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)
        
        self.motion_level = 0   # Track possible recursive calls
        self.grid_panel.Bind(wx.EVT_MOTION, self.on_mouse_motion)
        self.frame.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_left_down_frame)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_left_down_win)
        self.grid_panel.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_left_down)
        self._multi_key_progress = False    # True - processing multiple keys
        self._multi_key_cmd = None          # Set if in progress
        
        
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
        self.grid_panel.SetFocus() # Give grid_panel focus
        
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
        """ Response to paint event
        """
        
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
            SlTrace.lg(f"Set orig_size:{self.orig_size}")
            self.cur_pos = self.prev_pos = self.orig_pos
            self.cur_size = self.prev_size = self.orig_size
            if self.orig_size[0] < 50:
                self.orig_size = self.frame.GetClientSize()
                SlTrace.lg(f"Set orig_size:{self.orig_size}")
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
        SlTrace.lg(f"orig_size: {self.orig_size} cur_size: {self.cur_size}", "paint")
        for item in self.items:
            SlTrace.lg(f"item: {item}", "item")
            item.draw()
            self.Show()

        self.prev_pos = self.cur_pos
        self.prev_size = self.cur_size

    def itemconfig(self, tags, **kwargs):
        """ Adjust items with tags with kwargs
        :tags: tag or tag list of items to change
        :kwargs: new attributes
                    supporting: outline
        """
        if type(tags) != list:
            tags = [tags]
            
        for item in self.items:
            ins = item.tags.intersection(tags)
            if len(ins) > 0:   # item have tag?
                for kw in  kwargs:
                    val = kwargs[kw]
                    if kw == "outline":
                        item.kwargs[kw] = val
                    else:
                        raise SelectError(f"itemconfig doesn't support {kw} (val:{val})")    
    """
    ----------------------- Mouse Control --------------------
    """
    def get_panel_loc(self, e):
        """ Get mouse location in panel coordinates
        """
        screen_loc = e.Position
        panel_loc = wx.Point(screen_loc.x,
                            screen_loc.y+
                            self.grid_panel_offset)
        return panel_loc
    
    def get_screen_loc(self, panel_loc):
        """ Convert panel location to screen location
        :panel_loc: wx.Point of location
        :returns: wx.Point on screen
        """
        screen_loc = wx.Point(panel_loc.x,
                              panel_loc.y-
                              self.grid_panel_offset)
        return screen_loc
    
    import pyautogui   #??? comment this line
                       #??? and first click causes
                       #??? the window to shrink
    # mouse_left_down
    def on_mouse_left_down(self, e):
        """ Mouse down
        """
                
        loc = self.get_panel_loc(e)
        SlTrace.lg(f"\non_mouse_left_down panel({loc.x},{loc.y})"
                   f" [{e.Position.x}, {e.Position.y}]"
                   f"window: pos: {self.GetPosition()}"
                   f" size: {self.GetSize()}"
                   f" GetClientAreaOrigin: {self.GetClientAreaOrigin()}"
                   )
        #??? Without the above live import pyautogui,
        # the first mouse click shrinks window.
        import pyautogui
        screenWidth, screenHeight = pyautogui.size()
        SlTrace.lg(f"screen width:{screenWidth}, hight: {screenHeight}")
        currentMouseX, currentMouseY = pyautogui.position()
        SlTrace.lg(f"mouse x,y: {currentMouseX}, {currentMouseY}")
        #'''
        #e.Skip()
        
        self.mouse_left_down_proc(loc.x, loc.y)
        self.grid_panel.SetFocus() # Give grid_panel focus


    def on_mouse_left_down_win(self, e):
        """ Mouse down in window
        """
                
        loc = wx.Point(e.Position)
        SlTrace.lg(f"\non_mouse_left_down_win ({loc.x},{loc.y})"
                   f" [{e.Position.x}, {e.Position.y}]"
                   f"window: pos: {self.GetPosition()}"
                   f" size: {self.GetSize()}"
                   f" GetClientAreaOrigin: {self.GetClientAreaOrigin()}"
                   )
        import pyautogui
        screenWidth, screenHeight = pyautogui.size()
        SlTrace.lg(f"screen width:{screenWidth}, hight: {screenHeight}")
        currentMouseX, currentMouseY = pyautogui.position()
        SlTrace.lg(f"mouse x,y: {currentMouseX}, {currentMouseY}")
        e.Skip()

    def on_mouse_left_down_frame(self, e):
        """ Mouse down in window
        """
                
        loc = wx.Point(e.Position)
        SlTrace.lg(f"\non_mouse_left_down_frame ({loc.x},{loc.y})"
                   f" [{e.Position.x}, {e.Position.y}]"
                   f"window: pos: {self.GetPosition()}"
                   f" size: {self.GetSize()}"
                   f" GetClientAreaOrigin: {self.GetClientAreaOrigin()}"
                   )
        import pyautogui
        screenWidth, screenHeight = pyautogui.size()
        SlTrace.lg(f"screen width:{screenWidth}, hight: {screenHeight}")
        currentMouseX, currentMouseY = pyautogui.position()
        SlTrace.lg(f"mouse x,y: {currentMouseX}, {currentMouseY}")
        e.Skip()
        
    def mouse_left_down_def(self, x, y):
        """ process mouse left down event
        Replaced for external processing
        :x: mouse x coordiante
        :y: mouse y coordinate
        """
        SlTrace.lg(f"mouse_left_down_proc x={x}, y={y}", "mouse_proc")
    
    def set_mouse_left_down_proc(self, proc):
        """ Set link to front end processing of
        mouse left down event
        :proc: mouse processing function type proc(x,y)
        """
        self.mouse_left_down_proc = proc

    # mouse motion and mouse down motion
    def on_mouse_motion(self, e):
        """ Mouse motion in  window
        we convert <B1-Motion> into on_button_1_motion calls
        """
        loc = self.get_panel_loc(e)
        if e.Dragging():
            self.mouse_b1_motion_proc(loc.x, loc.y)
        else:
            self.mouse_motion_proc(loc.x, loc.y)

    def mouse_motion_def(self, x, y):
        """ Set to connect to remote processing
        """
        SlTrace.lg(f"mouse_motion_proc(x={x}, y={y})", "motion")

    def mouse_b1_motion_def(self, x, y):
        """ Default mouse_b1_motion event proceessing
        """
        SlTrace.lg(f"mouse_b1_motion_proc(x={x}, y={y})")
    
    def set_mouse_motion_proc(self, proc):
        """ Default mouse_motion event processing
        mouse motion event
        :proc: mouse processing function type proc(x,y)
        """
        self.mouse_motion_proc = proc
   
    def set_mouse_b1_motion_proc(self, proc):
        """ Set link to front end processing of
        mouse b1 down motion event
        :proc: mouse processing function type proc(x,y)
        """
        self.mouse_b1_motion_proc = proc
    



    """
    ----------------------- Keyboard Control --------------------
    """

    def set_key_press_proc(self, proc):
        """ Set key press processing function to facilitating 
        setting/changing processing function to after initial
        setup
        :proc: key processing function type proc(keysym)
        """
        self.key_press_proc = proc

       
    def on_char_hook(self, e):
        SlTrace.lg(f"\non_char_hook:{e}", "keys")
        
        if e.AltDown():
            SlTrace.lg(f"{self.get_mod_str(e)}", "keys")
            e.Skip()    # Pass up to e.g., Menu
            return
        
        SlTrace.lg(f"sym: {self.get_mod_str(e)}", "keys")
        SlTrace.lg(f"GetUnicodeKey:{e.GetUnicodeKey()}", "keys")
        SlTrace.lg(f"GetRawKeyCode:{e.GetRawKeyCode()}", "keys")
        SlTrace.lg(f"GetKeyCode:{e.GetKeyCode()}", "keys")
        SlTrace.lg(f"chr(GetKeyCode){chr(e.GetKeyCode())}"
                   f" {ord(chr(e.GetKeyCode()))}", "keys")
        
        keysym = self.get_keysym(e)
        self.key_press_proc(keysym)
        self.grid_panel.SetFocus() # Give grid_panel focus

    def on_key_down(self, e):
        SlTrace.lg(f"on_key_down:{e}", "keys")
        SlTrace.lg(f"sym: {self.get_mod_str(e)}", "keys")
        if e.AltDown():
            SlTrace.lg(f"{self.get_mod_str(e)}", "keys")
            e.Skip()    # Pass up to e.g., Menu
            return
        
        SlTrace.lg(f"GetUnicodeKey:{e.GetUnicodeKey()}", "keys")
        SlTrace.lg(f"GetRawKeyCode:{e.GetRawKeyCode()}", "keys")
        SlTrace.lg(f"GetKeyCode:{e.GetKeyCode()}", "keys")
        keysym = self.get_keysym(e)
        self.key_press_proc(keysym)

    def get_mod_str(self, e):
        """ return modifier list string
        :e: event
        :returns: "[mod1-][mod2-][...]key_sym"
        """
        mod_str = ""
        if e.HasModifiers():
            mods = e.GetModifiers()
            if mods & wx.MOD_ALT:
                if mod_str != "": mod_str += "-"
                mod_str += "ALT"
            if mods & wx.MOD_CONTROL:
                if mod_str != "": mod_str += "-"
                mod_str += "CTL"
            if mods & wx.MOD_SHIFT:
                if mod_str != "": mod_str += "-"
                mod_str += "SHIFT"
            if mods & wx.MOD_ALTGR and mods == wx.MOD_ALTGR:
                if mod_str != "": mod_str += "-"
                mod_str += "ALTGR"
            if mods & wx.MOD_META:
                if mod_str != "": mod_str += "-"
                mod_str += "META"
            if mods & wx.MOD_WIN:
                if mod_str != "": mod_str += "-"
                mod_str += "WIN"
        ret = mod_str
        if ret != "": ret += "-"
        ret += self.get_keysym(e)
        return ret
        

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
    add_menus = True     # True add menus to frame
    add_after_test = True   # Test delay
    
    if add_menus:
        # Provide Menubar to capture Alt-<key>s
        from wx_adw_menus import AdwMenus, FteFake
        
    SlTrace.clearFlags()
    #SlTrace.setFlags("paint")
    SlTrace.setFlags("keys")
    app = wx.App()
    mytitle = "CanvasPanel Selftest"
    width = 400
    height = 500
    if add_menus:
        mytitle += " Using AdwMenus"
        width += 100
    frame = wx.Frame(None, title=mytitle, size=wx.Size(width,height))
    frame.Show()
    if add_menus:
        fte = FteFake()
        menus = AdwMenus(fte, frame=frame)
    canv_pan = CanvasPanel(frame, app=app)
    canv_pan.Show()

    """
    Setup frame level key processing
    Exercising keys passed up from CanvasPanel
    """    
    def frame_on_key_down(e):
        """ process frame level key presses
        """
        SlTrace.lg(f"frame: {canv_pan.get_mod_str(e)}")
        
    def frame_on_char_hook(e):
        """ process frame level key presses
        """
        SlTrace.lg(f"frame hook: {canv_pan.get_mod_str(e)}")
    
    def key_press_proc(key_sym):
        """ Process keys sent from CanvasPanel
        """
        SlTrace.lg(f"key_press: {key_sym}")
        
    if not add_menus:   # if no menu to catch    
        frame.Bind(wx.EVT_KEY_DOWN, frame_on_key_down)
        frame.Bind(wx.EVT_CHAR_HOOK, frame_on_char_hook)

    
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
    if add_after_test:
        SlTrace.lg("Test after() function")
        SlTrace.setFlags("stdouthasts,decpl=2")    
        delay = 1000    # milliseconds
        SlTrace.lg(f"Delay {delay} milliseconds")
        canv_pan.after(0, test_msg_before)
        canv_pan.after(delay, test_msg_after)

    canv_pan.set_key_press_proc(key_press_proc)
    
    app.MainLoop()
    