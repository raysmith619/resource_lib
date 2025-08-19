#settings_server_demo.py  13Aug2025  crs, build demo
""" Demo of settings server (a part of wx_chess_game_display)
"""

class SettingsServerDemo:
    def __init__(self):
        # Mimic game data
        self.setting_game_start_no = 1
        self.setting_game_end_no = None # No limit
        self.setting_is_move_display = True
        self.setting_is_final_position_display = True
        self.setting_is_printing_board = True
        self.setting_is_printing_fen = True
        self.loop_interval = 250    # msec loop interval
        self.setting_is_stop_on_error = True
        
        # combination settings
        self.settings_is_shortest_move = False
        self.settings_is_fastest_run = False

        # settings before use_fastest_run
        self.old_setting_is_move_display = True
        self.old_setting_is_printing_board = False
        self.old_setting_is_printing_fen = False
        self.old_loop_interval = 250    # msec loop interval


    """ More mimicing
    
    Settings with explicit get/set functions
    "Use Shortest Move Interval" :
    """
    
    def get_shortest_move(self):
        return self.settings_is_shortest_move
    
    def set_shortest_move(self, value=True):
        self.settings_is_shortest_move = value
        self.setting_move_interval = 2
        
    def get_fastest_run(self):
        return self.settings_is_fastest_run

    def set_fastest_run(self, value=True):
        self.settings_use_fastest_run = value
        if value:
            self.old_setting_is_move_display = self.setting_is_move_display
            self.old_setting_is_printing_board = self.setting_is_printing_board
            self.old_setting_is_printing_fen = self.setting_is_printing_fen
            self.old_loop_interval = self.loop_interval
            self.setting_is_move_display = False
            self.setting_is_printing_board = False
            self.setting_is_printing_fen = False
            self.loop_interval = 1    # msec loop interval
        else:
            self.setting_is_move_display = self.old_setting_is_move_display
            self.setting_is_printing_board = self.old_setting_is_printing_board
            self.setting_is_printing_fen = self.old_setting_is_printing_fen
            self.loop_interval = self.old_loop_interval
                
        return self.settings_use_fastest_run
