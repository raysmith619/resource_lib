#wx_trace_flag_box.py   18Apr2024  crs Author
""" Select Trace Flag data display
Facilitates setting and display of select flag value
design
flag -text
value - text  with type: boolean, int
    types:              display/input
            boolean     check box
            int         entry
            string      entry
display
    [ ] flag name
        
"""
import re
import wx
from select_trace import SlTrace

class TraceFlagBox(wx.Panel):
    def __init__(self,
                 parent : wx.Panel,
                 flag : str,
                 typ : type = None,
                 value = None):
        """ Setup entry/display of a flag
        :flag: name of flag
        :typ: type of value default: Determined by value if present
                                    else: bool
        :value: current value default:
        """
        super().__init__(parent)
        self.flag = flag
        if typ is None:
            if value is not None:
                typ = type(value)
            else:
                typ = bool                
        self.type = typ
        if value is None:
            if typ == bool:
                value = False
            elif typ == int:
                value = 0
            elif typ == float:
                value = 0.
            else:
                value = ""
        self.value = value
        
        tfb_sizer = wx.BoxSizer(wx.HORIZONTAL)
        if typ == bool:
            val_ctl = wx.CheckBox(self, label=flag)   # Treat all flags the same -
            val_ctl.SetValue(value)
            self.Bind(wx.EVT_CHECKBOX, self.on_checkbox)                                        #   sizer
        elif typ == int:
            val_ctl = wx.TextCtrl(self, value=str(value))
        elif typ == float:
            val_ctl = wx.TextCtrl(self, value=str(value))
        elif typ == str:
            val_ctl =  wx.TextCtrl(self, value=value)
        else:
            raise Exception(f"Unrecognized type {typ}")
        self.val_ctl = val_ctl
        tfb_sizer.Add(val_ctl, 0, wx.RIGHT)     # checkbox has own label
        if typ != bool:
            tfb_sizer.Add(wx.StaticText(self, label=flag), 0, wx.RIGHT)
        self.SetSizer(tfb_sizer)

    def on_checkbox(self, event):
        """Process any checkbox click
        :event: event
        """
        cb = event.GetEventObject()
        flag = cb.GetLabel()
        value = cb.GetValue()
        self.set(flag, value)
        
    def get(self):
        """ Get current value
        """
        return self.value

    def set(self, flag, val):
        """ Set value
        :flag: flag string
        :val: new value
        """
        SlTrace.setTraceFlag(flag, val)
        if isinstance(self.val_ctl, wx.CheckBox):    
            self.val_ctl.SetValue(val)
        elif isinstance(self.val_ctl, wx.TextCtrl):
            self.val_ctl = wx.TextCtrl(self, value=str(val))
            
            
    def str_to_type(self, st):
        """ Determine flag type value string
        :st: value string
        :returns: variable type default: bool
        """
        
        if st is None:
            return bool
        if type(st) == str:
            stl = st.lower()
            if stl in ["t", "true", "1", "f", "false", "0"]:
                return bool
            
            if re.match(r"^\d+", st):
                return int
        
            if re.match(r"^((\d+\.\d*)|(\d*\.\d+)$", st):
                return float
        
        return str       # else Assume a string
        
        
            
                
if __name__ == "__main__":
    SlTrace.lg("Testing")
    
    app = wx.App()
    frame = wx.Frame(None)
    panel = wx.Panel(frame)
    tfl_sizer = wx.BoxSizer(wx.VERTICAL)
    panel.SetSizer(tfl_sizer)

    flags = SlTrace.getAllTraceFlags()
    for flag in flags:
        value = SlTrace.getLevel(flag)
        tfb = TraceFlagBox(panel, flag, value=value)
        tfl_sizer.Add(tfb, proportion=1)
    frame.Show()
    
    app.MainLoop()
    