# settings_control.py
"""
Adapted from select_control.py

Facilitates
    setting and retrieving settings
    persistent storage of values
"""
import re
import wx

from select_error import SelectError
from select_trace import SlTrace
from setting import Setting

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise SelectError('Not a recognized Boolean value %s' % v)
"""
=======================================================================
Main Class SettingsControl
=======================================================================
"""
    
class SettingsControl:
    CONTROL_NAME_PREFIX = "SETTINGS_CONTROL"
    _instance = None         # Instance
    instance_no = 0         # Count instances
    UNDO_SECT = "___undo___"    # UNDO section name
    REDO_SECT = "___redo___"    # REDO section name
            
    def __init__(self,
                settings_server,
                settings_display,
                settings_dict=None,
                control_prefix=None,
                update_report=None,
                 ):
        """ Setup data control and access
        :settings_server: holder of setting variables/access
        :settings_display: settings display and input
        :settings_dict: dictionary by setting name of setup,
                        access
        :control_prefix: properties storage name prefix
        :update_report: update trace function
                        default: no report
        """
        self.settings_server = settings_server
        self.settings_display = settings_display
        if control_prefix is None:
            control_prefix = self.CONTROL_NAME_PREFIX
        self.control_prefix = control_prefix
        self.settings = {}          # Settings dictionary, by field name (Setting)
        self.changed = False        # Set if any value is changed vie set_val
        self.save_stack = []        # Settings stack
        self.unsave_stack = []      # Settings redo stack
        self.save_no = 0            # Track saves
        self.restore_no = 0
        self.redo_no = 0
        self.entry_no = 0           # entry position as created for display
        self.label_no = 0           # Ordering labels, to keep name unique
        self.update_report = update_report
        
        self.setting_types = {}        
        self.name_by_no = []
        self.entry_no = len(self.name_by_no)
        
        self.settings_display.set_update_data_fun(
            self.display_update_data)
        self.settings_display.set_update_data_fun
        '''
        self.rp("after set_update_data_fun")
        self.sud(self.display_update_data)
        self.rp("after assignment via sud")
        '''
        self.settings_display.set_update_control_fun(
            self.display_update_control)
        
        # If group dictionary present add settings
        if (self.settings_server is not None
            and self.settings_display is not None
            and settings_dict is not None):        
            self.make_settings_group(
                settings_server=settings_server,
                settings_display=settings_display,
                settings_dict=settings_dict)
        

    """ Debugging support
    def rp(self, msg=None):
        if msg is None:
            msg = ""
        SlTrace.lg(msg)
        SlTrace.lg(f"settings_display.settings_data_panel.update_data_fun:"
                f" {self.settings_display.settings_data_panel.update_data_fun}")
    def sud(self, fun):
        self.settings_display.settings_data_panel.update_data_fun = fun
    """ 
    
    def display_update_data(self, name, value):
        """ Called, announcing display data change
        :name: setting name
        :value: new value
        """
        SlTrace.lg(f"SettingsControl: display_update_data"
                   f"({name}, {value})")
        self.set_val(name, value, update_display=False)        

    def display_update_control(self, name):
        """ Called, announcing display control change
        :name: setting name
        """
        SlTrace.lg(f"SettingsControl: display_update_control"
                   f"({name})")        
        if name == "Save":
            self.save_settings()
        elif name == "Restore":
            self.restore_vals()
        elif name == "Undo":
            self.undo_settings()
        elif name == "Redo":
            self.redo_settings()
        else:
            raise SelectError(f"Unrecognized button name \"{name}\"")    
            
    def update_setting(self, name, value=None):
        """ Update existing setting value
        :name: Settings unique name
        :value: value of setting, type used unless value_type is present
        """
        if name not in self.settings:
            raise SelectError(f"update_setting {name}, {value}"
                              " not in settings")
        
            return self.settings[name].update(value)
        
    def make_setting(self, name,
                     value=None,
                     value_type=None,
                     setting_type = "std",
                     label=None,
                     attr=None,
                     get_fun=None,
                     set_fun=None,
                     display_get_fun=None,
                     display_set_fun=None):
        """ Create field, if not present, returning value
        :name: Settings unique name
        :value: value of setting, type used unless
                value_type is present
        :value_type: default: type(value)
        :attr: data attribute in settings_server
        :get_fun:   data get instead of settings_server.attr
        :set_fun:   data set instead of settings_server.attr
        :setting_type: setting value type
        :display_get_fun: display get value function
                REQUIRED for setting_type "std"
                        signature:
                            get_set_fun()
                                returns: current value        
        :display_set_fun: display set value function
                REQUIRED for setting_typ "std"
                        signature:
                            get_set_fun(value=self.value)
                                returns: current value        
        :label: Entry label text, default: use name
        :returns: value set
        """
        if name in self.settings:
            raise SelectError(f"name: {name} already created")
        
        if value is None and value_type is None:
            raise SelectError(f"make_setting: name: {name}"
                              "Both value and setting type can't be None")
            
        if (setting_type == "std"):
            if self.settings_server is None:
                raise SelectError(f"make_setting({name},{value})"
                                   " requires settings_server")
            
            if get_fun is None:
                raise SelectError(f"make_setting({name},{value})"
                                   " is missing get_fun")
                
            if set_fun is None:
                raise SelectError(f"make_setting({name},{value})"
                                   " is missing set_fun")
        
        if value_type is None:
            value_type = type(value)    # Infertype from value
        if label is None:
            label = name
        self.settings[name] = Setting(self,
                name, value=value,
                value_type=value_type,
                get_fun=get_fun,
                set_fun=set_fun,
                display_get_fun=display_get_fun,
                display_set_fun=display_set_fun,
                label=label,
                )       
        self.name_by_no.append(name)
        self.entry_no = len(self.name_by_no)
        
        prop_key = self.get_prop_key(name)
        prop_val = SlTrace.getProperty(prop_key, default=None)
        if prop_val is None:
            val = value
        else:
            tpd = type(value)
            if tpd is str:
                val = prop_val            # Keep the string
            elif tpd is bool:
                val = str2bool(prop_val)
            else:
                val = tpd(prop_val)         # Just cast it
        self.set_val(name, val)
        return val

    def make_settings_group(self,
            settings_server=None,
            settings_display=None,
            settings_dict=None):
        """ Setup a group of settings
        And load values from properties file
        :settings_server: serve settings main control
                        default: self.settings_server
        :settings_display: display settings and retrieve values
                        default:self.settings_display
        :settings_dict:  Settings setup and definition
                dictionary, by setting name, of the
                        following setup specification
                        dictionary:
                        value: initial setting value
                            OR get_fun value access function
                            OR attr settings_server.getattr(attr)
                            This is superceeded by a value,
                            if present, in the properties file
                        value_type: value type
                                default: use type(value)
                        attr:
                            OR use get_fun, set_fun
                           default: generate get_fun, set_fun
                        get_fun:
                        set_fun
                            if attr is present
                            then generate get_fun, set_fun
                            else use get_fun,set_fun
            """
        if settings_server is None:
            settings_server = self.settings_server
        if settings_display is None:
            settings_display = self.settings_display
        for name in settings_dict:
            if name in self.settings:
                raise SelectError("make_setting_group:"
                                  f" {name} already present")
            sd = settings_dict[name]
            if "attr" in sd:
                attr = sd["attr"]
                if not hasattr(settings_server, attr):
                    raise SelectError(f"No attr {attr}"
                            f" in obj {settings_server.__class__.__name__}")
                if "get_fun" in sd or "set_fun" in sd:
                    raise SelectError(f"make_setting_group{name}"
                            " Can't have attr and get_fun and set_fun")
                get_fun, set_fun = self.attr_to_get_set(
                    settings_server, attr=attr)
            else:
                if "get_fun" not in sd or "set_fun" not in sd:
                    raise SelectError(f"make_setting_group{name}"
                            " Must have attr or  get_fun and set_fun")
                get_fun, set_fun = sd["get_fun"], sd["set_fun"]
            
            if "value" in sd:
                value = sd["value"]
                set_fun(value)
            else:
                value = get_fun()
                
            if "value_type" in sd:
                value_type = sd["value_type"]
            else:
                value_type = type(value)
            display_get_fun = settings_display.get_get_name_val_fun(
                name)
            display_set_fun = settings_display.get_set_name_val_fun(
                name)
            
            self.make_setting(name=name, value=value,
                        value_type=value_type, attr=attr,
                        get_fun=get_fun, set_fun=set_fun,
                        display_get_fun=display_get_fun,
                        display_set_fun=display_set_fun)
        self.load_prop_stack()

    def attr_to_get_set(self, settings_server, attr):
        """ Generate get/set functions from attribute
        :settings_server: class instance containing attribute
        :attr: attribute name
        :returns: get_fun, set_fun
        """
        if settings_server is None:
            raise SelectError(f"attr_to_get_set: settings_server is None")
        
        def get_fun():
            """ attribute get function
            """
            ret = getattr(settings_server, attr)
            return ret
        
        def set_fun(value):
            """ attribute get function
            """
            ret = setattr(settings_server, attr, value)
            return ret
        
        return get_fun,set_fun
        
    def get_val_from_display(self, name):
        """ Get value from field
        Does not set value
        :name: field name
        """
        field = name
        if field not in self.settings:
            raise SelectError(f"Command has no attribute {field}")
        value = self.settings[field].get_display_val()
        return value

    
    def set_vals(self):
        """ Read form, if displayed, and update internal values
        """
        for name in self.settings:
            self.settings[name].set_val_from_display()
       
    
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

    def get_setting_type(self, name):
        """ Get entry type: std, label, internal
        :name: entry name
        """
        return self.settings[name].get_setting_type()
    
    def get_val(self, name, default=None):
        """ Get current value, if any, else property value, if any,
        else default
        :name: field name
        :default: returned if not found
        """
        if name in self.settings:
            val = self.settings[name].get_val()
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

    def get_setting_names(self, std=True, internal=False, label=False):
        """ Get list of setting names
        in sorted by
        :std: True include standard names
                default: True
        :internal:  Include special entry names 
                _... internal values
                default: False
        :label: Include group labels
                default: False
        """
        names = []
        for name in self.settings:
            setting = self.settings[name]
            setting_type = setting.get_setting_type()
            if setting_type == "internal":
                if internal:
                    names.append(name)
            elif setting_type == "std":
                if std:
                    names.append(name)
            elif setting_type == "label":
                if label:
                    names.append(name)
                
        return sorted(names)
        
    def list_vals(self, prefix=None):
        """ List all key,value pairs
        :prefix: Optional text prefix
        """
        if prefix is None:
            prefix = ""
        for name in self.settings:
            setting = self.settings[name]
            setting_type = setting.get_setting_type()
            val = setting.get_val()
            SlTrace.lg(f"{prefix} {name}({setting_type}): {val}")

    def make_label(self, label):
        """ Make label for control panel display
        :label: label string
        """
        self.label_no += 1
        name = f"label_{self.label_no}"
        self.make_setting(name, value=label, setting_type="label", label=label)
    
    def set_setting(self, name, value):
        """ Set setting, given value
        Updates field display and properties value
        :name: setting name
        :value:        value to set
        """
        if name not in self.settings:
            raise SelectError(f"Control has no field variable {name}")
        self.settings[name].set_val(value)
        
    def set_prop_val(self, name, value):
        """ Set local (value) and property value(string)
        :name: field name
        :value: default value, if not found
                using str(value)
        """
        ###self.set_val(name, value)         # already set current value
        prop_key = self.get_prop_key(name)
        SlTrace.setProperty(prop_key, str(value))

    def update_prop_val(self, name):
        """ Update properties value from current value
        :name: field name
        """
        val = self.get_val(name)
        self.set_prop_val(name, val)

    def update_settings(self, force=False):
        """ Update all display values from current
            Save previous settings if any changes or force is True
                if text variables, use widget contents
                    to update textvar, and var, and prop
                else use control vars to update prop
            :force: Always save settings default: False
        """
        trace_str = ""
                                    # Check if any changes
        for name in self.settings:
            is_changed = False
            setting = self.settings[name]
            val = setting.get_val()
            val_display = setting.get_display_val()
            if val != val_display:
                new_val = val_display
                is_changed = True
            if is_changed and SlTrace.trace("track_vals"):
                if trace_str != "":
                    trace_str += " "
                val_str = f"was: {val} is {new_val}"
                trace_str += f"Change: {name}:{val_str}"
                SlTrace.lg(trace_str)
        if force or is_changed:
            self.save_settings()

    def restore_vals(self, redo=False):
        """ Backup current values, clearing changed flag
        :redo: if True, restore before last undo
        :returns: True if successful else False
        """
        
        restored_entry = None
        self.restore_no += 1
        SlTrace.lg(f"restore_vals restore_no: {self.restore_no}", "track_vals")
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
        :returns: dictionary by name of current value settings
        """
        entry = {}
        for name in self.settings:
            entry[name] = self.settings[name].get_val()
        return entry    
                    
    def save_vals(self, entry=None, to_redo=False):
        """ Backup current values, or others, clearing changed flag
        :entry: values dictionary default: use self.get_settings()
        :to_redo: if True save to unsave_stack
        """
        if entry is None:
            entry = self.get_settings()            
        self.save_no += 1
        SlTrace.lg(f"save_vals save_no: {self.save_no}", "track_vals")
        if to_redo:
            self.unsave_stack.append(entry)
        else:
            self.save_stack.append(entry)
        self.changed = False
        SlTrace.lg("save_vals", "track_vals")
        se = entry
        for name in se:
            SlTrace.lg(f"{name}: {se[name]}", "track_vals")
        self.update_prop_stack(to_redo=to_redo) 

    def get_stack_prefix(self, to_redo=False):
        """ Get properties prefix for stack
        :to_redo: True = redo/unsave stack - default
                    False undo/save stack
        """
        prefix = f"{self.control_prefix}."
        if to_redo:
            prefix += self.REDO_SECT
        else:
            prefix += self.UNDO_SECT
        return prefix
        
    def update_prop_stack(self, to_redo=False):
        """ Update stack in properties
        :to_redo: to_redo True - stack_save
                          False - stack_unsave
        """
        prefix = self.get_stack_prefix(to_redo)
        if to_redo:
            stack  = self.unsave_stack
        else:
            stack = self.save_stack

        self.remove_props(prefix)
        # 1 is top of stack, most recently set
        for n,se in enumerate(reversed(stack), 1):
            stack_key = f"{prefix}.{str(n)}" 
            for name in se:
                prop_key = f"{stack_key}.{name}"
                val = se[name]
                SlTrace.setProperty(prop_key, val)
                
        
    def load_prop_stack(self, to_redo=False):
        """ Load stack from properties
        :to_redo: to_redo True - stack_save
                          False - stack_unsave
        """
        stack_prefix = self.get_stack_prefix(to_redo)

        # Get stack entries
        # Get stack depth
        if len(self.settings) < 1:
            SlTrace.lg("No settings = no stack")
            return
        
        max_stack = 20
        entries = []        # ordered 1,2,...
        for n in range(1,  max_stack+1):
            level_key = f"{stack_prefix}.{str(n)}"
            level_keys = SlTrace.getPropKeys(startswith=level_key)
            if len(level_keys) == 0:
                break   # End of stack
            
            entry = {}
            for name in self.settings:
                setting = self.settings[name]
                setting_key = level_key + "." + name
                val = SlTrace.getProperty(setting_key, default=None)
                if val is None:
                    val = setting.get_val()
                else:
                    if setting.value_type == bool:
                        val = str2bool(val)
                    else:
                        val = setting.value_type()
                entry[name] = val
            entries.append(entry)
            stack = list(reversed(entries))
        if len(entries) == 0:
            return      # No stack in properties
        
        if to_redo:
            self.unsave_stack = stack
        else:
            self.save_stack = stack

        if SlTrace.trace("stack") or True:
            self.print_stack("After loading", to_redo)

    def print_stack(self, prefix=None, to_redo=False):
        if to_redo:
            stack_name = "unsave"
            stack = self.unsave_stack
        else:
            stack_name = "save"
            stack = self.save_stack
        SlTrace.lg(f"{stack_name} stack" )
        for i, se in enumerate(reversed(stack)):
            se_str = f"{i}: "
            for name in se:
                se_str += f"\n    {name}={se[name]}"
            SlTrace.lg(se_str)        
                    
            
            
        
                    

    def remove_props(self, prefix):
        """ Remove properties starting with prefix
        :prefix: starting prefix
        """
        property_keys = SlTrace.getPropKeys(startswith=prefix)
        for prop_key in property_keys:
            SlTrace.deleteProperty(prop_key)
                           
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
        self.restore_vals(redo=True)
                        
    def set_val(self, name, value, no_change=False,
                update_display=True):
        """ Set field value, updating property value
        :name: field name
        :value: value to set
        :no_change: True -> ignore change default:False
        :update_display: update display value
                        False - no display update
                        default: True
        :returns: value to facilitate compact variable updating
        """
        setting = self.settings[name]
        if not no_change:
            self.changed = True
        setting.set_val(value, update_display=update_display)
        return value
    
if __name__ == '__main__':
    import sys
    import argparse
    
    app = wx.App()
    from settings_server_demo import SettingsServerDemo
    from wx_settings_display_demo import SettingsDisplayDemo
    
    SlTrace.setProps()
    class TestFrame(wx.Frame):
        def __init__(self,
            parent=None,
            width=400,
            height=400,
            size=None):
            if size is None:
                size = wx.Size(width, height)
            super().__init__(parent)
            self.Bind(wx.EVT_CLOSE, self.on_close)
            settings_display = SettingsDisplayDemo(self,
                                title="wx_settings_frame2",
                                size=size,
                                onclose=self.on_close) 
            settings_display.Show()
            settings_server = SettingsServerDemo()
            
            settings_dict = {
                    "Print_Board" :
                        {"attr" : "setting_is_printing_board"},
                    "Print_FEN" :
                        {"attr" : "setting_is_printing_fen"},
                    "Display_Move" :
                        {"attr" : "setting_is_move_display"},
                    "Display_Final_Position" :
                        {"attr" : "setting_is_final_position_display"},
                    "Stop_on_Error" :
                        {"attr" : "setting_is_stop_on_error"},
                    "Use_Shortest_Move_Interval" :
                        {"get_fun" : settings_server.get_shortest_move,
                        "set_fun" : settings_server.set_shortest_move},
                    "Set_FASTEST_Run" :
                        {"get_fun" : settings_server.get_fastest_run,
                        "set_fun" : settings_server.set_fastest_run},
                    "Move_Interval" :
                        {"attr" : "loop_interval"},
            }
            settings_control = SettingsControl(
                settings_server=settings_server,
                settings_display=settings_display)
            settings_control.make_settings_group(
                settings_dict=settings_dict)
            
        def on_close(self, event=None):
            SlTrace.lg("SettingsControl closeing")
            SlTrace.onexit()
            sys.exit()    
                
                
            
    tF = TestFrame(None)
    
    app.MainLoop()
    SlTrace.lg("After app.MainLoop")
    tF.on_close()
    