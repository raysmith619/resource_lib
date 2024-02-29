# squares_test.py   24Feb2024  crs, Author
"""
Squares picture to investigate efficient partial window update
"""
import wx

from select_trace import SlTrace
from wx_canvas_panel import CanvasPanel
from wx_canvas_panel_item import wx_Point
    
SlTrace.clearFlags()
#SlTrace.setFlags("paint")
SlTrace.setFlags("keys")
app = wx.App()
mytitle = "Squares Partial Window Update"
width = 800
height = 800
ncol = 25       # layout
nrow = ncol
sq_width = width/ncol
sq_height = height/nrow

colors = ["red","orange","yellow",
            "green","blue", "indigo",
            "violet", "white"]
icolor = -1          # Current colors index

frame = wx.Frame(None, title=mytitle, size=wx.Size(width,height))
frame.Show()
canv_pan = CanvasPanel(frame, app=app)
canv_pan.Show()
for icol in range(ncol):
    for irow in range(nrow):
        icolor = (icolor+1)%len(colors) # Wrap arround
        color = colors[icolor]
        x1 = icol*sq_width
        y1 = irow*sq_height
        x2 = x1 + sq_width
        y2 = y1 + sq_height
        canv_pan.create_rectangle(x1,y1,x2,y2, fill=color)
        
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
    
frame.Bind(wx.EVT_KEY_DOWN, frame_on_key_down)
frame.Bind(wx.EVT_CHAR_HOOK, frame_on_char_hook)

canv_pan.set_key_press_proc(key_press_proc)

ci = 0
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
    sz = 5
    for item in canv_pan.get_panel_items(screen_pt):
        chg_rect = item.bounding_rect()
        SlTrace.lg(f"\nchg_rect: {chg_rect}")
        if item.canv_type == "create_rectangle":
            SlTrace.lg(f"item: {item}")
            new_id = canv_pan.create_rectangle(item.points[0].x,item.points[0].y,
                                      item.points[1].x, item.points[1].y, color="blue")
            new_item = canv_pan.items_by_id[new_id]
            SlTrace.lg(f"new item: {new_item}")
            canv_pan.Refresh(rect=chg_rect)
    canv_pan.create_point(screen_pt.x,screen_pt.y,
                            radius=4, fill=color)
    canv_pan.create_text(screen_pt.x+1,screen_pt.y+2, text=f"{x},{y}")
    SlTrace.lg(f" mouse:{x},{y} create_point({screen_pt.x},{screen_pt.y})")
    SlTrace.lg(f"panel.sfx,sfy: {canv_pan.sfx},{canv_pan.sfy})")
canv_pan.set_mouse_left_down_proc(mouse_left_down_proc)
        
app.MainLoop()
