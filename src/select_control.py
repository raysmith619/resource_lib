# select_control.py
"""
Adapted from block/src/select_control_window.py

Base for independent control
Provides a singleton which is universally accessible
Facilitates
    setting and retrieving of game controls
    persistent storage of values
"""
from tkinter import *

from select_error import SelectError
from select_trace import SlTrace


    

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise SelectError('Not a recognized Boolean value %s' % v)
    
    
    
class SelectControl:
    CONTROL_NAME_PREFIX = "variable_control"
    _instance = None         # Instance
    instance_no = 0         # Count instances
    
    def __init__(self, *args, **kwargs):
        SlTrace.lg(f"SelectControl.__init__ {SelectControl.instance_no}")
        
            
    def _init(self, play_control=None,
                control_prefix=None
                 ):
        """ Control attributes
        :title: window title
        """
        SelectControl.instance_no += 1
        self.play_control = play_control
        if control_prefix is None:
            control_prefix = self.CONTROL_NAME_PREFIX
        self.control_prefix = control_prefix
        self.vals = {}              # Current values if any
        self.ctls = {}              # Dictionary of field control widgets
        self.ctls_vars = {}         # Dictionary of field control widget variables
        self.ctls_textvars = {}     # Dictionary of field text variables, if requested
        self.changed = False        # Set if any value is changed vie set_val
        self.save_stack = []        # variable setting stack
        self.unsave_stack = []      # variable redo stack
        self.save_no = 0            # Track saves
        self.restore_no = 0
        self.redo_no = 0
        self.make_val("_save_no", self.save_no)
        self.make_val("_restore_no", self.restore_no)
        self.make_val("_redo_no", self.redo_no)
        
    def __new__(cls, *args, **kwargs):
        """ Make a singleton
        """
        if cls._instance is None:
            cls._instance = super(SelectControl, cls).__new__(cls)
            ###cls._instance._init(*args, **kwargs)
            cls._instance._init(*args, **kwargs)
        return cls._instance

    def add_widget(self, name, widget):
        """ Add control widget in sync with variables
        :name: control name
        :widget: widget
        """
        if name in self.ctls:
            raise SelectError(f"duplicate widget add: {name}")
        
        self.ctls[name] = widget
        
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
            val = self.vals[name]
            if default is not None and type(val) != type(default):
                tpd = type(default)
                SlTrace.lg(f"get_val: self.vals[{name}] type{type(val)} != type{tpd} of default{default}")
                val = tpd(val)
            elif type(val) == str and re.match(r'^\d+$', val):
                SlTrace.lg(f"get_val: suspect {name} {val} is an int")
                return int(val)
            elif type(val) == str and re.match(r'^(\d*)?\.(\d*)$', val) and val != ".":
                SlTrace.lg(f"get_val: suspect {name} {val} is a float")
                return float(val)
                    
            return val
        
        val = self.get_prop_val(name, default)
        return val

    def get_textvar(self, name):
        """ Get variable for field
        :name: field name
        :returns: field control variable
        """
        if name not in self.ctls_textvars:
            raise SelectError(f"text field {name} not present")
        return self.ctls_textvars[name]

    def get_var(self, name):
        """ Get variable for field
        :name: field name
        :returns: field control variable
        """
        if name not in self.ctls_vars:
            raise SelectError(f"field {name} not present")
        return self.ctls_vars[name]
    
    def list_vals(self, prefix=None):
        """ List all key,value pairs
        :prefix: Optional text prefix
        """
        if prefix is None:
            prefix = ""
        for name in self.vals:
            val = self.vals[name]
            SlTrace.lg(f"{prefix} {name}: {val}")
    
    def list_textvals(self, prefix=None):
        """ List all key,value text variable pairs
        :prefix: Optional text prefix
        """
        if prefix is None:
            prefix = ""
        for name in self.ctls_textvars:
            var = self.ctls_textvars[name]
            SlTrace.lg(f"{prefix} {name}: {var.get()}")
            
            
    def make_val(self, name, default=None, repeat=False, textvar=False):
        """ Create field, if not present, returning value
        :name: field name
        :default: value used if field not present
        :repeat: True->allow repeats default: False
        :textvar: True - create text field variable for widjets such as Entry etc.
        :returns: value set
        """
        if default is None:
            raise SelectError(f"make_val[{name}] REQUIRED default is Missing")
        if name in self.vals:
            if not repeat:
                raise SelectError(f"name: {name} already made")
        
        else:
            self.ctls_vars[name] = self.content_var(type(default))
            self.vals[name] = default
        prop_key = self.get_prop_key(name)
        prop_val = SlTrace.getProperty(prop_key, default=None)
        if prop_val is None:
            val = default
        else:
            tpd = type(default)
            if tpd is str:
                val = prop_val            # Keep the string
            elif tpd is bool:
                val = str2bool(prop_val)
            else:
                val = tpd(prop_val)         # Just cast it
        self.set_val(name, val)
        if textvar:
            self.ctls_textvars[name] = StringVar()
            self.ctls_textvars[name].set(val)
        return val
    
    def set_ctl(self, field_name, value):
        """ Set field, given value
        Updates field display and properties value
        :field_name: field name
        :value:        value to set
        """
        if field_name not in self.ctls_vars:
            raise SelectError(f"Control has no field variable {field_name}")
        ctl_var = self.ctls_vars[field_name]
        ctl_var.set(value)
        self.set_prop_val(field_name, value)


    def content_var(self, ctype):
        """ create content variable of the ctype val
        :ctype: variable type
        """
        if ctype == str:
            var = StringVar()
        elif ctype == int:
            var = IntVar()
        elif ctype == float:
            var = DoubleVar()
        elif ctype == bool:
            var = BooleanVar()
        else:
            raise SelectError(f"Unsupported content var type {ctype}")
        
        return var


    def set_ctl_val(self, field_name, val):
        """ Set control field
        Creates field variable if not already present
        Sets vals[field_name]
        :field_name: field name
        :val: value to display
        """
        if field_name not in self.ctls_vars:
            content_var = self.content_var(type(val))
            self.ctls_vars[field_name] = content_var
        self.ctls_vars[field_name].set(val)
        self.vars[field_name] = val


    def set_prop_val(self, name, value):
        """ Set local (value) and property value(string)
        :name: field name
        :value: default value, if not found
        """
        self.vals[name] = value         # set current value
        prop_key = self.get_prop_key(name)
        SlTrace.setProperty(prop_key, str(value))

    def update_prop_val(self, name):
        """ Update properties value from current value
        :name: field name
        """
        val = self.vals[name]
        self.set_prop_val(name, val)

    def update_settings(self, force=False):
        """ Update all control vars properties
            Save previous settings if any changes or force is True
                if text variables, use widget contents
                    to update textvar, and var, and prop
                else use control vars to update prop
            :force: Always save settings default: False
        """
        trace_str = ""
                                    # Check if any changes
        for name in self.ctls_vars:
            is_changed = False
            var = self.ctls_vars[name]
            val = var.get()
            if name in self.ctls_textvars and name in self.ctls:
                widget = self.ctls[name]
                new_val = widget.get()
            else:
                var = self.ctls_vars[name]
                new_val = var.get()
            if new_val != val:
                is_changed = True
            if is_changed and SlTrace.trace("track_vals"):
                if trace_str != "":
                    trace_str += " "
                val_str = f"was: {val} is {new_val}"
                trace_str += f"Change: {name}:{val_str}"
        if force or is_changed:
            self.save_settings()
            
        for name in self.ctls_vars:
            if name in self.ctls_textvars and name in self.ctls:
                widget = self.ctls[name]
                val = widget.get()
                self.set_val(name, val)
            else:
                var = self.ctls_vars[name]
                val = var.get()
                self.set_val(name, val)
            if SlTrace.trace("track_vals"):
                if trace_str != "":
                    trace_str += " "
                val_str = self.get_prop_val(name, "???")
                trace_str += f"{name}:{val_str}"
        if trace_str != "":
            SlTrace.lg(f"update_settings: {trace_str}")

    def restore_vals(self, redo=False):
        """ Backup current values, clearing changed flag
        :redo: if True, restore before last undo
        :returns: True if successful else False
        """
        
        restored_entry = None
        self.restore_no += 1
        SlTrace.lg(f"restore_vals restore_no: {self.restore_no}", "track_vals")
        self.set_val("_restore_no", self.restore_no, no_change=True)
        if redo:
            if len(self.unsave_stack)  > 0:
                restored_entry = self.unsave_stack.pop()
        else:
            if len(self.save_stack) > 0:
                restored_entry = self.save_stack.pop()
        if restored_entry is not None:
            cur_vals = self.get_settings()
            self.save_vals(entry=cur_vals, to_redo=not redo)
            for name in restored_entry:
                self.set_val(name, restored_entry[name])
            self.changed = False
            SlTrace.lg("restore_vals")
            se = restored_entry
            for name in se:
                SlTrace.lg(f"{name}: {se[name]}")
            return True
        
        else:
            SlTrace.lg(f"empty {'redo' if redo else 'save'} stack")
            return False
        

    def save_if_change(self):
        """ Save values if any change since last save_vals
        """
        if self.changed:
            self.save_vals()


    def save_settings(self):
        """ Save current saveings
        """
        self.save_vals()

    def get_settings(self):
        """ Get current value settings
        :returns: current value settings
        """
        entry = {}
        for name in self.ctls_vars:
            entry[name] = self.get_val(name)
        return entry    
                    
    def save_vals(self, entry=None, to_redo=False):
        """ Backup current values, or others, clearing changed flag
        :entry: values dictionary defalut: use self.ctls_vars
        :to_redo: if True save to unsave_stack
        """
        if entry is None:
            entry = self.get_settings()            
        self.save_no += 1
        SlTrace.lg(f"save_vals save_no: {self.save_no}", "track_vals")
        self.set_val("_save_no", self.save_no, no_change=True)
        if to_redo:
            self.unsave_stack.append(entry)
        else:
            self.save_stack.append(entry)
        self.changed = False
        SlTrace.lg("save_vals", "track_vals")
        se = entry
        for name in se:
            SlTrace.lg(f"{name}: {se[name]}", "track_vals")
            
    def undo_settings(self):
        """ Recover previous saved window settings
        """
        self.restore_vals()
    
    def redo_settings(self):
        """ Recover settings replaced by last undo
        """
        self.redo_no += 1
        SlTrace.lg(f"redo_settings redo_no: {self.redo_no}", "track_vals")
        self.redo_no += 1
        self.set_val("_redo_no", self.redo_no, no_change=True)
        self.restore_vals(redo=True)
                        
    def set_val(self, name, value, no_change=False):
        """ Set field value, updating property value
        :name: field name
        :value: value to set
        :no_change: True -> ignore change default:False
        :returns: value to facilitate compact variable updating
        """
        tvalue = type(value)
        tval = type(self.vals[name])
        if tvalue != tval:
            if tvalue == str and tval == bool:
                value = str2bool(value)
            else:
                if tvalue == str:
                    if value == "":
                        value = "0"
                value = tval(value)
                    
        if value != self.vals[name]:
            if not no_change:
                self.changed = True
        self.vals[name] = value           # Update properties
        self.update_prop_val(name)
        if name in self.ctls_textvars:
            self.ctls_textvars[name].set(value)
        if name in self.ctls_vars:
            self.ctls_vars[name].set(value)
        return value
    
