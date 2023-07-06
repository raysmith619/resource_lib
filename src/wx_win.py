#wx_win.py    24May2023  crs, Author
"""
Reference to wx window support
"""
import time
import wx

from select_trace import SlTrace

class WxWin:
    def __init__(self, adw, title=None):
        """ Setup wxPython window access
        :adw: AudioDrawWindow base
        :title: optional window title
        """
        self.adw = adw
        self.app = wx.App()
        frame = wx.Frame(None,  title=title)

        adw_panel = wx.Panel(frame)
        adw_vbox = wx.BoxSizer(wx.VERTICAL)
        tout_hbox = wx.BoxSizer(wx.HORIZONTAL)
        adw_vbox.Add(tout_hbox, flag=wx.CENTER)
        tout_ctrl = wx.TextCtrl(adw_panel)
        tout_hbox.Add(tout_ctrl)
        self.tout_ctrl = tout_ctrl

        
        adw_panel.SetSizerAndFit(adw_vbox)
        frame.Show()

    def MainLoop(self):
        self.app.MainLoop()

    def update(self):
        time.sleep(.1)
        wx.Yield()
                        
if __name__ == "__main__":
    from wx_audio_draw_window import AudioDrawWindow
    
    #adw = AudioDrawWindow(setup_wx_win=False)
    adw = None
    wx_win = WxWin(adw, "WxWin Self Test")
    wx_win.MainLoop()
