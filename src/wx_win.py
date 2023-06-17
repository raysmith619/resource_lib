#wx_win.py    24May2023  crs, Author
"""
Reference to wx window support
"""
import wx

from select_trace import SlTrace

class WxWin:
    def __init__(self, app, frame):
        """ Setup wxPython window access
        :app: wx.App instance
        :frame: wx.Frame instance
        """
        self.app = app
        self.frame = frame
        self.panel = wx.Panel(frame)
        v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.win_print_ctrl = wx.TextCtrl(self.panel)
        v_sizer.Add(self.win_print_ctrl, 0, wx.ALL )
        win_print_frame = wx.Panel(frame)
        win_print_frame.pack(side=tk.TOP)
        win_print_entry = tk.Entry(
            win_print_frame, width=50)
        win_print_entry.pack(side=tk.TOP)
        self.win_print_entry = win_print_entry

        canvas = tk.Canvas(mw, width=self.win_width, height=self.win_height)
        canvas.pack()
        self.canvas = canvas
        self.update()  # Force display
        SlTrace.lg(f"canvas width: {canvas.winfo_width()}")
        SlTrace.lg(f"canvas height: {canvas.winfo_height()}")
