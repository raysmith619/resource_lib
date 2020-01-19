# variable_control.py 06Jan2020
"""
Simple Control and Display of program variables
Adapted from trace_control.py/TraceControl
Essentially presents a scrollable list of variable names and values
Uses select_control/SelectControl to store and manipulate variable contents

"""
from tkinter import *
from select_trace import SlTrace
from select_error import SelectError

from select_control import SelectControl
from tkinter.constants import TOP

class VariableControl(Toplevel):
    def __init__(self, master=None, window_exit=None, var_ctl=None, update_call=None):
        """ Trace flag dictionary
        :window_exit: - If present, called upon window delete
        :var_ctl: variable control object
        :update_call: call after update default: no call
        """
        SlTrace.lg("VariableControl")
        if master is None:
            master = Toplevel()            
            SlTrace.lg("VariableControl - new master")
        self.vc_mw = master
        self.window_exit = window_exit
        
        if var_ctl is None:
            var_ctl = SelectControl()
        self.var_ctl = var_ctl
        self.update_call = update_call

        vc_x0 = 800
        vc_y0 = 100
        vc_w = 200
        vc_h = 200
        vc_geo = f"{vc_w}x{vc_h}+{vc_x0}+{vc_y0}"
        self.vc_mw.geometry(vc_geo)
        self.vc_mw.title("Variable Control")
        top_frame = Frame(self.vc_mw)
        self.vc_mw.protocol("WM_DELETE_WINDOW", self.delete_vc_window)
        top_frame.pack(side="top", fill="both", expand=True)
        self.top_frame = top_frame
        vc_update_button = Button(master=self.top_frame, text="Update", command=self.var_update)
        vc_update_button.pack(side="left", fill="both", expand=True)
        vc_undo_button = Button(master=self.top_frame, text="Undo", command=self.var_undo)
        vc_undo_button.pack(side="left", fill="both", expand=True)
        vc_redo_button = Button(master=self.top_frame, text="Redo", command=self.var_redo)
        vc_redo_button.pack(side="left", fill="both", expand=True)
        vc_frame = Frame(self.vc_mw)
        vc_frame.pack(side="top", fill="both", expand=True)
        self.vc_frame = vc_frame
        
        self.start = 0
        max_width = 5
        min_height = 10
        t_height = min_height
        max_height = 20
        nfound = 0
        names = self.var_ctl.get_var_names(label=True)
        for var_name in names:
            entry_type = self.var_ctl.get_entry_type(var_name)
            var = self.var_ctl.get_var(var_name)
            val = self.var_ctl.get_val(var_name)
            if entry_type == "internal":
                continue
            if entry_type == "label":
                len_var = len(val)
            elif isinstance(var, BooleanVar):
                len_var = len(var_name) + 2
                nfound += 1
            else:
                continue
            if len_var > max_width:
                max_width = len_var
        win_width = max_width
        if nfound < min_height:
            t_height = min_height
        if nfound > max_height:
            t_height = max_height
        ###text = Text(self.vc_frame, width=win_width, height=t_height, yscrollcommand=self.sb.set)
        ###self.sb = Scrollbar(master=self.vc_frame, orient="vertical")
        var_frame = Frame(self.vc_frame, width=200, height=300)
        var_frame.pack()
        canvas = Canvas(var_frame, width=200, height=300, scrollregion=(0,0, 200, 300))
        vbar = Scrollbar(var_frame, orient=VERTICAL)
        vbar.pack(side=RIGHT, fill=Y)
        canvas.config(yscrollcommand=vbar.set)
        canvas.pack(side="top", fill="both", expand=True)
        ###self.sb.pack(side="right",fill="y")
        var_frame = canvas
        canvas.configure(scrollregion = (canvas.bbox(ALL)))
        for var_name in self.var_ctl.get_var_names(label=True):
            entry_type = self.var_ctl.get_entry_type(var_name)
            var = self.var_ctl.get_var(var_name)
            val = self.var_ctl.get_val(var_name)
            if entry_type == "internal":
                continue
            if entry_type == "label":
                fmt_text = "%-*s" % (max_width, val)
                lb = Label(var_frame, text=fmt_text, background="white")
                lb.pack(side=TOP)
            elif isinstance(var, BooleanVar):
                entry_frame = Frame(var_frame)
                entry_frame.pack(side=TOP)
                fmt_text = "%-*s" % (max_width, val)
                self.var_ctl.make_val(var_name, val, repeat=True)
                lb = Label(entry_frame, text=var_name)
                lb.pack(side=LEFT)
                wj = Checkbutton(entry_frame, variable=self.var_ctl.get_var(var_name))
                wj.pack(side=RIGHT)
                self.var_ctl.add_widget(var_name, wj, repeat=True)
            elif isinstance(var, (IntVar, DoubleVar, StringVar)):
                entry_frame = Frame(var_frame)
                entry_frame.pack(side=TOP)
                lb = Label(entry_frame, text=var_name)
                lb.pack(side=LEFT)
                self.var_ctl.make_val(var_name, val, repeat=True, textvar=True)
                wj = Entry(entry_frame, width=10, textvariable=self.var_ctl.get_textvar(var_name))
                wj.pack(side=RIGHT)
                self.var_ctl.add_widget(var_name, wj, repeat=True)
                
            else:
                SlTrace.lg(f"variable({var_name} type({type(var)}) is not yet supported")    

    def destroy(self):
        """ Destroy us
        """
        SlTrace.lg("VariableControl.destroy")
        self.delete_vc_window()
            
    def delete_vc_window(self):
        """ Process Trace Control window close
        """
        SlTrace.lg("VariableControl.delete_vc_window")
        if self.vc_mw is not None:
            self.vc_mw.destroy()
            self.vc_mw = None
        
        if self.window_exit is not None:
            self.window_exit()
                
    def select_button(self, event):
        SlTrace.lg(f"VariableControl.select_button {event}")
        flag = self.flag_by_cb[event.widget]
        cb, flag, var = self.data_by_flag[flag]
        val = self.strace.getLevel(flag)        # Variable doesn't seem to work for us
        val = not val                           # Keep value in strace
        self.set_trace_level(flag, val, change_cb=False)  # CB already set

                        
    def set_val(self, name, value, no_change=False):
        """ Set variable value
        :name: variable name
        :value: value to set
        :no_change: don't 
        """
        SlTrace.lg(f"VariableControl set_val name:{name}, value={value}")
        self.var_ctl.set_val(name, value, no_change=no_change)
        return value
        

    def var_update(self):
        """ Update all variables from input fields
        if update_call call self.update_call(self) AFTER update
        """
        SlTrace.lg(f"VariableControl.var_update")
        self.var_ctl.update_settings()
        if self.update_call is not None:
            self.update_call(self)


    def var_undo(self):
        """ Select all known trace flags
        """
        SlTrace.lg(f"VariableControl.var_undo")
        self.var_ctl.undo_settings()


    def var_redo(self):
        """ undo last var_undo
        """
        SlTrace.lg(f"VariableControl.var_redo")
        self.var_ctl.redo_settings()
                


    def list_vars(self):
        self.var_ctl.list_vars()

