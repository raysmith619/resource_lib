#select_window.py 19Sep2018
"""
Program Level Menu control
 From PoolWindow
"""
import sys
import os
from tkinter import *
from select_trace import SlTrace
from trace_control_window import TraceControlWindow
from arrange_control import ArrangeControl

# Here, we are creating our class, Window, and inheriting from the Frame
# class. Frame is a class from the tkinter module. (see Lib/tkinter/__init__)
class SelectWindow(Frame):
    CONTROL_NAME_PREFIX = "play_control"

    def __deepcopy__(self, memo=None):
        """ provide deep copy by just passing shallow copy of self,
        avoiding tkparts inside sel_area
        """
        SlTrace.lg("SelectWindow __deepcopy__", "copy")
        return self
            
        
    # Define settings upon initialization. Here you can specify
    ###@profile    
    def __init__(self,
                 master=None,
                 title=None,
                 control_prefix=None,
                 pgmExit=None,
                 file_open=None,
                 file_save=None,                 
                 cmd_proc=False,
                 cmd_file=None,
                 arrange=None,
                 arrange_selection=False,
                 game_control=None,
                 games=[],          # text, proc pairs
                 actions=[],
                 ):
        """ Setup window controls
        :arrange_selection: - incude arrangement controls
                        default: False
        """
        # parameters that you want to send through the Frame class. 
        Frame.__init__(self, master)   

        #reference to the master widget, which is the tk window                 
        self.title = title
        self.master = master
        self.file_open = file_open
        self.file_save = file_save
        if control_prefix is None:
            control_prefix = SelectWindow.CONTROL_NAME_PREFIX
        self.control_prefix = control_prefix
        self.arrange = arrange
        if arrange is not None:
            arrange_selection = False
        self.arrange_selection = arrange_selection
        self.pgmExit = pgmExit
        self.game_control = game_control
        master.protocol("WM_DELETE_WINDOW", self.pgm_exit)
        self.games = games
        self.actions = actions
        self.tc = None          # Trace control
        self.arc = None         # Arrangement control
        self.arc_call_d = {}     # arc call back functions
        self.cmd_proc = cmd_proc    # Setup command file processing
        self.cmd_file = cmd_file    # if not None, execute this cmd file
        #with that, we want to then run init_window, which doesn't yet exist
        self.init_window()

        
    #Creation of init_window
    def init_window(self):

        # changing the title of our master widget 
        if self.title is not None:
            self.master.title(self.title)

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=False)

        # creating a menu instance
        menubar = Menu(self.master)
        self.menubar = menubar      # Save for future reference
        self.master.config(menu=menubar)

        # create the file object)
        file_open_cmd = self.file_open
        if file_open_cmd is None:
            file_open_cmd = self.File_Open_tbd
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=file_open_cmd)
        file_save_cmd = self.file_save
        if file_save_cmd is None:
            file_save_cmd = self.File_Save_tbd
        filemenu.add_command(label="Save", command=file_save_cmd)
        filemenu.add_separator()
        filemenu.add_command(label="Log", command=self.LogFile)
        filemenu.add_command(label="Properties", command=self.Properties)
        filemenu.add_separator()
        ###filemenu.add_comand(label="Cmd", command=self.command_proc)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.pgmExit)
        menubar.add_cascade(label="File", menu=filemenu)
        if self.arrange is not None:         # Explicit arrange control cmd
            menubar.add_command(label="Arrange",
                                 command=self.arrange)
                            
        elif self.arrange_selection:    # Arrange control - optoinal
            menubar.add_command(label="Arrange",
                                 command=self.arrange_control)

                                # Trace control
        menubar.add_command(label="Trace", command=self.trace_control)
        self.arrange_windows()
        self.master.bind( '<Configure>', self.win_size_event)


    def get_game_control(self):
        """ Retrieve game control to pass to SelectPlay
        """
        return self.game_control
    

    def win_size_event(self, event):
        """ Window sizing event
        """
        win_x = self.master.winfo_x()
        win_y = self.master.winfo_y()
        win_width = self.master.winfo_width()
        win_height = self.master.winfo_height()
        self.set_prop_val("win_x", win_x)
        self.set_prop_val("win_y", win_x)
        self.set_prop_val("win_width", win_width)
        self.set_prop_val("win_height", win_height)
    
    def arrange_windows(self):
        """ Arrange windows
            Get location and size for properties if any
        """
        win_x = self.get_prop_val("win_x", 50)
        if win_x < 0 or win_x > 1400:
            win_x = 50
        win_y = self.get_prop_val("win_y", 50)
        if win_y < 0 or win_y > 1400:
            win_y = 50
        
        win_width = self.get_prop_val("win_width", self.master.winfo_width())
        win_height = self.get_prop_val("win_height", self.master.winfo_height())
        geo_str = "%dx%d+%d+%d" % (win_width, win_height, win_x, win_y)
        self.master.geometry(geo_str)
        
    def geometry(self, geo):
        """ Adjust parent window size/location
        """
        self.master.geometry(geo)
    
    def get_prop_key(self, name):
        """ Translate full  control name into full Properties file key
        """        
        key = self.control_prefix + "." + name
        return key

    def get_prop_val(self, name, default):
        """ Get property value as (string)
        :name: field name
        :default: default value, if not found
        :returns: "" if not found
        """
        prop_key = self.get_prop_key(name)
        prop_val = SlTrace.getProperty(prop_key)
        if prop_val is None:
            return default
        
        if isinstance(default, int):
            if prop_val == "":
                return 0
           
            return int(prop_val)
        elif isinstance(default, float):
            if prop_val == "":
                return 0.
           
            return float(prop_val)
        else:
            return prop_val

    def set_prop_val(self, name, value):
        """ Set property value as (string)
        :name: field name
        :value: default value, if not found
        """
        prop_key = self.get_prop_key(name)
        SlTrace.setProperty(prop_key, str(value))
        
        
    def pgm_exit(self):
        if self.pgmExit is not None:
            self.pgmExit()
        else:
            sys.exit()    
            
    def File_Open_tbd(self):
        print("File_Open_menu to be determined")

    def File_Save_tbd(self):
        print("File_Save_menu to be determined")

    def add_menu(self):
        """ Add pull-down menu to top menu bar
        :label: pull-down label
        :returns: menubar, filemenu to which one can
            filemenu.add_command(label="Log", command=self.LogFile)
            filemenu.add_separator()
            ...
            menubar.add_cascade(label="menu-title", menu=filemenu)
           
        """
        filemenu = Menu(self.menubar, tearoff=0)
        return self.menubar, filemenu
 
    def add_menu_command(self, label=None, call_back=None):
        """ Add simple menu command to top menu
        :label: command label
        :call_back: function to be called when selected
        """
        self.menubar.add_command(label=label, command=call_back)

    def add_menu_separator(self):
        """ Add simple menu separator to top menu
        """
        self.menubar.add_separator()


    def command_proc(self):
        """ Setup command processing options / action
        """
        
        
    def get_arc(self):
        """ Return reference to arrange control
        """
        return self.arc
    
    
    def LogFile(self):
        print("Display Log File")
        abs_logName = SlTrace.getLogPath()
        SlTrace.lg("Log file  %s"
                    % abs_logName)
        ###osCommandString = "notepad.exe %s" % abs_propName
        ###os.system(osCommandString)
        import subprocess as sp
        programName = "notepad.exe"
        sp.Popen([programName, abs_logName])
    
    
    def Properties(self):
        print("Display Properties File")
        abs_propName = SlTrace.defaultProps.get_path()
        SlTrace.lg("properties file  %s"
                    % abs_propName)
        ###osCommandString = "notepad.exe %s" % abs_propName
        ###os.system(osCommandString)
        import subprocess as sp
        programName = "notepad.exe"
        sp.Popen([programName, abs_propName])
        
        
    def select_all(self):
        if self.tc is None:
            self.select_trace()
        self.tc.select_all()
        
            
    def select_none(self):
        if self.tc is None:
            self.select_trace()
        self.tc.select_none()

        

    def arrange_control(self):
        """ Create arrangement window
        :returns: ref to ArrangeControl object
        """
        if self.arc is not None:
            self.arc.delete_window()
            self.arc = None
        
        self.arc = ArrangeControl(self, title="Arrange")
        for callname, callfn in self.arc_call_d.items():     # Enable any call back functions
            self.arc.set_call(callname, callfn)
        return self.arc

    def ctl_list(self, ctl_name, selection_list):
        return self.arc.ctl_list(ctl_name, selection_list)


    def get_ctl_entry(self, name):
        """ Get control value.  If none return default
        """
        if self.arc is None:
            return None
        return self.arc.get_entry_val(name)
 

    def get_current_val(self, name, default=None):
        """ Get control value.  If none return default
        """
        if self.arc is None:
            return default
        return self.arc.get_current_val(name, default)


    def get_component_val(self, name, comp_name, default=None):
        """ Get component value of named control
        Get value from widget, if present, else use entry value
        """
        if self.arc is None:
            return default
        return self.arc.get_component_val(name, comp_name, default)

    def get_component_next_val(self, base_name,
                            nrange=50,
                            inc_dir=1,
                            default_value=None):
        """ Next value for this component
        :control_name: control name
        :comp_name: component name
        :nrange: - number of samples for incremental
        :default_value: default value
        """
        return self.arc.get_component_next_val(base_name,
                                nrange=nrange, inc_dir=inc_dir, default_value=default_value)


    def get_inc_val(self, name, default):
        """ Get inc value.  If none return default
        """
        if self.arc is None:
            return default
        return self.arc.get_inc_val(name, default)
 

    def set_current_val(self, name, val):
        """ Set current value.
        """
        if self.arc is None:
            return
        return self.arc.set_current_val(name, val)
 

    def set_component_val(self, name, comp_name, val):
        """ Set current value.
        """
        if self.arc is None:
            return
        return self.arc.set_component_val(name, comp_name, val)
        
    
    def set_call(self, name, function):
        """ Set for call back from arrange control
           1. If arc present via arc
           2. Else store for later enabling when arc is created
        """
        if self.arc is not None:
            self.arc.set_call(name, function)
        else:
            self.arc_call_d[name] = function
 
        

    def trace_control(self):
 
        def report_change(flag, val, cklist=None):
            SlTrace.lg("changed: %s = %d" % (flag, val), "controls")
            new_val = SlTrace.getLevel(flag)
            SlTrace.lg("New val: %s = %d" % (flag, new_val), "controls")
            if cklist is not None:
                cklist.list_ckbuttons()
        
        if self.tc is not None:
            self.tc.delete_tc_window()
            self.tc = None
        
        self.tc = TraceControlWindow(self, change_call=report_change)


    def tc_destroy(self):
        """ Called if TraceControlWindow window closes
        """
        self.tc = None


    def update_form(self):
        """ Update any field changes
        """
        if self.arc is not None:
            self.arc.update_form()
#########################################################################
#          Self Test                                                    #
#########################################################################
if __name__ == "__main__":
    from trace_control_window import TraceControlWindow    
        
    # root window created. Here, that would be the only window, but
    # you can later have windows within windows.
    mw = Tk()
    SlTrace.lg("Startup")
    
    def user_exit():
        print("user_exit")
        print("Calling SlTrace.onexit()")
        SlTrace.onexit()
        exit()
    
    def user_file_open():
        print("user_file_open")
    
    def user_file_save():
        print("user_file_save")
            
            
    SlTrace.setProps()
    set_flags = True
    set_flags = False
    if set_flags:
        SlTrace.lg("setFlags")
        SlTrace.setFlags("flag1=1,flag2=0,flag3=1,flag4=0, flag5=1, flag6=1")
    else:
        SlTrace.lg("no setFlags")
        
    mw.geometry("400x300")
    
    #creation of an instance
    app = SelectWindow(mw,
                    title="select_window Testing",
                    pgmExit=user_exit,
                    arrange_selection=False,
                    file_open = user_file_open,
                    file_save = user_file_save,
                    )

    show_trace = True
    show_trace = False
    if show_trace:
        app.trace_control()

    
    #mainloop 
    mw.mainloop()  