if __name__ == '__main__':
    from tkinter import *       # IntVar() fails without
    import argparse
    
    SlTrace.setProps()
    
    
    mw = Tk()
    cF = SelectControl()
    ncol = cF.make_val("ncol", 4)     # default, override from properties
    nrow = cF.make_val("nrow", 5)
    size = cF.make_val("size", 123.456, textvar=True)
    SlTrace.lg(f"After make_val ncol={ncol} nrow={nrow} size={size}")    
    cF.list_vals("Pre-command line parsing")
    pcl_ncol = ncol
    pcl_nrow = nrow
    pcl_size = size
    SlTrace.lg(f"Initializing values ncol={ncol} nrow={nrow} size={size}")    
    cF.update_settings()
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--ncol=', type=int, dest='ncol', default=ncol)
    parser.add_argument('--nrow=', type=int, dest='nrow', default=nrow)
    args = parser.parse_args()             # or die "Illegal options"
    SlTrace.lg(f"args: {args}\n")
    ncol = cF.set_val("ncol", args.ncol)
    nrow = cF.set_val("nrow", args.nrow)
    SlTrace.lg(f"After command line parsing ncol={ncol} nrow={nrow} size={size}")
    cF.update_settings()    
    cF.list_vals("starting vals:")
    cF.update_settings()
    ncol = 2
    nrow = 3
    size = 789.
    cF.set_val("ncol", ncol)
    cF.set_val("nrow", nrow)
    cF.set_val("size", size)
    cF.list_vals(f"After ncol={cF.get_val('ncol')} nrow={cF.get_val('nrow')} size={cF.get_val('size')}")
    cF.update_settings()
    cF.update_settings()     # No changes should be seen/saved
    
    size2 = size + .1
    cF.make_val("size", size2, repeat=True, textvar=True)
    ncol = 8
    nrow = 8
    size = 400.
    cF.set_val("ncol", ncol)
    cF.set_val("nrow", nrow)
    cF.set_val("size", size)
    SlTrace.lg(f"After ncol={cF.get_val('ncol')} nrow={cF.get_val('nrow')} size={cF.get_val('size')}")
    cF.list_vals()
    cF.list_textvals("textvars")
    
    cF.undo_settings()
    SlTrace.lg("After undo_settings")
    cF.list_vals()
    cF.list_textvals("textvars")
    
    cF.redo_settings()
    SlTrace.lg("After redo_settings")
    cF.list_vals()
    cF.list_textvals("textvars")
    
    cF.set_val("ncol", pcl_ncol+1)
    cF.set_val("nrow", pcl_nrow+1)
    cF.set_val("size", pcl_size+1)
    SlTrace.lg(f"After ncol={cF.get_val('ncol')} nrow={cF.get_val('nrow')} size={cF.get_val('size')}")
    cF.list_vals()
    cF.list_textvals("textvars")
    cF.update_settings()
    
    cF.set_val("ncol", pcl_ncol+2)
    cF.set_val("nrow", pcl_nrow+2)
    cF.set_val("size", pcl_size+3)
    SlTrace.lg(f"After ncol={cF.get_val('ncol')} nrow={cF.get_val('nrow')} size={cF.get_val('size')}")
    cF.list_vals()
    cF.list_textvals("textvars")


    cF.undo_settings()
    SlTrace.lg(f"After undo_settings")
    cF.list_vals()
    cF.list_textvals("textvals")

    cF.undo_settings()
    SlTrace.lg(f"After undo_settings")
    cF.list_vals()
    cF.list_textvals("textvals")

    cF.undo_settings()
    SlTrace.lg(f"After undo_settings")
    cF.list_vals()
    cF.list_textvals("textvals")

    cF.redo_settings()
    SlTrace.lg(f"After undo_settings redo=True")
    cF.list_vals()
    cF.list_textvals("textvais")

    cF.redo_settings()
    SlTrace.lg(f"After undo_settings redo=True")
    cF.list_vals()
    cF.list_textvals("textvals")

