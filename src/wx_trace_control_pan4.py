#wx_trace_control_pan4.py  24Apr2024  crs, move ctl buttons
""" 
Control buttons / flags for trace flag control window
"""
import wx
import wx.lib.scrolledpanel as scrolled

from select_trace import SlTrace
from wx_trace_flag_box import TraceFlagBox


class FlagsPanel(scrolled.ScrolledPanel):

    def __init__(self, parent):

        scrolled.ScrolledPanel.__init__(self, parent, -1)

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vbox)
        self.vbox = vbox
                
        ###self.flags_panel = wx.Panel(self)
        ###self.flags_sizer = wx.BoxSizer(wx.VERTICAL)
        ###self.flags_panel.SetSizer(self.flags_sizer)
        
    def add(self, entry):
        """ Add flag  entry
        :entry: (TraceFlagBox)
        """
        self.vbox.Add(entry, 0)
        
    def clear(self):
        """ clear out entries
        """
        self.vbox.Clear(delete_windows=True)
    
    def complete(self):
        """ Complete scrolling setup
        """
        self.SetupScrolling(scroll_x=False)
        #self.Fit()


class TraceControlPanel(wx.Panel):
    def __init__(self, panel, change_call=None):
        """ Support trace control display and updates
        :change_call: function to do updates default: no calls
        """
        self.flags_sizer = None     # sizer controling flags
        self.flag_by_cb = {}             # Dictionary hashed on cb widget
        self.data_by_flag = {}      # [tcb, flag]
        
        self.standalone = False      # Set True if standalone operation
        self.change_call = change_call
        
        wx.Panel.__init__(self, panel)
        
        ctl_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.v_sizer = wx.BoxSizer(wx.VERTICAL)
        tc_set_text = wx.StaticText(self, label="Set")
        tc_all_button = wx.Button(self, label="ALL", style=wx.BU_EXACTFIT)
        tc_all_button.Bind(wx.EVT_BUTTON, self.set_all)
        tc_clear_button = wx.Button(self, label="NONE", style=wx.BU_EXACTFIT)
        tc_clear_button.Bind(wx.EVT_BUTTON, self.clear_all)
        tc_bpt_button = wx.Button(self, label="BPT")
        tc_show_text = wx.StaticText(self, label="Show")
        tc_bpt_button.Bind(wx.EVT_BUTTON, self.breakpoint)
        tc_show_all_button = wx.Button(self, label="ALL")
        tc_show_all_button.Bind(wx.EVT_BUTTON, self.show_all)
        tc_show_set_button = wx.Button(self, label="SET")
        tc_show_set_button.Bind(wx.EVT_BUTTON, self.show_set)
        tc_show_clear_button = wx.Button(self, label="CLEAR")
        tc_show_clear_button.Bind(wx.EVT_BUTTON, self.show_clear)

        self.flags_panel = FlagsPanel(self)  # Holds flags panel

        ctl_sizer.Add(tc_set_text, 0, wx.RIGHT)
        ctl_sizer.Add(tc_all_button, 1, wx.RIGHT)        
        ctl_sizer.Add(tc_clear_button, 1, wx.RIGHT)
        ctl_sizer.Add((5,0), 0)
        ctl_sizer.Add(tc_bpt_button, 1, wx.RIGHT)
        ctl_sizer.Add((5,0), 0)
        ctl_sizer.Add(tc_show_text, 0, wx.RIGHT)
        ctl_sizer.Add(tc_show_all_button, 1, wx.RIGHT)
        ctl_sizer.Add(tc_show_set_button, 1, wx.RIGHT)
        ctl_sizer.Add(tc_show_clear_button, 1, wx.RIGHT)
        self.v_sizer.Add(ctl_sizer, 0, wx.EXPAND)
        self.v_sizer.Add(self.flags_panel, 1, wx.EXPAND)
        self.SetSizer(self.v_sizer)

        flags = self.getAllFlags()
        self.display_flags(flags)
        self.v_sizer.Fit(self)
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
        self.flags_panel.clear()
        for flag in flags:
            value = self.getLevel(flag)
            tfb = TraceFlagBox(self.flags_panel, flag, value=value)
            self.data_by_flag[flag] = [tfb, flag]
            self.flags_panel.add(tfb)
        self.flags_panel.complete()
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
        return SlTrace.getTraceFlags()
    
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
    nflags = 50
    for n in range(1,nflags+1):
        flag = f"flag_{n}"
        SlTrace.setTraceFlag(flag, True)
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()

 