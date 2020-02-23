# command_file.py
"""
Base for independent control window
Provides a singleton which is universally accessible
Facilitates
    setting and display of game controls
    persistent storage of values
    window positioning / sizing
    Undo / Re-do of value setting
"""
from tkinter import *
import re
import os

from select_error import SelectError
from select_trace import SlTrace


    

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise SelectError('Not a recognized Boolean value %s' % v)
    
    
    
class SelectControlWindow(Toplevel):
    CONTROL_NAME_PREFIX = "window_control"
    DEF_WIN_X = 500
    DEF_WIN_Y = 300
    _instance = None         # Instance
    instance_no = 0         # Count instances
    
    def __init__(self, *args, **kwargs):
        SlTrace.lg("SelectControlWindow.__init__ %d" % SelectControlWindow.instance_no)
        
            
    def _init(self, play_control=None,
                control_prefix=None,
                title=None,
                display=True,
                new = False
                 ):
        """ Control attributes
        :title: window title
        """
        SelectControlWindow.instance_no += 1
        self.play_control = play_control
        if control_prefix is None:
            control_prefix = self.CONTROL_NAME_PREFIX
        self.control_prefix = control_prefix
        self.mw = Toplevel()
        self.mw.protocol("WM_DELETE_WINDOW", self.delete_window)
        if title is None:
            title = "Game Control"
        self.title = title
        self.vals = {}          # Current values if any
        self.ctls = {}          # Dictionary of field control widgets
        self.ctls_vars = {}     # Dictionary of field control widget variables
        self.display = display   # Done in instance, if at all
        self._is_displayed = False


    def __new__(cls, *args, **kwargs):
        """ Make a singleton
        """
        if cls._instance is None:
            cls._instance = super(SelectControlWindow, cls).__new__(cls)
            ###cls._instance._init(*args, **kwargs)
            cls._instance._init(**kwargs)
        return cls._instance
    
    
    def set_play_control(self, play_control):
        """ Link ourselves to the display
        """
        self.play_control = play_control
        
            
    def control_display(self):
        """ display /redisplay controls to enable
        entry / modification
        """
        if self._is_displayed:
            return
        
        top_frame = Frame(self.mw)
        top_frame.pack(side="top", fill="x", expand=True)
        self.top_frame = top_frame
        
        self.base_frame = top_frame     # Changed on use
        self.base_field = "game_control"
        self.mw.title(self.title)
        top_frame = Frame(self.mw)
        top_frame.pack(side="top", fill="x", expand=True)
        self.top_frame = top_frame
        
        
        bottom_frame = Frame(self.mw, borderwidth=2, relief=SUNKEN)
        bottom_frame.pack(side="bottom", expand=True)
        self.bottom_frame = bottom_frame
        
        self.set_fields(bottom_frame, "base", title="")
        self.set_button(field="set", label="Set", command=self.set)
        self.set_sep()
        self.set_button(field="Reset", label="Reset", command=self.reset)
        self.set_sep()
        self.set_button(field="Undo", label="Undo", command=self.undo)
        self.set_sep()
        self.set_button(field="Redo", label="Redo", command=self.redo)
        
        self.arrange_windows()
        self._is_displayed = True       # Mark as displayed
        

    """ Control functions for game control
    """
    def set(self):
        self.set_vals()

    
    def reset(self):
        self.set_vals()

    
    def undo(self):
        self.set_vals()

    
    def redo(self):
        self.set_vals()

    def get_val_from_ctl(self, field_name):
        """ Get value from field
        Does not set value
        :field_name: field name
        """
        field = field_name.lower()
        if field not in self.ctls_vars:
            raise SelectError("Command has no attribute %s" % field)
        value = self.ctls_vars[field].get()
        return value

    
    def set_vals(self):
        """ Read form, if displayed, and update internal values
        """
        for field in self.ctls_vars:
            self.set_val_from_ctl(field)

    def set_val_from_ctl(self, field_name):
        """ Set ctls value from field
        Also updates player value properties
        :field_name: field name
        """
        if not field_name in self.ctls_vars:
            raise SelectError("No field named %s" % field_name)
        ctl_var = self.ctls_vars[field_name]
        if ctl_var is None:
            raise SelectError("No variable for %s" % field_name)
        
        value = ctl_var.get()
        self.set_prop_val(field_name, value)


    def set_fields(self, base_frame, base_field, title=None):
        """ Set current control area
        :frame: current frame into which controls go
        :base_field: base for variables/widgets are stored
        """
        base_frame.pack()
        self.base_frame = base_frame
        self.base_field = base_field
        if title is None:
            title = base_field
        if title != "":
            wlabel = Label(base_frame, text=title, anchor=W)
            wlabel.pack(side="left", anchor=W)
            self.set_text("   ")
        

    def set_text(self, text, frame=None):
        """ Add text to current location/frame
        :text: text string to add
        :frame: frame into add default: base_frame
        """
        if frame is None:
            frame = self.base_frame
        wlabel = Label(frame, text=text, anchor=W)
        wlabel.pack(side="left", anchor=W)


    def set_sep(self, text=None, frame=None):
        """ Add default separator
        :text: text in separator
        :frame:  destination frame
        """
        if text is None:
            text = "  "
        if frame is None:
            frame = self.base_frame
        self.set_text(text, frame=frame)


    def set_vert_sep(self, frame=None):
        """ Add default vertical separator
        :frame:  destination frame
        """
        if frame is None:
            frame = self.base_frame
        sep_frame = Frame(frame)
        sep_frame.pack(side="top", anchor=N)
        self.set_text("  ", frame=sep_frame)



    def set_check_box(self, frame=None, field=None,
                        label=None, value=False,
                        command=None):
        """ Set up check box for field
        :field: local field name
        :label: button label - default final section of field name
        :value: value to set
        :command: function to call with new value when box changes
                    default: no call
        """
        if frame is None:
            frame = self.base_frame
        if label is None:
            label = field
            
        if label is not None:
            wlabel = Label(frame, text=label)
            wlabel.pack(side="left")
        content = BooleanVar()
        full_field = self.field_name(field)
        value = self.get_prop_val(full_field, value)
        content.set(value)
        cmd = None
        if command is not None:     # HACK - only works for ONE checkbox
            self.check_box_change_content = content
            self.check_box_change_callback = command
            cmd = self.check_box_change 
        widget =  Checkbutton(frame, variable=content, command=cmd)
        widget.pack(side="left", fill="none", expand=True)
        self.ctls[full_field] = widget
        self.ctls_vars[full_field] = content
        self.set_prop_val(full_field, value)

    def check_box_change(self):
        value = self.check_box_change_content.get()
        self.check_box_change_callback(value)

    def set_entry(self, frame=None, field=None,
                        label=None, value=None,
                        width=None):
        """ Set up entry
        :frame: containing frame
        :field: relative field name (after self.base_field)
        :label: field label default: no label
        :value: value to set, iff not in properties
                value's variable type is used as the entry content's type
        """
        if frame is None:
            frame = self.base_frame
        content = self.content_var(type(value))
        full_field = self.field_name(field)
        value = self.get_prop_val(full_field, value)
        content.set(value)
        if label is not None:
            wlabel = Label(frame, text=label)
            wlabel.pack(side="left")
            
        widget =  Entry(frame, textvariable=content, width=width)
        widget.pack(side="left", fill="none", expand=True)
        self.ctls[full_field] = widget
        self.ctls_vars[full_field] = content
        self.set_prop_val(full_field, value)


    def set_button(self, frame=None, field=None,
                        label=None, command=None):
        """ Set up check box for field
        :frame: containing frame, default self.base_frame
        :field: field name
        :label: button label - default: field
        :command: command to execute when button pressed
        """
        if frame is None:
            frame = self.base_frame
        if label is None:
            label = field
        widget =  Button(frame, text=label, command=command)
        widget.pack(side="left", fill="none", expand=True)
        full_field = self.field_name(field)
        self.ctls[field] = widget
        # No variable

    def field_name(self, *fields):
        """ Create basic field name from list
        :fields: set of field segments
        """
        field_name = self.base_field
        for field in fields:
            if field_name != "":
                field_name += "."
            field_name += field
        return field_name
            
    def win_size_event(self, event):
        """ Window sizing event
        """
        win_x = self.mw.winfo_x()
        win_y = self.mw.winfo_y()
        win_width = self.mw.winfo_width()
        win_height = self.mw.winfo_height()
        self.set_window_size(win_x, win_y, win_width, win_height)

        
    def set_window_size(self, x, y, width, height, change=False):
        """ Size our window
        :change: True force window resize
        """
        self.set_prop_val("win_x", x)
        self.set_prop_val("win_y", y)
        self.set_prop_val("win_width", width)
        self.set_prop_val("win_height", height)
        if SlTrace.trace("set_window_size("):
            if ( not hasattr(self, "prev_x") or self.prev_x != x
                 or not hasattr(self, "prev_y") or self.prev_y != y
                 or not hasattr(self, "prev_width") or self.prev_width != width
                 or not hasattr(self, "prev_height") or self.prev_height != height):
                SlTrace.lg("set_window_size( change=%d x=%d y=%d width=%d height=%d" % (change, x,y,width,height))
            self.prev_x = x 
            self.prev_y = y
            self.prev_width = width
            self.prev_height = height
        if change:
            geo_str = "%dx%d+%d+%d" % (width, height, x, y)
            self.mw.geometry(geo_str)
    
    def arrange_windows(self):
        """ Arrange windows
            Get location and size for properties if any
        """
        win_x = self.get_prop_val("win_x", self.DEF_WIN_X)
        if win_x < 0:
            win_x = 50
        win_y = self.get_prop_val("win_y", self.DEF_WIN_Y)
        if win_y < 0:
            win_y = 50
        
        win_width = self.get_prop_val("win_width", self.mw.winfo_width())
        win_height = self.get_prop_val("win_height", self.mw.winfo_height())
        self.set_window_size(win_x, win_y, win_width, win_height, change=True)
        self.mw.protocol("WM_DELETE_WINDOW", self.delete_window)
        self.mw.bind('<Configure>', self.win_size_event)
       
    
    def get_prop_key(self, name):
        """ Translate full control name into full Properties file key
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
        if prop_val is None or prop_val == "":
            return default
        if isinstance(default, bool):
            bv = str2bool(prop_val)
            return bv
        
        if isinstance(default, int):
            if prop_val == "":
                return 0
            try:
                prop_val = int(prop_val)
            except:
                try:
                    prop_val = float(prop_val)
                except:
                    prop_val = 0
                    
            return int(prop_val)
        
        if isinstance(default, float):
            if prop_val == "":
                return 0.
           
            return float(prop_val)
        else:
            return prop_val

    
    def get_val(self, name, default=None):
        """ Get current value, if any, else property value, if any,
        else default
        :name: field name
        :default: returned if not found
        """
        if name in self.vals:
            return self.vals[name]
        
        val = self.get_prop_val(name, default)
        return val


    def set_ctl(self, field_name, value):
        """ Set field, given value
        Updates field display and properties value
        :field_name: field name
        :value:        value to set
        """
        if field_name not in self.ctls_vars:
            raise SelectError("Control has no field variable %s" % field_name)
        ctl_var = self.ctls_vars[field_name]
        ctl_var.set(value)
        self.set_prop_val(field_name, value)


    def content_var(self, type):
        """ create content variable of the type val
        :type: variable type
        """
        if type == str:
            var = StringVar()
        elif type == int:
            var = IntVar()
        elif type == float:
            var = DoubleVar()
        elif type == bool:
            var = BooleanVar()
        else:
            raise SelectError("Unsupported content var type %s"
                              % type)
        
        return var


    def set_ctl_val(self, field_name, val):
        """ Set control field
        Creates field variable if not already present
        :field_name: field name
        :val: value to display
        """
        if field_name not in self.ctls_vars:
            content_var = self.content_var(type(val))
            self.ctls_vars[field_name] = content_var
        self.ctls_vars[field_name].set(val)
 


    def set_prop_val(self, name, value):
        """ Set property value as (string)
        :name: field name
        :value: default value, if not found
        """
        self.set_val(name, value)
        prop_key = self.get_prop_key(name)
        SlTrace.setProperty(prop_key, str(value))

    
    def set_val(self, name, value):
        """ Set field value
        :name: field name
        :value: value to set
        """
        self.vals[name] = value           # Update properties
        


    def destroy(self):
        """ Destroy window resources
        """
        if self.mw is not None:
            self.mw.destroy()
        self.mw = None
        
        
    def delete_window(self):
        """ Handle window deletion
        """
        if self.play_control is not None and hasattr(self.play_control, "close_score_window"):
            self.play_control.close_score_window()
        else:
            self.destroy()
            quit()
            SlTrace.lg("Properties File: %s"% SlTrace.getPropPath())
            SlTrace.lg("Log File: %s"% SlTrace.getLogPath())
            sys.exit(0)

        self.play_control = None

    
if __name__ == '__main__':
        
    root = Tk()
    root.withdraw()       # Hide main window

    SlTrace.setProps()
    cF = SelectControlWindow(title="SelectControlWindow Testing", display=False)
    cf2 = SelectControlWindow()
    cf2.control_display()
        
    root.mainloop()