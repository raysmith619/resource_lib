# select_control_window.py
"""
Base for independent control window
NOTE: for Singleton version see select_control_window_singleton.py
Facilitates
    setting and display of game controls
    persistent storage of values
    window positioning / sizing
    Undo / Re-do of value setting
"""
from tkinter import *
import time

from crs_funs import str2bool, str2val
from select_error import SelectError
from select_trace import SlTrace
from select_input import SelectInput

    

def content_var_type(val):
    """ Convert content_variable instance
    into variable type
    :var:   variable type
    """
    if isinstance(val, StringVar):
        val_type = str
    elif isinstance(val, IntVar):
        val_type = int
    elif isinstance(val, DoubleVar):
        val_type = float
    elif isinstance(val, BooleanVar):
        val_type = bool
    else:
        raise SelectError(f"Unsupported content var type {val}")
    return val_type
    

def content_var(val):
    """ create content variable of the type of val
    :val:   value to initialize content
    """
    val_type = type(val)
    if val_type == str:
        var = StringVar()
    elif val_type == int:
        var = IntVar()
    elif val_type == float:
        var = DoubleVar()
    elif val_type == bool:
        var = BooleanVar()
    else:
        raise SelectError(f"Unsupported content var val_type {val_type}")
    var.set(val)
    return var
    
    
