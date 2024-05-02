# wx_trace_control_window.py 19Mar2024  crs, from trace_control_window.py
# Use wxPython
import sys
import time
import atexit

import wx

from select_trace import SlTrace
from wx_trace_control_pan3 import TraceControlPanel
        
class TraceControlWindow(wx.Frame):
    def __init__(self, tcbase=None, change_call=None):
        """ Trace flag dictionary
        :tcbase: - parent - call basis must have tc_destroy to be called if we close
        :change_call: - call with change flag, value, if present
        """
        if tcbase is None:
            SlTrace.lg("Standalone TraceControlWindow")
            root = wx.Frame(None, -1, "Trace Control")
            frame = wx.Frame(root)
            frame.Show()
            self.standalone = True
        self.tcbase = tcbase
        tc_x0 = 800
        tc_y0 = 100
        tc_w = 400
        tc_h = 200
        wx.Frame.__init__(self, tcbase, id=wx.ID_ANY,
                         size=(tc_w,tc_h), pos=(tc_x0,tc_y0))
        self.tcp = TraceControlPanel(self)                    

        if SlTrace.trace("trace_flags"):
            self.list_ckbuttons()
        self.Show()

    def on_exit(self):
        """ Close down window on program exit
        """
        SlTrace.lg("Closing down Trace Control Window")
        self.delete_tc_window()
        
    def update_loop(self):
        """ continue repeated tk.update() calls
        to enable window operation
        """
        loop_time = 50          # Loop recall time (msec)
        self.update()
        self.tc_mw.after(loop_time, self.update_loop)

    def update(self):
        if self.tc_mw is not None and self.tc_mw.winfo_exists():
            self.tc_mw.update()
        
    def sleep(self, sec):
        """ "sleep" for a number of sec
        without stoping tkinter stuff
        :sec: number of milliseconds to delay before returning
        """
        return  # TFD
        if self.tc_mw is None:
            return
        
        self.update()             # Insure at least one update
        now = time.time()
        end_time = now + sec
        while time.time() < end_time:
            if self.tc_mw is None:
                return
            
            self.update()
        return
    
    def mainloop(self):
        self.tc_mw.mainloop()
        
    def delete_tc_window(self):
        """ Process Trace Control window close
        """
        if self.tc_mw is not None:
            self.tc_mw.destroy()
            self.tc_mw = None
        
        if self.tcbase is not None and hasattr(self.tcbase, 'tc_destroy'):
            self.tcbase.tc_destroy()
                
    def enter_entry(self, event):
        flag = self.flag_by_cb[event.widget]
        old_level = SlTrace.getLevel(flag)
        tcb, flag = self.data_by_flag[flag]
                
    def select_button(self, event):
        flag = self.flag_by_cb[event.widget]
        tcb, flag = self.data_by_flag[flag]
        val = SlTrace.getLevel(flag)        # Variable doesn't seem to work for us
        val = not val                           # Keep value in strace
        self.set_trace_level(flag, val, change_cb=False)  # CB already set
        


    def list_ckbuttons(self):
        self.tcp.list_ckbuttons()

if __name__ == '__main__':
    app = wx.App()
    def report_change(flag, val, cklist=None):
        SlTrace.lg("changed: %s = %d" % (flag, val))
        new_val = SlTrace.getLevel(flag)
        SlTrace.lg("New val: %s = %d" % (flag, new_val))
        if cklist is not None:
            cklist.list_ckbuttons()
    
    root = wx.Frame(None)
    SlTrace.set_mw(root)
    ###frame = Frame(root)
    ###frame.pack()
    SlTrace.setProps()
    SlTrace.setFlags("flag1=t,flag2=f,flag3=t,flag4=10, flag5=20. flag6=abc")
    threshold = 5
    SlTrace.setLevel("tint1", 5)
    end_level = 100
    quit_set = False
    def our_quit(flag=None):
        """ Test for traceButton
        :flag: flag arg
        """
        global quit_set
        if flag is None:
            flag = "TBD"
        SlTrace.lg(f"our_quit({flag})")
        SlTrace.report("Quitting Program")
        root.destroy
        quit_set = True
        sys.exit()

        
    def test_int(flag, level=threshold, default=None):
        return  # TFD
        SlTrace.lg(f"Set {flag} to over {end_level} to quit")
        if SlTrace.trace(flag, threshold):
            SlTrace.lg(f"{flag} = {SlTrace.trace(flag)} >= {level}")
        else:
            SlTrace.lg(f"{flag} = {SlTrace.trace(flag)} < {level}")
        if quit_set or SlTrace.trace("tint1") > end_level:
            SlTrace.lg("Manual quit")
            sys.exit()
        SlTrace.traceButton("quit", our_quit)
                    
    tcw = TraceControlWindow(root, change_call=report_change)
    
    test_interval = False
    if test_interval:
        for i in range(end_level):
            test_int("tint1", default=2)
            tcw.sleep(1)
        
    app.MainLoop()    
    SlTrace.lg("End of test")