if __name__ == '__main__':
    def report_change(flag, val, cklist=None):
        SlTrace.lg("changed: %s = %d" % (flag, val))
        new_val = SlTrace.getLevel(flag)
        SlTrace.lg("New val: %s = %d" % (flag, new_val))
        if cklist is not None:
            cklist.list_ckbuttons()

    cF = None
    vC = None
    

    def set_controls():
        global cF
        global vC
        
        cF = SelectControl()        # Ref to singleton
        if vC is not None:
            vC.destroy()
            vC = None
        vC = VariableControl(var_ctl=cF, update_call=update_call)
        
    def update_call(ctl = None):
        if ctl is not None:
            ctl.var_ctl.list_vals("after update")
               
    mw = Tk()
    # creating a menu instance
    # changing the title of our master widget 
    mw.title("self test")
    top_frame = Frame(mw)
    # allowing the widget to take the full space of the root window
    top_frame.pack(fill=BOTH, expand=1)
    menubar = Menu(top_frame)
    mw.config(menu=menubar)
    menubar.add_command(label="contols", command=set_controls)


    SlTrace.setProps()
    cF = SelectControl()
    cF.make_label("Puzzle Size")
    ncol = cF.make_val("ncol", 4)     # default, override from properties
    nrow = cF.make_val("nrow", 5)
    size = cF.make_val("size", 123.456, textvar=True)
    cF.make_label("Run Speed")
    cF.make_label("Display Time")
    cF.make_val("Display_time", .5)            # Display time, None - no display
    
    SlTrace.lg(f"After make_val ncol={ncol} nrow={nrow} size={size}")    
    cF.list_vals("Pre-command line parsing")
    vC = VariableControl(var_ctl=cF, update_call=update_call)
        
    mw.mainloop()