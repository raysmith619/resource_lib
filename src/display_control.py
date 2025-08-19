# display_control.py
"""
Display control (Frames, widgets...)
"""
import re

from select_error import SelectError
from select_trace import SlTrace

# Testing display control class
class DisplayControl:
    
    def __init__(self, settings_control=None):
        """ Setup link to setting conttrol (SettingControl)
        :setting_control: (SettingControl) if known
                Use set_setting_control if unknown
        """
        if settings_control is not None:
            self.set_settings_control(settings_control)
   
    def set_settings_control(self, settings_control):
       self.settings_control = settings_control

    def make_setting(self, *args, **kwargs):
        """ Connection to setting control (SettingControl)
            See SettingControl.make_setting for description
        """
        if self.setting_control is None:
            raise SelectError("Please setup setting_control link")
        
            self.setting_control.make_setting(*args, **kwargs) 

    def set_val(self, *args, **kwargs):
        if self.setting_control is None:
            raise SelectError("Please setup setting_control link")

        self.setting_control.set_val(*args, **kwargs,
                    update_display=False) # avoid recursion loop

    
    def get_display_val(self, name):
        """ Get displayed value
        """
        SlTrace.lg(f"get_display_val({name}) TBD")
        return None               
    
    def set_display_val(self, name, value):
        """ Transfer value to display
        """
        SlTrace.lg(f"set_display_val({name}: {value}) TBD")               
        

    def make_get_set(self, control_obj,
                    name, attribute):
        """ create get_set function for attribute
        :control_obj: instance of major class
        :name: setting name
        :attribute: setting attribute
        :returns get_set function
        """
        def get_set(name, value=None):
            if value is None:
                return getattr(control_obj, attribute)
            else:
                setattr(control_obj, value)
                return value
            
        return get_set
        
    def connect_names_to_settings(self, settings_obj,
                                name_to_attribute):
        """ Connect to settings via name
        :settings_obj: object which has
            get_val(name) which returns setting value
            set_val(name, value) which sets setting value
            
        :name_to_attri
        get_fun(name) returns get_set function
        :control_obj: object with attribute variables
        :name
        """
        self.name_to_get = {}
        self.control_obj = control_obj
        for name in name_to_attribute:
            attribute = name_to_attribute[name]
            if not hasattr(control_obj, attribute):
                raise SelectError(f"name {name}"
                        f" attribute: {attribute}"
                        f" is not present in control_obj"
                        f" {control_obj.__class__.__name__}")
                
            self.name_to_get[name] = self.make_get_set(
                        control_obj,
                        name, attribute)

    def make_get_set(self, control_obj,
                    name, attribute):
        """ create get_set function for attribute
        :control_obj: instance of major class
        :name: setting name
        :attribute: setting attribute
        :returns get_set function
        """
        def get_set(name, value=None):
            if value is None:
                return getattr(control_obj, attribute)
            else:
                setattr(control_obj, value)
                return value
            
        return get_set
        
    def connect_names_to_get_set(self, control_obj,
                                name_to_attribute):
        """ Provide get_set functions for each name
        get_fun(name) returns get_set function
        :control_obj: object with attribute variables
        :name
        """
        self.name_to_get = {}
        self.control_obj = control_obj
        for name in name_to_attribute:
            attribute = name_to_attribute[name]
            if not hasattr(control_obj, attribute):
                raise SelectError(f"name {name}"
                        f" attribute: {attribute}"
                        f" is not present in control_obj"
                        f" {control_obj.__class__.__name__}")
                
            self.name_to_get[name] = self.make_get_set(
                        control_obj,
                        name, attribute)
            

