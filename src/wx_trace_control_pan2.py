#wx_trace_control_panel.py  24Apr2024  crs, move ctl buttons
""" 
Control buttons / flags for trace flag control window
"""
import wx
import wx.lib.scrolledpanel as scrolled

from select_trace import SlTrace
from wx_trace_flag_box import TraceFlagBox


class FlagsPanel(scrolled.ScrolledPanel):

    def __init__(self, parent):

        scrolled.ScrolledPanel.__init__(self, parent, -1,
                                        scroll_x=False)

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vbox)
        self.vbox = vbox
        
    def add_flag(self, entry):
        """ Add flag  entry
        :entry: (TraceFlagBox)
        """
    
    def complete(self):
        """ Complete scrolling setup
        """
        self.SetupScrolling()


class TraceControlPanel(wx.Panel):
    def __init__(self, panel, change_call=None):
        """ Support trace control display and updates
        :change_call: function to do updates default: no calls
        """
        self.flags_panel = None     # pannel for flags
        self.flag_by_cb = {}             # Dictionary hashed on cb widget
        self.data_by_flag = {}      # [tcb, flag]
        
        self.standalone = False      # Set True if standalone operation
        self.change_call = change_call
        
        wx.Panel.__init__(self, panel)
        
        ctl_sizer = wx.BoxSizer(wx.HORIZONTAL)
        v_sizer = wx.BoxSizer(wx.VERTICAL)

        tc_all_button = wx.Button(self, label="SET ALL")
        tc_all_button.Bind(wx.EVT_BUTTON, self.set_all)
        tc_clear_button = wx.Button(self, label="CLEAR ALL")
        tc_clear_button.Bind(wx.EVT_BUTTON, self.clear_all)
        tc_bpt_button = wx.Button(self, label="BPT")
        tc_bpt_button.Bind(wx.EVT_BUTTON, self.breakpoint)
        tc_show_all_button = wx.Button(self, label="Show ALL")
        tc_show_all_button.Bind(wx.EVT_BUTTON, self.show_all)
        tc_show_set_button = wx.Button(self, label="Show SET")
        tc_show_set_button.Bind(wx.EVT_BUTTON, self.show_set)
        tc_show_clear_button = wx.Button(self, label="Show CLEAR")
        tc_show_clear_button.Bind(wx.EVT_BUTTON, self.show_clear)


        
        ctl_sizer.Add(tc_all_button, 1, wx.RIGHT)        
        ctl_sizer.Add(tc_clear_button, 1, wx.RIGHT)
        ctl_sizer.Add(tc_bpt_button, 1, wx.RIGHT)
        ctl_sizer.Add(tc_show_all_button, 1, wx.RIGHT)
        ctl_sizer.Add(tc_show_set_button, 1, wx.RIGHT)
        ctl_sizer.Add(tc_show_clear_button, 1, wx.RIGHT)
        v_sizer.Add(ctl_sizer, 0, wx.EXPAND)
        self.SetSizer(v_sizer)

        
        self.flags_panel = wx.Panel(self)
        self.flags_sizer = wx.BoxSizer(wx.VERTICAL)
        self.flags_panel.SetSizer(self.flags_sizer)
        v_sizer.Add(self.flags_panel, 0, wx.LEFT|wx.BOTTOM)
        flags = self.getAllFlags()
        self.display_flags(flags)
        v_sizer.Fit(self)
        self.Show()

    def list_ckbuttons(self):
        cb_flags = sorted(self.data_by_flag.keys())
        for flag in cb_flags:
            tcb = self.data_by_flag[flag][0]
            value = tcb.get() if tcb is not None else None
            SlTrace.lg(f"flag={flag} val={value}")

    def display_flags(self, flags):
        """Display new set of flags
        :flags: ordered list of flag strings
        """
        self.data_by_flag = {}  # Set to displayed controls
        self.flags_sizer.Clear(delete_windows=True)
        self.flags_sizer.Show(self)    
        for flag in flags:
            value = self.getLevel(flag)
            tfb = TraceFlagBox(self.flags_panel, flag, value=value)
            self.data_by_flag[flag] = [tfb, flag]
            self.flags_sizer.Add(tfb, 0, wx.LEFT)
        self.flags_sizer.Fit(self.flags_panel)
        self.Layout()    
        self.Show()
        
    def show_all(self, event=None):
        """ Select buttons to show
        """
        flags = sorted(self.getAllFlags())
        self.display_flags(flags)

    def show_set(self, event=None):
        """ Select buttons to show
        """
        flags = sorted(self.getAllFlags())
        set_flags = []
        for flag in flags:
            if self.getLevel(flag):
                set_flags.append(flag)
        self.display_flags(set_flags)

    def show_clear(self, event=None):
        """ Select buttons to show
        """
        flags = sorted(self.getAllFlags())
        clear_flags = []
        for flag in flags:
            if not self.getLevel(flag):
                clear_flags.append(flag)
        self.display_flags(clear_flags)
        
    def set_all(self, event=None):
        """ All all trace flags
        """
        for flag in sorted(self.getAllFlags()):   # In display order
            self.set_trace_level(flag, True)
        self.show_set()

    def clear_all(self, event=None):
        """ Clear all known trace flags (only booleans)
        """
        for flag in sorted(self.getAllFlags()):   # In display order
            self.set_trace_level(flag, False)
        self.show_clear()
        
    def set_trace_level(self, flag, val, change_cb=True):
        """ Set trace level, changing Control button if requested
        :flag: - trace flag name
        :val: - value to set
        :change_cb: True(default) appropriately change the control
        """
        self.setLevel(flag, val)
        
        if flag not in self.data_by_flag:
            return
        
        tcb, flag = self.data_by_flag[flag]        
        if tcb is None:
            SlTrace.lg("set_trace_level(%s,%d) - flag No tcb" % (flag, val))
            return

        if change_cb:
            tcb.set(flag, val)
                    
        SlTrace.lg(f"flag={flag}, val={val}", "trace_flags")
        self.setLevel(flag, val)
            
        if self.change_call is not None:
            self.change_call(flag, val)

    def getAllFlags(self):
        return SlTrace.getAllTraceFlags()
    
    def getLevel(self, flag):
        return SlTrace.getLevel(flag)

    def setLevel(self, flag, value):
        """ Set level
        :flag: flag string
        :value: value
        :returns: new value
        """
        SlTrace.setLevel(flag, value)
        return value
    
    def breakpoint(self, event=None):
        """ Force immediate breakpoint - enter debugger
        """
        import pdb
        SlTrace.lg("Breakpoint")
        pdb.set_trace()
            
########################################################################
class MainFrame(wx.Frame):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None,
                          title="Testing TraceControlPan",
                          size=(600,400))
        panel = TraceControlPanel(self)
        self.Show()

#----------------------------------------------------------------------
if __name__ == "__main__":
    SlTrace.lg("Testing")
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()

 