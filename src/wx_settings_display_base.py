#wx_settings_display_base.py
""" 
Settings base for display control (SettingsDisplay)
Converted from wx_settings_display_demo.py
May compress SettingsDisplay->SettingsDisplayBase->ChessSettingsDisplay...
wxPython version of settings frame

TBD load/save settings from properties file
TBD implement do/undo settings
"""
import wx

from select_trace import SlTrace
from settings_display import SettingsDisplay

from wx_settings_data_panel_base import SettingsDataPanelBase
from wx_settings_control_panel_base import SettingsControlPanelBase

        
class SettingsDisplayBase(wx.Frame, SettingsDisplay):
    def __init__(self, parent=None, title=None, size=None,
                control_prefix="BASE_SETTINGS_FRAME",
                 
                data_panel_type=SettingsDataPanelBase,
                control_panel_type=SettingsControlPanelBase,
                update_data_fun=None,
                update_control_fun=None,
                onclose=None):
        """
        :parent: containg frame
        :title: optional title
        :size: frame size (wx.Size)
        :control_prefix: properties prefix
        :data_panel_type: settings data panel class
                    default: SettingsDataPanelDemo,
        :control_panel_type: settings control(button) panel class
                    default: SettingsControlPanelDemo,
        :update_data_fun: data change function
                        update_data_fun(name, value)
        :update_control_fun: control(e.g. button) function
                        update_control_fun(name)
        :onclose: call on window closure
                default: no action
        """
        if size is None:
            size = wx.Size(400,400)

        super().__init__(parent)    # wx.Frame.__init__
                                    # says super-class
                                    # never called
        SettingsDisplay.__init__(self,
                    update_data_fun=update_data_fun,
                    update_control_fun=update_control_fun,
                    onclose=onclose)
        self.Bind(wx.EVT_CLOSE, self.onclose)   # For SettingsDisplay

        self.control_prefix = control_prefix
        if title is None:
            title = "SettingsFrameDemo"
        self.SetTitle(title)
        green = "grey"
        self.settings_panel = wx.Panel(self, size=size, name=title)
        self.settings_panel.SetBackgroundColour(wx.Colour(246,246,246))
        settings_sizer = wx.BoxSizer(wx.VERTICAL)
        self.settings_data_panel = data_panel_type(
                        self.settings_panel,
                        size = wx.Size(120, 200),
                        update_data_fun=self.update_data_fun)
        settings_sizer.Add(self.settings_data_panel, 0, wx.ALL)
        settings_sizer.Add(wx.StaticLine(self.settings_panel), 0,
                                wx.EXPAND|wx.TOP|wx.BOTTOM)
        self.control_panel = control_panel_type(
            self.settings_panel, size=wx.Size(320, 30),
            update_control_fun=self.update_control_fun)
        settings_sizer.Add(self.control_panel, 0, wx.EXPAND)
        self.settings_panel.SetSizer(settings_sizer)
        settings_sizer.Fit(self)


    """ Debugging"""
    
    def rp(self, msg):
        if msg is None:
            msg = " "
        SlTrace.lg(f"SettingsDisplayDemo: {msg}")
        SlTrace.lg(f"settings_display.settings_data_panel.update_data_fun:"
                f" {self.settings_data_panel.update_data_fun}")
            
    """ Data access methods Only provide funtion gets
    """
    def get_get_name_val_fun(self, name):
        """ Get get_val function        
        :name: setting name
        :returns: get val function
        """
        return self.settings_data_panel.get_get_name_val_fun(name)
    
    def get_set_name_val_fun(self, name):
        """ Get set_val function
        :name: setting name
        :returns: set function
        """
        return self.settings_data_panel.get_set_name_val_fun(name)

    def set_update_data_fun(self, fun):
        """ Set link to function which should be called, with
        the item settings name, when any control display
        item(e.g., button) is cliked by the user
        Passed on to control_panel
        """
        self.settings_data_panel.set_update_data_fun(
            fun)


        
    def set_update_control_fun(self, fun):
        """ Set link to function which should be called, with
        the item settings name, when any control display
        item(e.g., button) is cliked by the user
        Passed on to control_panel
        """
        self.control_panel.set_update_control_fun(fun)

    """ NOT USED MUCH - using get_get/set_name_val_funs
    """        
    def get_name_val(self, name):
        """ Get widget value for name
        :name: setting name
        :returns: widget value
        """
        return self.settings_data_panel.get_name_val(name)
    
    def set_name_val(self, name, value):
        """ Get widget value for name
        :name: setting name
        :value: to set
        :returns: widget value
        """
        return self.settings_data_panel.set_name_val(name)
        
if __name__ == '__main__':
    import os
    import sys
    
    app = wx.App()
    width = int(400)
    height = int(400)
    size = wx.Size(width, height)
    frame = wx.Frame(None, size=wx.Size(width,height),
                     title="base_frame")
    
    def update_data_fun(name, value):
        SlTrace.lg(f"{os.path.basename(__file__)}:"
                   f" update_data_fun(\"{name}\", {value})")
    
    def update_control_fun(name):
        SlTrace.lg(f"{os.path.basename(__file__)}"
                   f" update_control_fun(\"{name}\")")

    def onclose():
        """ Called when demo window closes
        """
        SlTrace.lg("settings_frame closed")
        sys.exit(0)
        
    settings_frame = SettingsDisplayBase(frame,
                        title="SettingsFrameDemo",
                        size=size,
                        onclose=onclose
                        )
    settings_frame.set_update_data_fun(update_data_fun)
    settings_frame.set_update_control_fun(update_control_fun) 
    settings_frame.Show()
    app.MainLoop()  
