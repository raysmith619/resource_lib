#wx_chess_settings_frame.py
import sys
import argparse
import wx

from select_trace import SlTrace
from settings_control import SettingsControl

from settings_server_demo import SettingsServerDemo
from wx_settings_display_demo import SettingsDisplayDemo

class ChessSettingsFrame(wx.Frame):
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

if __name__ == '__main__':

    app = wx.App()
    SlTrace.setProps()
    SlTrace.clearFlags()
                
                
            
    csf = ChessSettingsFrame(None)

    app.MainLoop()
    SlTrace.lg("After app.MainLoop")
    tF.on_close()
