# trace_control_window.py 27Jan2020

from tkinter import *
import atexit

import time

from select_trace import SlTrace

class TraceControlWindow(Toplevel):
    def __init__(self, tcbase=None, change_call=None):
        """ Trace flag dictionary
        :tcbase: - parent - call basis must have tc_destroy to be called if we close
        :change_call: - call with change flag, value, if present
        """
        self.standalone = False      # Set True if standalone operation
        if tcbase is None:
            SlTrace.lg("Standalone TraceControlWindow")
            root = Tk()
            frame = Frame(root)
            frame.pack()
            self.standalone = True
        self.tcbase = tcbase
        
        self.change_call = change_call

                    
        self.tc_mw = Toplevel()
        tc_x0 = 800
        tc_y0 = 100
        tc_w = 200
        tc_h = 200
        tc_geo = "%dx%d+%d+%d" % (tc_w, tc_h, tc_x0, tc_y0)
        self.tc_mw.geometry(tc_geo)
        self.tc_mw.title("Trace")
        top_frame = Frame(self.tc_mw)
        self.tc_mw.protocol("WM_DELETE_WINDOW", self.delete_tc_window)
        top_frame.pack(side="top", fill="both", expand=True)
        self.top_frame = top_frame
        tc_all_button = Button(master=self.top_frame, text="ALL", command=self.select_all)
        tc_all_button.pack(side="left", fill="both", expand=True)
        tc_none_button = Button(master=self.top_frame, text="NONE", command=self.select_none)
        tc_none_button.pack(side="left", fill="both", expand=True)
        tc_bpt_button = Button(master=self.top_frame, text="BPT", command=self.breakpoint)
        tc_bpt_button.pack(side="left", fill="both", expand=True)
        tc_frame = Frame(self.tc_mw)
        tc_frame.pack(side="top", fill="both", expand=True)
        self.tc_frame = tc_frame
        
        self.start = 0
        self.sb = Scrollbar(master=self.tc_frame, orient="vertical")
        max_width = 5
        min_height = 10
        t_height = min_height
        max_height = 20
        nfound = 0
        for flag in SlTrace.getAllTraceFlags():
            if len(flag) > max_width:
                max_width = len(flag)
            nfound += 1
        win_width = max_width
        if nfound < min_height:
            t_height = min_height
        if nfound > max_height:
            t_height = max_height
        text = Text(self.tc_frame, width=win_width, height=t_height, yscrollcommand=self.sb.set)
        self.sb.config(command=text.yview)
        self.sb.pack(side="right",fill="y")
        text.pack(side="top", fill="both", expand=True)
        self.flag_by_cb = {}             # Dictionary hashed on cb widget
        self.data_by_flag = {}
        for flag in sorted(SlTrace.getAllTraceFlags()):
            level = SlTrace.getLevel(flag)
            var = BooleanVar()
            var.set(level)
            fmt_text = "%-*s" % (max_width, flag)
            cb = Checkbutton(text, text=fmt_text, padx=0, pady=0, bd=0, variable = var)
            self.flag_by_cb[cb] = flag
            self.data_by_flag[flag] = (cb, flag, var)
            text.window_create("end", window=cb)
            text.insert("end", "\n")
            cb.bind("<Button-1>", self.select_button)
            ###cb.pack()
        self.list_ckbuttons()
        if self.standalone:
            atexit.register(self.on_exit)
            self.update_loop()

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
        self.tc_mw.update()
        self.tc_mw.after(loop_time, self.update_loop)

    def sleep(self, sec):
        """ "sleep" for a number of sec
        without stoping tkinter stuff
        :sec: number of milliseconds to delay before returning
        """
        now = time.time()
        end_time = now + sec
        while time.time() < end_time:
            self.tc_mw.update()
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

    def select_all(self):
        """ Select all known trace flags
        """
        for flag in sorted(SlTrace.getTraceFlags()):   # In display order
            self.set_trace_level(flag, 1)


    def select_none(self):
        """ Select all known trace flags
        """
        for flag in sorted(SlTrace.getTraceFlags()):   # In display order
            self.set_trace_level(flag, 0)


    def breakpoint(self):
        """ Force immediate breakpoint - enter debugger
        """
        import pdb
        SlTrace.lg("Breakpoint")
        pdb.set_trace()
                
    def select_button(self, event):
        flag = self.flag_by_cb[event.widget]
        cb, flag, var = self.data_by_flag[flag]
        val = SlTrace.getLevel(flag)        # Variable doesn't seem to work for us
        val = not val                           # Keep value in strace
        self.set_trace_level(flag, val, change_cb=False)  # CB already set
        
        
    def set_trace_level(self, flag, val, change_cb=True):
        """ Set trace level, changing Control button if requested
        :flag: - trace flag name
        :val: - value to set
        :change_cb: True(default) appropriately change the control
        """
        if flag not in self.data_by_flag:
            SlTrace.lg("set_trace_level(%s,%d) - flag has no check button" % (flag, val))
            return
         
        cb, flag, var = self.data_by_flag[flag]        
        if cb is None:
            SlTrace.lg("set_trace_level(%s,%d) - flag None check button" % (flag, val))
            return

        if change_cb:
            if val != 0:
                cb.select()
            else:
                cb.deselect()
                    
        SlTrace.lg("flag=%s, var=%s, val=%s" %(flag, var, val), "controls")
        SlTrace.setLevel(flag, val)
            
        if self.change_call is not None:
            self.change_call(flag, val)


    def list_ckbuttons(self):
        cb_flags = sorted(self.data_by_flag.keys())
        for flag in cb_flags:
            var = self.data_by_flag[flag][2]
            print("flag=%s var=%s val=%d" % (flag, var, var.get()))

if __name__ == '__main__':
    def report_change(flag, val, cklist=None):
        SlTrace.lg("changed: %s = %d" % (flag, val))
        new_val = SlTrace.getLevel(flag)
        SlTrace.lg("New val: %s = %d" % (flag, new_val))
        if cklist is not None:
            cklist.list_ckbuttons()
    
    root = Tk()

    frame = Frame(root)
    frame.pack()
    SlTrace.setProps()
    SlTrace.setFlags("flag1=1,flag2=0,flag3=1,flag4=0, flag5=1, flag6=1")
    app = TraceControlWindow(frame, change_call=report_change)
    app.mainloop()
