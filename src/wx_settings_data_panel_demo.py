#wx_settings_data_panel_demo.py
""" 
Chess display settings
data value setting/clearing
"""
import wx

from select_trace import SlTrace, SelectError

from settings_display import SettingsDisplay

class SettingsDataPanelDemo(wx.Panel, SettingsDisplay):

    
    def __init__(self, parent=None, title=None, size=None,
            update_data_fun=None):
        """ Setup data panel
        :parent: containing frame
        :title: optional title
        :size: wx.size
        :update_data_fun: if present function called
                    with settings name, value
                    when widget activated
                        update_fun(name, value)
        """
        if title is None:
            title = "Data"
        if size is None:
            size = wx.Size(200, 200)
        super().__init__(parent, name=title)
        SettingsDisplay.__init__(self, update_data_fun=update_data_fun)


        main_panel = wx.Panel(self, name=title)

        settings_panel = wx.Panel(main_panel, size=size)
        main_sizer = wx.BoxSizer(wx.VERTICAL)        
        main_sizer.Add(settings_panel, wx.EXPAND)
        main_panel.SetSizer(main_sizer)
        main_sizer.Fit(main_panel)

        settings_sizer = wx.BoxSizer(wx.VERTICAL)
        settings_panel.SetSizer(settings_sizer)

        self.cb_print_board = wx.CheckBox(settings_panel, -1,
                                    "Print Board")
        self.Bind(wx.EVT_CHECKBOX, self.cmd_print_board,
                  self.cb_print_board)
        settings_sizer.Add(self.cb_print_board, wx.EXPAND)

        self.cb_print_fen = wx.CheckBox(settings_panel, -1,
                    "Print FEN")
        self.Bind(wx.EVT_CHECKBOX, self.cmd_print_fen,
                  self.cb_print_fen)
        settings_sizer.Add(self.cb_print_fen, wx.EXPAND)

        self.cb_display_move = wx.CheckBox(settings_panel, -1,
                        "Display Move")
        self.Bind(wx.EVT_CHECKBOX, self.cmd_display_move,
                  self.cb_display_move)
        settings_sizer.Add(self.cb_display_move, wx.EXPAND)

        self.cb_display_final_pos = wx.CheckBox(settings_panel, -1,
                        "Display Final Position")
        self.Bind(wx.EVT_CHECKBOX, self.cmd_display_final_pos,
                  self.cb_display_final_pos)
        settings_sizer.Add(self.cb_display_final_pos, wx.EXPAND)

        self.cb_stop_on_error = wx.CheckBox(settings_panel, -1,
                    "Stop on Error")
        self.Bind(wx.EVT_CHECKBOX, self.cmd_stop_on_error,
                  self.cb_stop_on_error)
        settings_sizer.Add(self.cb_stop_on_error, wx.EXPAND)
        
        self.cb_shortest_move_interval = wx.CheckBox(settings_panel, -1,
                    "Use Shortest Move Interval")
        self.Bind(wx.EVT_CHECKBOX, self.cmd_shortest_move_interval,
                  self.cb_shortest_move_interval)
        settings_sizer.Add(self.cb_shortest_move_interval, wx.EXPAND)
        
        self.cb_set_fastest_run = wx.CheckBox(settings_panel, -1,
                    "Set FASTEST Run")
        self.Bind(wx.EVT_CHECKBOX, self.cmd_set_fastest_run,
                  self.cb_set_fastest_run)
        settings_sizer.Add(self.cb_set_fastest_run, wx.EXPAND)
        
        move_interval_panel = wx.Panel(settings_panel)
        move_interval_sizer = wx.BoxSizer(wx.HORIZONTAL)
        move_interval_panel.SetSizer(move_interval_sizer)        
        settings_sizer.Add(move_interval_panel, wx.EXPAND)
        move_interval_panel.SetSizer(move_interval_sizer)
        move_interval_label = wx.StaticText(
            move_interval_panel, wx.ID_ANY, 'Move Interval')
        move_interval_sizer.Add(move_interval_label)
        self.tc_move_interval = wx.TextCtrl(move_interval_panel,
                                    wx.ID_ANY, size=(40,20),
                                    style=wx.TE_PROCESS_ENTER)        
        self.Bind(wx.EVT_TEXT_ENTER, self.cmd_enter_move_interval,
                  self.tc_move_interval)
        move_interval_sizer.Add(self.tc_move_interval, wx.EXPAND)

        settings_sizer.Fit(settings_panel)

        """ Name to info correspondence
            Dictionary by setting name:
            entry either dictionary  of "wid" : widget
                                        "type" : data type
                                             default int
                  OR widget 
        """
        self.name_to_info = {
            "Print_Board"  : self.cb_print_board,
            "Print_FEN"    : self.cb_print_fen,
            "Display_Move" : self.cb_display_move,
            "Display_Final_Position" : self.cb_display_final_pos,
            "Stop_on_Error" : self.cb_stop_on_error,
            "Use_Shortest_Move_Interval" : self.cb_shortest_move_interval,
            "Set_FASTEST_Run" : self.cb_set_fastest_run,
            "Move_Interval" : {"wid" :self.tc_move_interval,
                               "type" : int}
        }

    """ Debugging"""
    
    def rp(self, msg):
        if msg is None:
            msg = " "
        SlTrace.lg(f"SettingsDataPanelDemo: {msg}")
        SlTrace.lg(f"update_data_fun:"
                f" {self.update_data_fun}")
    
    def _update_setting(self, name):
        """ Update widget val, report
        :name: setting name
        """
        val = self.get_name_val(name)
        self._update_data_fun(name, val)
        self.print_name_val(name, val)
    
    def print_name_val(self, name, val):
        msg1 = "Don't " if not val else ""
        SlTrace.lg(msg1 + name)
    
    def cmd_print_board(self, event=None):
        self._update_setting("Print_Board")

    def cmd_display_move(self, event=None):
        self._update_setting("Display_Move")
    
    def cmd_display_final_pos(self, event=None):
        self._update_setting(name = "Display_Final_Position")
    
    def cmd_stop_on_error(self, event=None):
        self._update_setting(name = "Stop_on_Error")
    
    def cmd_print_fen(self, event=None):
        self._update_setting("Print_FEN")
    
    def cmd_shortest_move_interval(self, event=None):
        self._update_setting("Use_Shortest_Move_Interval")
    
    def cmd_set_fastest_run(self, event=None):
        self._update_setting("Set_FASTEST_Run")
    
    def cmd_enter_move_interval(self, event=None):
        self._update_setting("Move_Interval")

    def get_name_info(self, name):
        """ Get expanded info for name
        :name: setting name
        """
        if name not in self.name_to_info:
            raise SelectError(f"{name} not in name_to_info")
        
        name_info = self.name_to_info[name]
        if not isinstance(name_info, dict):
            name_info = {"wid" : name_info}
        if "type" not in name_info:
            name_info["type"] = bool
        return name_info
    
    def get_name_wid(self, name):
        info = self.get_name_info(name)
        return info["wid"]
        
    def get_name_type(self, name):
        info = self.get_name_info(name)
        return info["type"]

    """ Data access methods
    """    
    def get_get_name_val_fun(self, name):
        """ Get get_val function        
        :name: setting name
        :returns: get val function
        """
        wid = self.get_name_wid(name)
        if isinstance(wid, wx.TextCtrl):
           return self.make_tc_get_fun(name) 
        return wid.GetValue
    
    def get_set_name_val_fun(self, name):
        """ Get set_val function
        :name: setting name
        :returns: set function
        """
        wid = self.get_name_wid(name)
        if isinstance(wid, wx.TextCtrl):
           return self.make_tc_set_fun(name) 
        return wid.SetValue

    def make_tc_set_fun(self, name):
        """ make TextCtrl setting call function
        :name: settings name
        """
        wid = self.get_name_wid(name)
        def set_val(value):
            set_str = str(value)
            wid.SetValue(set_str)
        return set_val    

    def make_tc_get_fun(self, name):
        """ make TextCtrl get call function
        :name: settings name
        """
        wid = self.get_name_wid(name)
        var_type = self.get_name_type(name)
        def get_val():
            value = wid.GetValue()
            return var_type(value)
        return get_val    
        
    def get_name_val(self, name):
        """ Get value for name
        NOT USED MUCH - most action is via get_fun's
                    returned by get_get_name_val_fun
        :name: setting name
        :returns: setting value
        """
        get_fun = self.get_get_name_val_fun(name)
        val = get_fun()
        return val        
    
    def set_name_val(self, name, value):
        """ Get widget value for name
        NOT USED MUCH - most action is via set_fun's
                    returned by get_set_name_val_fun

        :name: setting name
        :value: to set
        :returns: widget value
        """
        set_fun = self.get_set_name_val_fun()
        return set_fun(value)

    def set_update_data_fun(self, update_data_fun):
        """ Set link to function which should be called, with
        the item settings name, when any data display
        item is modified by the user
        """
        self.update_data_fun = update_data_fun

            

if __name__ == '__main__':
    app = wx.App()
    width = int(400)
    height = int(400)
    size = wx.Size(width,height)
    frame = wx.Frame(None, size=size,
                     title="base_frame: wx_settings_data_panel")
    frame.Show()
    settings_panel = wx.Panel(frame, size=size,
                              name="data panel")
    settings_sizer = wx.BoxSizer(wx.VERTICAL)
    def data_update_fun(name, value):
        SlTrace.lg(f"""data_update_fun("{name}", {value})""")
        
    settings_data_panel = SettingsDataPanelDemo(settings_panel,
                                title="Settings", size=size) 
    settings_sizer.Add(settings_data_panel, wx.EXPAND)
    settings_panel.SetSizer(settings_sizer)
    settings_panel.Show()
    settings_data_panel.set_update_data_fun(data_update_fun)
    settings_data_panel.rp("After set_update_data_fun")
    app.MainLoop()  
