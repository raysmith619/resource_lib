#setting.py  09Aug2025  crs, author
""" Encapsulates program setting
"""
class Setting:
    def __init__(self,
                 setting_control,
                 name, value=None,
                value_type=None,
                get_fun=None,
                set_fun=None,
                setting_type="std",
                display_get_fun=None,
                display_set_fun=None, 
                label=None):
        """ Setup setting for display, update, etc
        :setting_control: (SettingControl) reference settings controller
        :name: setting name, unique within this control and display
        :value: setting initial value, type used if no setting_type
        :value_type: value type if present
                    default: type(value)
        :setting_type: setting type
                    "std"   - standard DEFAULT
                    "internal"
                    "label" - display label support
        :get_fun: user variable get function
                REQUIRED: signature get_get_fun()
                            returns: current value        
        :set_fun: user variable set function
                REQUIRED: signature get_set_fun(self.value)
                            returns: current value        
        :display_get_fun:   get value from display
        :display_set_fun:   sets value to display 
        """
        self.setting_control = setting_control
        self.name = name
        self.value = value
        self.value_type = value_type
        self.setting_type = setting_type
        self.label = label
        self.get_get_fun = get_fun
        self.set_fun = set_fun
        self.display_get_fun = display_get_fun
        self.display_set_fun = display_set_fun 
        
    def get_val(self):     # Get current value
        return self.value
        
    def get_user_val(self):
        """ Get value from user
        """
        self.value = self.get_fun()
        return self.value

    def set_user_val(self, value=None):
        """ Set user value
        """
        if value is None:
            value = self.value
        self.value = value
        self.set_fun(value)
        return self.value
            
    def get_setting_type(self):
        return self.setting_type

    def set_val(self, value, update_display=True):
        """ Set value, also properties value
        :value: to set
        :update_display: Update display iff True
                    default: True - update
        """
        value_set = value
        if type(value_set) != self.value_type:
            value_set = self.value_type(value)
        self.set_user_val(value_set)
        
        if update_display:
            self.display_set_fun(value_set)
        self.setting_control.set_prop_val(self.name, value)

    def set_val_from_display(self):
        """ Transfer display value to setting value
        """
        self.set_val(self.get_display_value(),
                     update_display=False)

    """ Links to display_control
    """    

    def get_display_val(self):
        self.value = self.display_get_fun()
        return self.value

    def set_display_val(self, value=None):
        """ Transfer value to display
        Could be something different than current value
        :value: value to display
                default: current value
        """
        if value is None:
            value = self.value
        self.display_set_fun(value) 
            
