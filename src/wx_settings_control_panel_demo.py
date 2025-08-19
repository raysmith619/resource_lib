#wx_settings_control_panel_demo.py
""" 
Demo display settings
controls: SAVE, LOAD, DO, UNDO
"""
import wx

from select_trace import SlTrace

from settings_display import SettingsDisplay

class SettingsControlPanelDemo(wx.Panel, SettingsDisplay):
    def __init__(self, parent=None, title=None, size=None,
                 update_control_fun=None):
        """ :parent: containg frame
        """
        if title is None:
            title = "Data"
        if size is None:
            size = wx.Size(200,100)
        super().__init__(parent, name=title, size=size)
        SettingsDisplay.__init__(self,
                    update_control_fun=update_control_fun)
        
        main_panel = wx.Panel(self, size=size, name=title)
        main_sizer = wx.BoxSizer(wx.VERTICAL)        

        controls_panel = wx.Panel(main_panel, size=size)
        controls_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        
        green = "#008000"
        btn_panel = wx.Panel(controls_panel)
        btn_panel.SetBackgroundColour(wx.Colour(246,246,246))
        
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sp = 5
        btn_save = wx.Button(btn_panel,label="Save")
        self.Bind(wx.EVT_BUTTON, self.cmd_btn_save, btn_save)
        btn_save.SetForegroundColour(wx.Colour(green))
        btn_sizer.AddSpacer(btn_sp)
        btn_sizer.Add(btn_save)
        
        
        btn_restore = wx.Button(btn_panel,label="Restore")
        self.Bind(wx.EVT_BUTTON, self.cmd_btn_restore, btn_restore)
        btn_restore.SetForegroundColour(wx.RED)
        btn_sizer.AddSpacer(btn_sp)
        btn_sizer.Add(btn_restore)
        
        btn_undo = wx.Button(btn_panel,label="Undo")
        self.Bind(wx.EVT_BUTTON, self.cmd_btn_undo, btn_undo)
        btn_undo.SetForegroundColour(green)
        btn_sizer.AddSpacer(btn_sp)
        btn_sizer.Add(btn_undo)

        btn_redo = wx.Button(btn_panel,label="Redo")
        self.Bind(wx.EVT_BUTTON, self.cmd_btn_redo, btn_redo)
        btn_redo.SetForegroundColour(wx.RED)
        btn_sizer.AddSpacer(btn_sp)
        btn_sizer.Add(btn_redo)
        btn_panel.SetSizer(btn_sizer)
        btn_sizer.Fit(btn_panel)

        controls_sizer.Add(btn_panel)
        controls_panel.SetSizer(controls_sizer)
        
        main_sizer.Add(controls_panel)
        controls_sizer.Fit(main_panel)
        main_panel.SetSizer(main_sizer)
        main_sizer.Fit(self)
        self.Show()

    """ controls panel event functions
    """
    def _update_settings(self, name):
        SlTrace.lg("wx_settings_control_panel_demo:"
                   f"_update_settings({name})", "settings_display")
        self._update_fun(name)

    def _update_fun(self, name):
        if self.update_control_fun is not None:
            self.update_control_fun(name)
                    
    def cmd_btn_save(self, event=None):
        self._update_settings("Save")
    
    def cmd_btn_restore(self, event=None):
        self._update_settings("Restore")
    
    def cmd_btn_undo(self, event=None):
        self._update_settings("Undo")
    
    def cmd_btn_redo(self, event=None):
        self._update_settings("Redo")
 
if __name__ == '__main__':
    app = wx.App()
    width = int(400)
    height = int(75)
    size = wx.Size(width,height)
    frame = wx.Frame(None, size=size,
                     title="base_frame: wx_controls_control_panel")
    frame.Show()
    controls_panel = wx.Panel(frame, size=size,
                              name="data panel")
    controls_sizer = wx.BoxSizer(wx.VERTICAL)
    def update_control_fun(name):
        SlTrace.lg(f"button: {name}")
        
    controls_data_panel = SettingsControlPanelDemo(
                controls_panel,
                title="Settings", size=size,
                update_control_fun=update_control_fun) 
    controls_sizer.Add(controls_data_panel, wx.EXPAND)
    controls_panel.SetSizer(controls_sizer)
    controls_panel.Show()
    app.MainLoop()  
