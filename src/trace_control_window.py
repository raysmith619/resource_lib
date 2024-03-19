# trace_control_window.py 27Jan2020
import sys
from tkinter import *
import atexit

import time

from select_trace import SlTrace
from crs_funs import str2val

class TraceControlWindow(Toplevel):
    def __init__(self, tcbase=None, change_call=None):
        """ Trace flag dictionary
        :tcbase: - parent - call basis must have tc_destroy to be called if we close
        :change_call: - call with change flag, value, if present
        """
        self.flag_by_cb = {}             # Dictionary hashed on cb widget
        self.data_by_flag = {}
        self.standalone = False      # Set True if standalone operation
        if tcbase is None:
            SlTrace.lg("Standalone TraceControlWindow")
            root = Tk()
            frame = Frame(root)
            frame.pack()
            self.standalone = True
            root.withdraw()
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
        top_frame.pack(side="top", fill="both", expand=False)
        self.top_frame = top_frame
        tc_all_button = Button(master=self.top_frame, text="SET ALL", command=self.select_all)
        tc_all_button.pack(side="left", fill="both", expand=False)
        tc_none_button = Button(master=self.top_frame, text="NONE", command=self.select_none)
        tc_none_button.pack(side="left", fill="both", expand=False)
        tc_bpt_button = Button(master=self.top_frame, text="BPT", command=self.breakpoint)
        tc_bpt_button.pack(side="left", fill="both", expand=False)
        self.show_list_which = "ALL"
        self.show_list_variable = StringVar()
        self.show_list_variable.set("Show SET")
        tc_show_button = Button(master=self.top_frame, textvariable=self.show_list_variable,
                                command=self.show_list)
        tc_show_button.pack(side="left", fill="none", expand=False)
        self.tc_show_button = tc_show_button
        tc_frame = Frame(self.tc_mw)
        tc_frame.pack(side="top", fill="both", expand=True)
        self.tc_frame = tc_frame
        self.tc_text_frame = None           # So we can destroy / resetup in create_flags_region
        self.flags_text = None
        self.sb = None
        self.create_flags_region(flags=SlTrace.getAllTraceFlags())
        if SlTrace.trace("trace_flags"):
            self.list_ckbuttons()
        
    def create_flags_region(self, flags=None):
        if self.tc_text_frame is not None:
            self.tc_text_frame.pack_forget()
            self.tc_text_frame.destroy()
            self.tc_text_frame = None
            
        if self.sb is not None:
            self.sb.destroy()
        self.update()                           # Show progress
        self.tc_text_frame = Frame(self.tc_frame)
        self.tc_text_frame.pack(side="top", fill="both", expand=True)

        self.start = 0
        self.sb = Scrollbar(master=self.tc_text_frame, orient="vertical")
        max_width = 5
        min_height = 10
        t_height = min_height
        max_height = 20
        nfound = 0
        for flag in flags:
            val = SlTrace.getLevel(flag)
            width = len(flag)
            if callable(val):
                val_len = 5
            elif type(val) == bool:
                val_len = 2
            else:
                val_len = len(str(val))
            width += val_len
            if width > max_width:
                max_width = width
            nfound += 1
        win_width = max_width
        if nfound < min_height:
            t_height = min_height
        if nfound > max_height:
            t_height = max_height
            
        text = Text(self.tc_text_frame, width=win_width, height=t_height,
                    yscrollcommand=self.sb.set,
                    state=DISABLED)
        self.sb.config(command=text.yview)
        self.sb.pack(side="right",fill="y")
        text.pack(side="top", fill="both", expand=True)
        self.update()                           # Show progress
        self.flag_by_cb = {}             # Dictionary hashed on cb widget
        self.data_by_flag = {}
        for flag in sorted(flags):
            level = SlTrace.getLevel(flag)
            if type(level) == bool:
                var = BooleanVar()
                var.set(level)
                ####fmt_text = "%-*s" % (max_width, flag)
                fmt_text = flag
                cb = Checkbutton(text, text=fmt_text, padx=0, pady=0, bd=0, variable = var, bg="white")
                self.flag_by_cb[cb] = flag
                self.data_by_flag[flag] = (cb, flag, var)
                text.config(state=NORMAL)
                text.window_create("end", window=cb)
                text.insert("end", "\n")
                text.config(state=DISABLED)
                cb.bind("<Button-1>", self.select_button)
            elif type(level) == int or type(level) == float or type(level) == str:
                if type(level) == int:
                    var = IntVar()
                elif type(level) == float:
                    var = DoubleVar()
                elif type(level) == str:
                    var = StringVar()
                var.set(level)
                var_width = len(str(level)) + 2
                text_var = StringVar()
                text_var.set(f"{level:{var_width}}")
                ####fmt_text = "%-*s" % (max_width, flag)
                fmt_text = flag
                ent = Entry(text, width=var_width, textvariable=text_var)
                self.flag_by_cb[ent] = flag
                self.data_by_flag[flag] = (ent, flag, text_var)     # field is what we need
                text.config(state=NORMAL)
                text.window_create("end", window=ent)
                text.insert("end", fmt_text)
                text.insert("end", "\n")
                text.config(state=DISABLED)
                ent.bind("<Return>", self.enter_entry)
            elif callable(level):
                fmt_text = "%-*s" % (max_width, flag)
                btn = Button(text, text=flag, command=level)
                self.flag_by_cb[btn] = flag
                self.data_by_flag[flag] = (btn, flag, None)     # field is what we need
                text.config(state=NORMAL)
                text.window_create("end", window=btn)
                text.insert("end", "\n")
                
            ###cb.pack()
        self.update()                           # Show progress
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

    def show_list(self):
        """ Select buttons to show
        """
        if self.show_list_which == "ALL":
            self.show_list_which = "JUST_SET"
            self.show_list_variable.set("Show ALL")
            just_flags = []
            for flag in SlTrace.getTraceFlags():
                val = SlTrace.getLevel(flag)
                if type(val) != bool:
                    just_flags.append(flag) # Include all non-boolean
                elif val:
                    just_flags.append(flag)
        else:
            self.show_list_which = "ALL"
            self.show_list_variable.set("Show SET")
            just_flags = SlTrace.getTraceFlags()
            
        self.create_flags_region(just_flags)
        
    def select_all(self):
        """ Select all known trace flags
        """
        for flag in sorted(SlTrace.getTraceFlags()):   # In display order
            if type(self.getLevel(flag)) == bool:
                self.set_trace_level(flag, True)


    def select_none(self):
        """ Select all known trace flags
        """
        for flag in sorted(SlTrace.getTraceFlags()):   # In display order
            if type(self.getLevel(flag)) == bool:
                self.set_trace_level(flag, False)

    def getLevel(self, flag):
        return SlTrace.getLevel(flag)
    
    def breakpoint(self):
        """ Force immediate breakpoint - enter debugger
        """
        import pdb
        SlTrace.lg("Breakpoint")
        pdb.set_trace()
                
    def enter_entry(self, event):
        flag = self.flag_by_cb[event.widget]
        old_level = SlTrace.getLevel(flag)
        _, flag, text_var = self.data_by_flag[flag]
        entry_text = text_var.get()
        new_level = str2val(entry_text, old_level)        
        self.set_trace_level(flag, new_level, change_cb=False)  # No select for Entry
                
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

        if change_cb and hasattr(cb, "select"):
            if val != 0:
                cb.select()
            else:
                cb.deselect()
                    
        SlTrace.lg("flag=%s, var=%s, val=%s" %(flag, var, val), "trace_flags")
        SlTrace.setLevel(flag, val)
            
        if self.change_call is not None:
            self.change_call(flag, val)


    def list_ckbuttons(self):
        cb_flags = sorted(self.data_by_flag.keys())
        for flag in cb_flags:
            var = self.data_by_flag[flag][2]
            SlTrace.lg(f"flag={flag} var={var} val={var.get()}")

if __name__ == '__main__':
    def report_change(flag, val, cklist=None):
        SlTrace.lg("changed: %s = %d" % (flag, val))
        new_val = SlTrace.getLevel(flag)
        SlTrace.lg("New val: %s = %d" % (flag, new_val))
        if cklist is not None:
            cklist.list_ckbuttons()
    
    root = Tk()
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
        SlTrace.lg(f"Set {flag} to over {end_level} to quit")
        if SlTrace.trace(flag, threshold):
            SlTrace.lg(f"{flag} = {SlTrace.trace(flag)} >= {level}")
        else:
            SlTrace.lg(f"{flag} = {SlTrace.trace(flag)} < {level}")
        if quit_set or SlTrace.trace("tint1") > end_level:
            SlTrace.lg("Manual quit")
            sys.exit()
        SlTrace.traceButton("quit", our_quit)
                    
    app = TraceControlWindow(change_call=report_change)
    
    for i in range(end_level):
        test_int("tint1", default=2)
        app.sleep(1)
        
        
    SlTrace.lg("End of test")