class SelectControlWindow(Toplevel):
    CONTROL_NAME_PREFIX = "window_control"
    DEF_WIN_X = 500
    DEF_WIN_Y = 300
    _instance = None         # Instance
    instance_no = 0         # Count instances

    @classmethod
    def reset_class(cls):
        """ Reset to gone
        Facilitate regeneration of window
        """
        cls._instance = None
    
    def __init__(self, mw=None,
                play_control=None,
                control_prefix=None,
                title=None,
                display=True,
                set_cmd=None,
                win_x=None,
                win_y=None,
                win_width=None,
                win_height=None,
                enter_command=None,
                 ):
        """ Control attributes
        :play_control:        special for game play
        :control_prefix: prefix for properties file entries
        :title: window title
        :set_cmd: function, if present, to call on button press
        :win_x:  New window x position default: use properties entry
        :win_y:  New window y position default: use properties entry
        :win_width: New window width default: use properties entry
        :win_height: New window height default: use properties entry
        :enter_command: if present, the common entry element keyboard ENTER command
        """
        SelectControlWindow.instance_no += 1
        self.play_control = play_control
        if control_prefix is None:
            control_prefix = self.CONTROL_NAME_PREFIX
        self.control_prefix = control_prefix
        if mw is None:
            mw = Toplevel()
        self.mw = mw
        self.update()           # TFD debugging display
        self.mw.protocol("WM_DELETE_WINDOW", self.delete_window)    
        if title is None:
            title = "Game Control"
        self.title = title
        self.vals = {}          # Current values if any
        self.ctls_labels = {}   # ctl labels (if one) by field
        self.ctls = {}          # Dictionary of field control widgets
        self.ctls_vars = {}     # Dictionary of field control widget variables
        self.display = display   # Done in instance, if at all
        self.set_cmd = set_cmd
        self.enter_command = enter_command
        ndim_spec = 0
        if win_x is not None:
            self.set_prop_val("win_x", win_x)
            ndim_spec += 1
        if win_y is not None:
            self.set_prop_val("win_y", win_y)
            ndim_spec += 1
        if win_width is not None:
            self.set_prop_val("win_width", win_width)
            ndim_spec += 1
        if win_height is not None:
            self.set_prop_val("win_height", win_height)
            ndim_spec += 1
        if ndim_spec > 0:
            self.arrange_windows()
        self._is_displayed = False
        
    def report(self, msg):
        """ Report, via popup window
        :msg:
        """
        SlTrace.report(f"{self.control_prefix}: {msg}")
            
    def set_play_control(self, play_control):
        """ Link ourselves to the display
        """
        self.play_control = play_control
        
            
    def control_display(self):
        """ display /redisplay controls to enable
        entry / modification
        """
        top_frame = Frame(self.mw)
        top_frame.pack(side="top", fill="x", expand=True)
        self.top_frame = top_frame
        
        self.base_frame = top_frame     # Changed on use
        self.base_field = "game_control"
        self.mw.title(self.title)
        top_frame = Frame(self.mw)
        top_frame.pack(side="top", fill="x", expand=True)
        self.top_frame = top_frame
        
        self.title_frame = None     # So can check if title
        if self.title is not None:
            self.title_frame = Frame(top_frame)
            self.title_frame.pack(side="top", fill="x", expand=True)
            title_label = Label(master=self.title_frame, text=self.title, font="bold")
            title_label.pack()
            
        
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

    def sleep(self, sec):
        """ "sleep" for a number of sec
        without stoping tkinter stuff
        :sec: number of milliseconds to delay before returning
        """
        now = time.time()
        end_time = now + sec
        while time.time() < end_time:
            self.update()
        return
    
    def redo(self):
        self.set_vals()

    def update(self):
        """ Do update to see display process
        """
        if self.mw is not None:
            self.mw.update()
            
    def get_ctl(self, field_name):
        """ Get field ctl
        :field_name: field name
        """
        field = field_name.lower()
        if field not in self.ctls_vars:
            fields_str = ", ".join(self.ctls_vars.keys())
            SlTrace.lg(f"ctl_vars fields: {fields_str}")
            raise SelectError(f"get_ctl: {self.control_prefix} has no field {field}")
            
        ctl = self.ctls[field]
        return ctl
            
    def get_val_from_ctl(self, field_name):
        """ Get value from field
        Does not set value
        :field_name: field name
        """
        field = field_name.lower()
        if field not in self.ctls_vars:
            fields_str = ", ".join(self.ctls_vars.keys())
            raise SelectError(f"get_val_from_ctl: '{self.control_prefix}'"
                              f" has no field '{field}'"
                              f"\n\nctl_vars fields: {fields_str}\n")
            
        value = self.ctls_vars[field].get()
        return value

    def update_from_ctl(self, field_name):
        """ Get value from field, and update properties
        :field_name: field name
        :returns: value from field
        """
        val = self.get_val_from_ctl(field_name)
        self.set_prop_val(field_name, val)
        return val
        
    
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
        while True:
            try:
                value = ctl_var.get()
                break
            except:
                ctl = self.ctls[field_name]
                ctl_str = ctl.get()
                ctl_var_type = content_var_type(ctl_var)
                default_val_str = self.get_prop_val(field_name, None)
                default_val = str2val(default_val_str, ctl_var_type)
                
                sr = SelectInput(master=self, title="GameControl",
                                  message=f"Bad format:'{ctl_str}' for {field_name}: ",
                                  default=default_val)
                value = sr.result
                if value is not None:
                    break
                    
        self.set_ctl_val(field_name, value)        
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


    def set_vert_sep(self, frame=None, text="  "):
        """ Add default vertical separator
        :frame:  destination frame
        :text: text to place in separator
        """
        if frame is None:
            frame = self.base_frame
        sep_frame = Frame(frame)
        sep_frame.pack(side="top", anchor=N)
        self.set_text(text, frame=sep_frame)



    def set_check_box(self, frame=None, field=None,
                        label=None, value=False,
                        command=None):
        """ Set up check box for field
        :field: local field name
        :label: button label - default final section of field name
        :value: value to set "string"
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
        SlTrace.lg(f"set_check_box adding field:{full_field}")
        self.set_prop_val(full_field, value)

    def check_box_change(self):
        value = self.check_box_change_content.get()
        self.check_box_change_callback(value)


    def null_radio_call(self, val):
        SlTrace.lg(f"null_radio_call({val})")
        
    def set_radio_button(self, frame=None, field=None,
                        label=None, value=None, set_value=None,
                        command=None):
        """ Set up one radio button for field
        :field: local field name (for all buttons in this group)
        :label: button label - must be unique in this group
        :value: value associated with this button
                    default: label string
        :set_value: set group value if present
                    default: leave group_value alone
                    Anyone of the set_radio_button calls
                    can set/change the value
                    if present, value is overridden
                    by property value
        :command: function called with button group value when button selected
        
        """
        if frame is None:
            frame = self.base_frame
        if field is None:
            SelectError("set_radio_button: field is missing")
        if label is None:
            SelectError("set_radio_button - label is missing")
        if value is None:
            value = label
        if command is None:
            cmd = None
        else:
            cmd=lambda cmd=command : cmd(value)
            
            
        full_field = self.field_name(field)
        if full_field not in self.ctls_vars:
            content = StringVar()          # Create new one for group
            self.ctls_vars[full_field] = content
            ctls_ctl = self.ctls[full_field] = {}  # dictionary of Radiobutton button widgets
        else:
            content = self.ctls_vars[full_field]
            ctls_ctl = self.ctls[full_field]
        if set_value is not None:
            prop_value = self.get_prop_val(full_field, None)
            if prop_value is None:
                content.set(set_value)
                self.set_prop_val(full_field, set_value)
            else:
                content.set(prop_value)
        widget =  Radiobutton(frame, variable=content, text=label, value=value,
                               command=cmd)
        widget.pack(side="left", fill="none", expand=True)
        ctls_ctl[full_field + "." + label] = widget           # Store each button in hash

    def set_entry(self, frame=None, field=None,
                        label=None, value=None,
                        enter_command=None,
                        width=None):
        """ Set up entry
        :frame: containing frame
        :field: relative field name (after self.base_field)
        :label: field label default: no label
        :value: value to set, iff not in properties
                value's variable type is used as the entry content's type
        :enter_command:    Command to call if ENTER is keyed when
                field is in focus
                default: use self.enter_command, if present
        :returns: entry widget
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
        if enter_command is not None:
            widget.bind ("<Return>", enter_command)
        elif self.enter_command is not None:
            widget.bind ("<Return>", self.enter_command)
            
        return widget

    def set_button(self, frame=None, field=None,
                        label=None, command=None):
        """ Set up button for field
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
        self.ctls[full_field] = widget
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
        return field_name.lower()
            
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
        if SlTrace.trace("set_window_size"):
            if ( not hasattr(self, "prev_x") or self.prev_x != x
                 or not hasattr(self, "prev_y") or self.prev_y != y
                 or not hasattr(self, "prev_width") or self.prev_width != width
                 or not hasattr(self, "prev_height") or self.prev_height != height):
                SlTrace.lg("set_window_size: change=%d x=%d y=%d width=%d height=%d" % (change, x,y,width,height))
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
        if win_width < 100:
            win_width = 100
        win_height = self.get_prop_val("win_height", self.mw.winfo_height())
        if win_height < 100:
            win_height = 100
        self.set_window_size(win_x, win_y, win_width, win_height, change=True)
        self.mw.protocol("WM_DELETE_WINDOW", self.hide_window)  # Still need info
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
            raise SelectError(f"Unsupported content var type {type}")
        
        return var


    def set_ctl_val(self, field_name, val):
        """ Set control field
        Creates field variable if not already present
        :field_name: field name, case insensitive name
        :val: value to display
        """
        field_name = field_name.lower()
        if field_name not in self.ctls_vars:
            content_var = self.content_var(type(val))
            self.ctls_vars[field_name] = content_var
        self.ctls_vars[field_name].set(val)
 


    def set_prop_val(self, name, value):
        """ Set property value as (string)
        and internal val as value
        :name: field name
        :value: default value, if not found
        """
        self.set_val(name, value)
        prop_key = self.get_prop_key(name)
        SlTrace.setProperty(prop_key, str(value))
        
    def set_ctl_label(self, field, label):
        """ Set field's associated label, if one
        """
        if field in self.ctls_labels:
            ctl_label = self.ctls_labels[field]
            ctl_label.config(text=label)

    
    def set_val(self, name, value):
        """ Set field value
        :name: field name
        :value: value to set
        """
        self.vals[name] = value
        


    def destroy(self):
        """ Destroy window resources
        """
        SlTrace.lg("SelectControlWindow destroy")
        if self.mw is not None:
            self.mw.destroy()
        self.mw = None
        
        
    def delete_window(self):
        """ Handle window deletion
        """
        SlTrace.lg("SelectControlWindow delete_window")
        if self.play_control is not None and hasattr(self.play_control, "close_score_window"):
            self.play_control.close_score_window()
        else:
            self.destroy()
            quit()
            SlTrace.lg("Properties File: %s"% SlTrace.getPropPath())
            SlTrace.lg("Log File: %s"% SlTrace.getLogPath())
            sys.exit(0)

        self.play_control = None
        
    def hide_window(self):
        """ Hide window as we said...
        """
        self.mw.withdraw()              # Just hide, for we can't easily delete/restore a singleton


    def show_window(self):
        """ Restore to view
        """
        self.mw.deiconify()
        
if __name__ == '__main__':
        
    SlTrace.setProps()
    root = Tk()
    ###root.withdraw()       # Hide main window
    test_general = False
    test_general = True
    test_radio_button = True
    test_radio_button = False
    if test_radio_button:
        scw = SelectControlWindow(title="SelectControlWindow Testing", display=True)
        mf = Frame(root)
        mf.pack()
    
        def call_unit(unit):    
            SlTrace.lg(f"call_unit({unit})")
        
        scw.set_fields(mf, "base_field", title="distance units")
        scw.set_radio_button(frame=mf, field="second", label="meter", set_value="foot", command=call_unit)
        scw.set_radio_button(frame=mf, field="second", label="yard", command=call_unit)
        scw.set_radio_button(frame=mf, field="second", label="foot", command=call_unit)
        fname = "base_field.second"
        fval = "yard"
        SlTrace.lg(f"Settng field:{fname} to {fval}")
        scw.set_ctl_val(fname, fval)
        sf = Frame(root)
        sf.pack()
        scw.set_fields(sf, "new_field", title="RadioButton Testing")
        scw.set_radio_button(frame=sf, field="a", label="a", set_value="b")
        scw.set_radio_button(frame=sf, field="a", label="b", command=call_unit) # Only a,b calls
        scw.set_radio_button(frame=sf, field="a", label="c")
        mainloop()
    elif test_general:    
        cF = SelectControlWindow(title="SelectControlWindow Testing", display=False)
        cf2 = SelectControlWindow()
        cf2.control_display()
            
        root.mainloop()