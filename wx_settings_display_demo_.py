#wx_settings_display_demo.py
""" 
Demo data display/import
"""
import wx

from select_trace import SlTrace
from settings_display import SettingsDisplay

from wx_settings_data_panel_demo import SettingsDataPanelDemo
from wx_settings_control_panel_demo import SettingsControlPanelDemo

        
class SettingsDisplayDemo(wx.Frame, SettingsDisplay):
    def __init__(self, parent=None, title=None, size=None,
                 control_prefix="CHESS_SETTINGS_FRAME",
                 update_data_fun=None,
                 update_control_fun=None):
        """
        :parent: containg frame
        :title: optional title
        :size: frame size (wx.Size)
        :control_prefix: properties prefix
        :update_data_fun: data change function
                        update_data_fun(name, value)
        :update_control_fun: control(e.g. button) function
                        update_control_fun(name)
        """
        if size is None:
            size = wx.Size(400,400)
        super().__init__(parent)    # wx.Frame.__init__
                                    # says super-class
                                    # never called
        SettingsDisplay.__init__(self,
                    update_data_fun=update_data_fun,
                    update_control_fun=update_control_fun)
        self.control_prefix = control_prefix
        self.update_data_fun = update_data_fun
        self.update_control_fun = update_control_fun
        green = "grey"
        settings_panel = wx.Panel(self, size=size, name=title)
        settings_panel.SetBackgroundColour(wx.Colour(246,246,246))
        settings_sizer = wx.BoxSizer(wx.VERTICAL)
        self.settings_data_panel = SettingsDataPanelDemo(
                        settings_panel,
                        size = wx.Size(200, 110),
                        update_fun=self.update_data_fun)
        settings_sizer.Add(self.settings_data_panel, 0, wx.ALL)
        settings_sizer.Add(wx.StaticLine(settings_panel), 0,
                                wx.EXPAND|wx.TOP|wx.BOTTOM)
        self.control_panel = SettingsControlPanelDemo(
            settings_panel, size=wx.Size(320, 30),
            update_control_fun=self.update_control_fun)
        settings_sizer.Add(self.control_panel, 0, wx.EXPAND)
        settings_panel.SetSizer(settings_sizer)
        settings_sizer.Fit(self)
        
    def setup_display_control(self, display_control):
        """ Setup value display/save support
        :display_control: display access
        """
        self.display_control = display_control


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
    app = wx.App()
    width = int(400)
    height = int(400)
    size = wx.Size(width, height)
    frame = wx.Frame(None, size=wx.Size(width,height),
                     title="base_frame")
    
    def update_data_fun(name, value):
        SlTrace.lg(f"""data_update_fun("{name}", {value})""")
    
    def update_control_fun(name):
        SlTrace.lg(f"""data_control_fun("{name}")""")

    settings_frame = SettingsDisplayDemo(frame,
                        title="wx_settings_frame2",
                        size=size,
                        update_data_fun=update_data_fun,
                        update_control_fun=update_control_fun
                        ) 
    settings_frame.Show()
    app.MainLoop()  
