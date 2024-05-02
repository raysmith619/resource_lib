#wx_trace_control_panel.py  24Apr2024  crs, move ctl buttons
""" 
Control buttons etc. for trace flag control window
"""
import wx
from select_trace import SlTrace

class TraceControlPanel(wx.Panel):
    def __init__(self, panel, select_all=None,
                select_none=None, breakpoint=None,
                show_button=None):
        self.select_all = select_all
        self.select_none = select_none
        self.breakpoint = breakpoint
        self.show_button = show_button
        self.show_list = None
        
        wx.Panel.__init__(self, panel)
        
        ctl_sizer = wx.BoxSizer(wx.HORIZONTAL)
        v_sizer = wx.BoxSizer(wx.VERTICAL)

        tc_all_button = wx.Button(self, label="SET ALL")
        tc_all_button.Bind(wx.EVT_BUTTON, self.select_all)
        tc_none_button = wx.Button(self, label="NONE")
        tc_none_button.Bind(wx.EVT_BUTTON, self.select_none)
        tc_bpt_button = wx.Button(self, label="BPT")
        tc_bpt_button.Bind(wx.EVT_BUTTON, self.breakpoint)
        tc_show_button = wx.Button(self, label="SHOW...")
        self.tc_show_button = tc_show_button
        tc_show_button.Bind(wx.EVT_BUTTON, self.show_button)
        self.show_list_which = "ALL"    # "ALL", "SET"

        
        ctl_sizer.Add(tc_all_button, 1, wx.EXPAND)        
        ctl_sizer.Add(tc_none_button, 1, wx.EXPAND)
        ctl_sizer.Add(tc_bpt_button, 1, wx.EXPAND)
        ctl_sizer.Add(tc_show_button, 1, wx.EXPAND)
        v_sizer.Add(ctl_sizer, 1, wx.EXPAND)
        self.SetSizer(v_sizer)
        if self.show_list_which == "ALL":
            self.tc_show_button.SetLabel("Show All")
        elif self.show_list_which == "SET":
            self.tc_show_button.SetLabel("Show Set")
        self.Show()

    def select_all(self, event=None):
        """ Process Select All button
        """
        if self.select_all:
            self.select_all()
            
if __name__ == "__main__":
    SlTrace.lg("Testing")
    
    app = wx.App()
    frame = wx.Frame(None)
    panel = wx.Panel(frame)
    tcp = TraceControlPanel(panel)
    frame.Show()
    
app.MainLoop()
 