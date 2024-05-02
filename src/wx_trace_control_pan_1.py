#wx_trace_control_pan.py   24Apr2024  crs from sizer_auto.py
# morphed in hopes of avoiding window parent error

import wx

from select_trace import SlTrace
from wx_trace_flag_box import TraceFlagBox

class ColorPanel(wx.Panel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent, number, color, sub_panels):
        """Constructor"""
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(color)

########################################################################
class MainPanel(wx.Panel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
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

        
        hsizer.Add(tc_all_button, 0, wx.RIGHT)        
        hsizer.Add(tc_none_button, 0, wx.RIGHT)
        hsizer.Add(tc_bpt_button, 0, wx.RIGHT)
        hsizer.Add(tc_show_button, 0, wx.RIGHT)
        #'''
        v_sizer.Add(hsizer, 1, wx.EXPAND)
        
        flags_panel = ColorPanel(self, 0, "white", 0)
        flags_sizer = wx.BoxSizer(wx.VERTICAL)
        flags_panel.SetSizer(flags_sizer)
        v_sizer.Add(flags_panel, 1, wx.EXPAND)
        flags = SlTrace.getAllTraceFlags()
        for flag in flags:
            value = SlTrace.getLevel(flag)
            tfb = TraceFlagBox(flags_panel, flag, value=value)
            flags_sizer.Add(tfb, 0, wx.EXPAND)
        '''
        flags_panel = ColorPanel(self, 0, "orange", 0)
        v_sizer.Add(hsizer, 1, wx.EXPAND)
        v_sizer.Add(flags_panel, 1, wx.EXPAND)
        '''

        self.SetSizer(v_sizer)


    def select_all(self, event=None):
        """ Process Select All button
        """
        if self.select_all:
            self.select_all()

    def select_none(self, event=None):
        """ Process Select NONE button
        """
        if self.select_none:
            self.select_none()

    def breakpoint(self, event=None):
        """ Process Select breakpoint button
        """
        if self.breakpoint:
            self.breakpoint()

    def show_button(self, event=None):
        """ Process Select breakpoint button
        """
        if self.show_button:
            self.show_button()
        
########################################################################
class MainFrame(wx.Frame):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None,
                          title="Testing TraceControlPan",
                          size=(600,400))
        panel = MainPanel(self)
        self.Show()

#----------------------------------------------------------------------
if __name__ == "__main__":
    SlTrace.lg("Testing")
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()