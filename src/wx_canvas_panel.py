# wx_canvas_panel.py 28Nov2023  crs, rename canvas_panel.py
#                    08Nov2023  crs
"""
Support for very limited list of tkinter Canvas type actions
on wxPython Panel  Our attempt here was to ease a port
from tkinter Canvas use to wxPython.
"""
import time
import wx
from select_trace import SlTrace, SelectError
from wx_stuff import * 
from wx_canvas_panel_item import CanvasPanelItem            
from wx_adw_display_pending import AdwDisplayPending

        
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
        self.sfx =  1       # default scaling
        self.sfy = 1
        if app is None:
            app = wx.App()
        self.app = app
        super().__init__(frame, *args, **kw)
        self.time_of_update = time.time()
        self.min_time_update = .01      # min time between updates (seconds)
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
        self.grid_panel_offset = 0 # menu + text TBD
        self.Show()
        self.can_id = 0
        self.items_by_id = {}   # Items stored by item.canv_id
                                # Augmented by CanvasPanelItem.__init__()
        self.items = []         # Items in order drawn
        self.adw_dp = AdwDisplayPending(self)        
        self.prev_reg = None    # Previously displayed

        #self.Bind(wx.EVT_PAINT, self.OnPaint)
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
        
    def scale_points(self, pts, sfx=None, sfy=None):
        """ scale a list of two dimensional points
        :pts: list of wx.Points
        :sfx: x scale factor  default: 1
        :sfy: y scale factor default: 1
        :returns: scaled points list
        """
        """ TFD Return original points unscalled
        """
        use_orig_points = True
        use_orig_points = False
        if use_orig_points:
            SlTrace.lg("use_orig_points")
            return pts[:]   # Copy of original points, unchanged
        
        if sfx is None:
            sfx = self.sfx
        if sfy is None:
            sfy = self.sfy
        pts_s = []
        if len(pts) == 0:
            return pts_s
        
        scale_1to1 = True
        if scale_1to1:
            sfx = sfy = 1.0
            SlTrace.lg(f"Force sfx:{sfx} sfy:{sfy}", "force_scale")
        x0,y0 = pts[0]
        for i in range(len(pts)):
            x,y = pts[i]
            x_s = x0 + int((x-x0)*sfx)
            y_s = y0 + int((y-y0)*sfy)
            pts_s.append(wx_Point(x_s,y_s))
        return pts_s
      
    def get_id(self):
        """ Get unique item id id
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

    def create_composite(self, disp_type=None, desc=None):
        """ Create a composite display object
        whose components are displayed in order as an object
        :desc: description, if one
        """
        item = CanvasPanelItem(self, "create_composite",
                               disp_type=disp_type, desc=desc)
        self.items.append(item)
        self.items_by_id[item.canv_id] = item    # store by id
        return item.canv_id
                    
    def create_rectangle(self, cx1,cy1,cx2,cy2,
                                **kwargs):
        """ Implement creat_rectangle
            supporting: fill, outline, width
        :returns: id
        """
        item = CanvasPanelItem(self, "create_rectangle",
                               cx1,cy1,cx2,cy2,
                               **kwargs)
        self.items.append(item)
        self.items_by_id[item.canv_id] = item    # store by id
        return item.canv_id
    
    def create_cursor(self, x0,y0,x1,y1,
                        **kwargs):
        """ Implement create_cursor
            supporting fill, outline, width
        """
        item = CanvasPanelItem(self, "create_cursor",
                               x0,y0,x1,y1,
                               **kwargs)
        self.items_by_id[item.canv_id] = item
        self.items.append(item)
        return item.canv_id
    
    def create_oval(self, x0,y0,x1,y1,
                        **kwargs):
        """ Implement create_oval
            supporting fill, outline, width
        """
        item = CanvasPanelItem(self, "create_oval",
                               x0,y0,x1,y1,
                               **kwargs)
        self.items_by_id[item.canv_id] = item
        self.items.append(item)
        return item.canv_id
    
    def create_point(self, x0,y0, radius=2,
                        **kwargs):
        """ Helper function to create a point
            Shortcut using create_oval
            supporting fill, outline, width
        """
        px0 = x0-radius
        py0 = y0-radius
        px1 = x0+radius
        py1 = y0+radius
        item_id = self.create_oval(px0,py0,px1,py1,
                                **kwargs)
        return item_id

    def create_line(self, *args, **kwargs):
        """ Implement tkinter's create_line
        :args: x1,y1,...xn,yn
        :kwargs:  width=, fill=, tags=[]
        """
        item = CanvasPanelItem(self, "create_line",
                               *args,
                               **kwargs)
        self.items_by_id[item.canv_id] = item
        self.items.append(item)
        return item.canv_id
    
    def create_text(self, x0,y0,
                        **kwargs):
        """ Implement create_text
            supporting fill, font
        """
        item = CanvasPanelItem(self, "create_text",
                               x0,y0,
                               **kwargs)
        self.items_by_id[item.canv_id] = item
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
                    item.refresh()          # Force redraw
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

    def draw_item(self, item):
        """ Draw item
        :item: CanvasPanalItem/canv_id item to draw
        """
        if type(item) == int:
            item = self.id_to_item(item)
        item.draw()
        
    def draw_items(self, items=None, rect=None,
                   types="create_composite"):
        """ Draw scalled items
        :items: items to draw default: self.items
        :rect: Draw only items in this rectangle
                default: draw all items
        :types: item types to draw
                "ALL" - all types except "create_composite"
                default: "create_composite"
        """
        if items is None:
            items = self.items
        if len(items) == 0:
            return
        do_composite = False
        do_all = False
        if types == "create_composite":
            do_composite = True
        elif types == "ALL":
            do_all = True
        else:
            if not isinstance(types,list):
                types = [types]     # Make list
        self.pos_adj = self.cur_pos-self.orig_pos
        SlTrace.lg(f"orig_size: {self.orig_size}"
                   f" cur_size: {self.cur_size}", "item")
        self.sfx = self.cur_size.x/self.orig_size.x
        self.sfy = self.cur_size.y/self.orig_size.y
        if len(items) == 0:
            return      # Short circuit if no items
        
        items_points = self.get_items_points(items)
        items_points_scaled = self.scale_points(items_points)

        ipo = 0     # current offset into items_points_scaled
        for item in items:                
            npts = len(item.points)
            points = items_points_scaled[ipo:ipo+npts]
            SlTrace.lg(f"item: {item}", "item")
            if ((do_composite and item.canv_type == "create_composite")
                    or (do_all and item.canv_type != "create_composite")
                    or (item.canv_type in types)):
                item.draw(points=points, rect=rect)
            ipo += npts # move to next item

    def get_items_points(self, items=None):
        """ Get all drawing points, or embeded figures
        characterization
        points
        :items: items list default: self.items
        :returns: list of all drawn points
        """
        if items is None:
            items = self.items
        points = []
        for item in self.items:
            points += item.points
        return points
                    
    def OnPaint(self, e):
        """ Response to paint event
        """
        
        self.on_paint_count += 1
        SlTrace.lg(f"\nOnPaint {self.on_paint_count}", "paint")
        size = self.GetSize()
        SlTrace.lg(f"panel size: {size}", "paint")
        
            
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
            SlTrace.lg(f"Frame size: {self.frame.GetSize()}", "paint")
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

        self.display_pending()
#        self.check_for_display()    # TFD - wait while events are processed
        self.prev_pos = self.cur_pos
        self.prev_size = self.cur_size
        SlTrace.lg(f"OnPaint: {self.cur_pos} {self.cur_size}", "paint")

    def set_check_proceed(self, proceed=True):
        self.check_proceed = proceed

    def my_app_kill(self, my_app):
        """ stop sup application loop
        :my_app: local wx.App instance
        """         
        my_app.ExitMainLoop()
        
    def check_for_display(self):
        """ Debug wait with event processing
        """
        self.app.MainLoop()

        duration = 4
        self.check_proceed = False
        wx.CallLater(duration*1000, self.set_check_proceed)
        while not self.check_proceed:
            my_app = wx.App()
            wx.CallLater(10, self.my_app_kill, my_app=my_app)
            my_app.MainLoop()
            pass
            
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

    
    def update_item(self, item, **kwargs):
        """ Update cell, with "inplace" attribute changes
            refreshes item's region 
        :item: item / id
        :**kwargs: attributes to be changed
        """
        if type(item) == int:
            item = self.items_by_id[item]
        item.update(**kwargs)
        bdrect = item.bounding_rect()
        self.grid_panel.RefreshRect(rect=bdrect)


    """
    ----------------------- Mouse Control --------------------
    """
    def get_panel_loc(self, e):
        """ Get mouse location in panel coordinates
        """
        screen_loc = e.Position
        panel_loc = wx_Point(screen_loc.x,
                            screen_loc.y-
                            self.grid_panel_offset)
        return panel_loc

    def id_to_item(self, canv_id):
        """ Return item, given id
        :returns: canv item
        """
        return self.items_by_id[canv_id]
    
    def get_panel_items(self, loc, canv_type="create_rectangle"):
        """ Get item/items at this location
        :loc: wx.Point location at this point
        :canv_type: canvas type e.g., create_rectangle
                default: create_rectangle
        """
        items = []
        for item in self.items:
            if item.bounding_rect().Contains(loc):
                if item.canv_type == canv_type:
                    items.append(item)
        return items
        
    def get_screen_loc(self, panel_loc):
        """ Convert panel location to screen location
        :panel_loc: wx_Point of location
        :returns: wx_Point on screen
        """
        screen_loc = wx_Point(panel_loc.x,
                              panel_loc.y+
                              self.grid_panel_offset)
        return screen_loc
    
    #import pyautogui   #??? comment this line
                       #??? and first click causes
                       #??? the window to shrink
    # mouse_left_down
    def on_mouse_left_down(self, e):
        """ Mouse down
        """
                
        loc = self.get_panel_loc(e) # grid relative
        SlTrace.lg(f"\non_mouse_left_down panel({loc.x},{loc.y})"
                   f" [{e.Position.x}, {e.Position.y}]"
                   f"window: pos: {self.GetPosition()}"
                   f" size: {self.GetSize()}"
                   f" GetClientAreaOrigin: {self.GetClientAreaOrigin()}"
                   )
        #e.Skip()
        size = self.grid_panel.GetSize()
        pts = self.scale_points([wx_Point(e.Position.x, e.Position.y),
                                 wx_Point(0,0), wx_Point(size.x,0),
                                 wx_Point(0,size.y), wx_Point(size.x,size.y)])
        pt = pts[0]
        self.mouse_left_down_proc(pt.x, pt.y)
        self.grid_panel.SetFocus() # Give grid_panel focus


    def on_mouse_left_down_win(self, e):
        """ Mouse down in window
        """
                
        loc = wx_Point(e.Position)
        SlTrace.lg(f"\non_mouse_left_down_win ({loc.x},{loc.y})"
                   f" [{e.Position.x}, {e.Position.y}]"
                   f"window: pos: {self.GetPosition()}"
                   f" size: {self.GetSize()}"
                   f" GetClientAreaOrigin: {self.GetClientAreaOrigin()}"
                   )
        e.Skip()

    def on_mouse_left_down_frame(self, e):
        """ Mouse down in window
        """
                
        loc = wx_Point(e.Position)
        SlTrace.lg(f"\non_mouse_left_down_frame ({loc.x},{loc.y})"
                   f" [{e.Position.x}, {e.Position.y}]"
                   f"window: pos: {self.GetPosition()}"
                   f" size: {self.GetSize()}"
                   f" GetClientAreaOrigin: {self.GetClientAreaOrigin()}"
                   )
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

    def redraw(self):
        """ Redraw screen
        """
        #self.Refresh()
        #self.Update()
        #self.Show()

    def refresh_item(self, item):        
        """ mark item's region to be displayed
        :item: CanvasPanelItem/id
        """
        if type(item) == int:
            if item >= len(self.items):
                return      # Outside bounds - ignore
            
            item = self.items[item]
        rect = item.bounding_rect()
        self.grid_panel.RefreshRect(rect)
                    
    def refresh_rectangle(self, *args,
                                **kwargs):
        """ Mark rectangle in need of repainting
        :arg[0]: wx.Rect 0 rectangle to refresh
        :
        :args[0]..args[3]: rectangle x1,y1, x2,y2 coordinates
        """
        if isinstance(args[0], wx.Rect):
            rect = args[0]
        else:
            rect = wx.Rect(wx.Point(args[0],args[1]),wx.Point(args[2],args[3]))
        SlTrace.lg(f"refresh_rectangle({rect})", "refresh")
        self.grid_panel.RefreshRect(rect)

    def update(self, x1=None, y1=None, x2=None, y2=None,
               full=False):
        """ Update display
            If x1,...y2 are present - limit update to rectangle
            If x1 is a wx.Rect use Rect
            :full: force full update
        """
        return  # TFD
        now = time.time()
        '''
        since_last = now - self.time_of_update
        if since_last < self.min_time_update:
            delay_ms = int((self.time_of_update + self.min_time_update-now)*1000)
            wx.CallLater(delay_ms, self.update, x1=x1, y1=y1, x2=x2, y2=y2)
            return          # Too soon for update
        '''
        self.time_of_update = time.time()
        if full:
            self.grid_panel.Refresh()
            self.grid_panel.Update()
            return
    
        SlTrace.lg(f"update: refresh({x1,y1, x2,y2})", "refresh")
        if x1 is not None or x2 is not None:
            if isinstance(x1, wx.Rect):
                self.grid_panel.RefreshRect(x1)
            else:
                self.grid_panel.RefreshRect(rect=wx.Rect(wx_Point(x1,y1),
                                                         wx_Point(x2,y2)))
        else:
            self.grid_panel.Refresh()
        self.grid_panel.Update()
        
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


    """
    Links to adw_display_pending
    """
    
    def add_item(self, item):
        """ Add display item
        :item: item/id (CanvasPanelItem)
        """
        self.adw_dp.add_item(item)

    def get_displayed_items(self):
        """ Get list of displayed items
        :returns: list of permanently displayed values (AdwDisplayPendingItem)
        """
        return self.adw_dp.get_displayed_items()


    def is_overlapping(self, item1, item2):
        """ Check if two display items are overlapping
        :returns: True iff overlapping
        """
        return self.adw_dp.is_overlapping(item1, item2)

        
    def add_cell(self, di_item):
        """ Add cell to be displayed
        :di_item: display item
        """            
        self.adw_dp.add_cell(di_item)

    def add_cursor(self, cursor):
        """ Display list and clear it
        """
        self.adw_dp.add_cursor(cursor)

    
    def display_pending(self):
        """ Display list and clear it
        """
        self.adw_dp.display_pending()

if __name__ == "__main__":
    add_menus = True     # True add menus to frame
    add_after_test = True   # Test delay
    add_after_test = False
    
    if add_menus:
        # Provide Menubar to capture Alt-<key>s
        from wx_adw_menus import AdwMenus, FteFake
        
    SlTrace.clearFlags()
    #SlTrace.setFlags("paint")
    SlTrace.setFlags("keys")
    app = wx.App()
    mytitle = "CanvasPanel Selftest"
    width = 600
    height = 800
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
    square_size = 100
    for row in range(1,height//square_size+1):     # Horizontal lines
        y = (row-1)*square_size
        canv_pan.create_line(0,y, width, y, fill="grey")
        canv_pan.create_point(0,y)
        canv_pan.create_text(0,y+3,text=f"{y}")
    for col in range(1,width//square_size+1):     # Vertical lines
        x = (col-1)*square_size
        canv_pan.create_line(x,0, x, height, fill="purple")
        canv_pan.create_point(x,0)
        canv_pan.create_text(x+3,3,text=f"{x}")
    # Dots at cross points
    for row in range(1,height//square_size+1):     # Horizontal lines
        y = (row-1)*square_size
        for col in range(1,width//square_size+1):     # Vertical lines
            x = (col-1)*square_size
            canv_pan.create_point(x, y, fill="white")
            if x == y:
                canv_pan.create_text(x+3,y+3,text=f"{x}")

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
    
    ci = 0
    colors = ["red","orange","yellow",
              "green","blue", "indigo",
              "violet", "white","black"]
    def mouse_left_down_proc(x,y):
        """ Process mouse left down event
        Create point to exercise scaling
        :x,y: grid relative location 
        """
        SlTrace.lg(f"mouse:{x},{y}")
        global ci
        ci += 1
        color = colors[ci%len(colors)]
        screen_pt = canv_pan.get_screen_loc(wx_Point(x,y))
        pt_radius = 4
        canv_pan.create_point(screen_pt.x,screen_pt.y,
                              radius=pt_radius, fill=color)
        canv_pan.create_text(screen_pt.x+1,screen_pt.y+2, text=f"{x},{y}")
        pt_size = pt_radius*2 + 5
        x1,y1 = screen_pt.x,screen_pt.y
        x2,y2 = int(screen_pt.x+pt_size/2),int(screen_pt.y+pt_size/2)
        canv_pan.refresh_rectangle(x1,y1,x2,y2)
        SlTrace.lg(f" mouse:{x},{y} create_point({screen_pt.x},{screen_pt.y})")
        SlTrace.lg(f"panel.sfx,sfy: {canv_pan.sfx},{canv_pan.sfy})")
    canv_pan.set_mouse_left_down_proc(mouse_left_down_proc)
            
    app.MainLoop()
    