#settings_display.py    12Aug2025  crs
""" Settings data access setup
This is a mix-in class for data display classes, providing
general access to data (e.g. checkBox) and control(e.g. Button),
control and data
    Functions (require overload for actual data)

    get_name_val_fun(self, name)
    set_update_data_fun(self, update_data_fun):
            Set link to function which should be called, with
            the item settings name, when any data display
            item is modified by the user
    set_update_control_fun(self, update_control_fun):
        Set link to function which should be called, with
        the item settings name, when any control display
        item(e.g., button) is cliked by the user

    MUST BE OVERRIDDEN
    get_get_name_val_fun returns function to get function
                            to return function for data_get
        fun(name) returns data value
    get_set_name_val_fun returns function to get function for
                    to return function for data_get 
                fun(name, value) set data value

    display classes such as ChessDisplayFrame/ChessDisplayPanel

"""
from select_trace import SlTrace,SelectError

class SettingsDisplay:
    def __init__(self,
                 update_data_fun=None,
                 update_control_fun=None):
        """ Setup settings data
        These may be called with functions
        if not known at creation time
        :update_data_fun: called when data updated
            fun(name,value)
        :update_control_fun: called when control activated
                                e.g., button clicked 
        """
        self.update_data_fun = update_data_fun
        self.update_control_fun = update_control_fun


    def set_get_name_val_fun(self, get_name_val_fun):
        self.get_name_val_fun = get_name_val_fun

    def get_name_val_fun(self, name):
        raise SelectError(f"get_name_val_fun({name}) needs OVERRIDE")


    def set_update_data_fun(self, fun):
        """ Set link to function which should be called, with
        the item settings name, when any control display
        item(e.g., button) is cliked by the user
        Passed on to control_panel
        """
        self.update_data_fun = fun

    def _update_data_fun(self, name, value):
        """ Do update call, if updata_data_fun set"""
        if self.update_data_fun is not None:
            self.update_data_fun(name, value)

    def set_update_control_fun(self, fun):
        """ Set link to function which should be called, with
        the item settings name, when any control display
        item(e.g., button) is cliked by the user
        """
        self.update_control_fun = fun
    

    def update_control(self, name):
        """ Do update call, if updata_control_fun set"""
        if self.update_control_fun is not None:
            self.update_control_fun(name)
        