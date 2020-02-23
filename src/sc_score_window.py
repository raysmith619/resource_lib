# sc_score_window.py    21-Feb_2019  crs
"""
Window control for display of game score_window
"""
from tkinter import *

from select_trace import SlTrace
from select_error import SelectError
from select_control_window import SelectControlWindow            
from sc_player_control import PlayerControl
from select_control import SelectControl

class PlayerFields:
    def __init__(self, player, widgets={}):
        self.player = player
        self.widgets = widgets
                
class ScoreWindow(SelectControlWindow):
    CONTROL_NAME_PREFIX = "score_control"
    DEF_WIN_X = 500
    DEF_WIN_Y = 0
    cF = SelectControl()        # Access to program variables
    
    wd = 15
    col_infos = [
        ["name", "name", wd],
        ["label", "label", wd],
        ["score", "score", wd],
        ["played", "played", wd],
        ["wins", "wins", wd],
        ]
    col_infos_wins = [
        ["name", "name", wd],
        ["label", "label", wd],
        ["score", "score", wd],
        ["played", "played", wd],
        ["wins", "wins", wd],
        ]
    col_infos_ties = [
        ["name", "name", wd],
        ["label", "label", wd],
        ["score", "score", wd],
        ["played", "played", wd],
        ["wins", "wins", wd],
        ["ties", "ties", wd],
        ]
        
            
    def _init(self, *args, title=None, control_prefix=None,
              play_control=None, player_control=None, show_ties=True,
              undo_micro_move=False,
              undo_micro_move_command=None,
               **kwargs):
        """ Initialize subclassed SelectControlWindow singleton
             Setup score /undo/redo window
             :undo_micro_move: Undo every move not just user moves
             :undo_micro_move_command: command to call when undo_micro_move
                 changes default: no call
        """
        self.players = {}      # Keep track of players, fields in score board
        if title is None:
            title = "Game Control"
        if control_prefix is None:
            control_prefix = ScoreWindow.CONTROL_NAME_PREFIX
        if player_control is None:
            player_control = PlayerControl()
        self.player_control = player_control
        if player_control is not None:
            self.player_control.set_score_control(self)
        self.play_control = play_control
        self.show_ties = show_ties
        self.undo_micro_move = self.cF.make_val("undo_micro_move", undo_micro_move,
                                                repeat=True)
        self.undo_micro_move_command = undo_micro_move_command
        super()._init(*args, title=title, control_prefix=control_prefix,
                       **kwargs)
        self.show_ties = show_ties
        if show_ties:
            self.col_infos = ScoreWindow.col_infos_ties
        else:
            self.col_infos = ScoreWindow.col_infos
        if self.display:
            self.control_display()    

    def control_display(self):            
        """ display /redisplay controls to enable
        entry / modification
        """
        if self._is_displayed:
            return

        super().control_display()       # Do base work        
        move_frame = self.top_frame
        move_frame.pack(side="top", fill="x", expand=True)
        move_no_frame = Frame(move_frame)
        move_no_frame.pack()
        move_no = 0
        move_no_str = "Move: %d" % move_no
        move_font = ('Helvetica', '25')
        self.move_no_label = Label(move_no_frame,
                              text=move_no_str,
                              font=move_font
                              )
        self.move_no_label.pack(side="left", expand=True)
        ###move_no_label.config(width=2, height=1)
        
        scores_frame = Frame(self.mw)
        scores_frame.pack()
        players = self.player_control.get_players()
        
        headings_frame = Frame(scores_frame)
        headings_frame.pack()
        self.set_field_headings(headings_frame)
        self.players_frame = Frame(scores_frame)
        self.players_frame.pack()
        for player in players:
            self.add_player(player)

        
        bw = 5
        bh = 1
        undo_font = ('Helvetica', '50')
        undo_button = Button(master=move_frame, text="Undo",
                            font=undo_font,
                            command=self.undo_button)
        undo_button.pack(side="left", expand=True)
        undo_button.config(width=bw, height=bh)
        redo_button = Button(master=move_frame, text="ReDo",
                             font=undo_font,
                            command=self.redo_button)
        redo_button.pack(side="left", expand=True)
        redo_button.config(width=bw, height=bh)
    
        self.set_sep(10*" ")
        undo_micro_move = self.cF.get_val("undo_micro_move",
                                           self.undo_micro_move)
        self.set_check_box(field="undo_micro_move",
                           label="micro moves", value=undo_micro_move,
                           command=self.undo_micro_move_change )
        ###self.setup_score_window(move_no_label=move_no_label)
        self.arrange_windows()
        self.mw.bind( '<Configure>', self.win_size_event)
        self.update_window()

    def undo_micro_move_change(self, new_value):
        """ Update undo_micro_move setting
        :new_value: updated value
        """
        self.cF.set_val("undo_micro_move",
                          new_value)
        if self.undo_micro_move_command is not None:
            self.undo_micro_move_command(new_value)
        
    def add_player(self, player):
        if player.id in self.players:
            return              # Only add first
        
        self.players[player.id] = PlayerFields(player)
        player_frame = Frame(self.players_frame)
        player_frame.pack(side="top", fill="both", expand=True)
        self.set_player_frame(player_frame, player, "name")
        self.set_player_frame(player_frame, player, "label")
        self.set_player_frame(player_frame, player, "score")
        self.set_player_frame(player_frame, player, "played")
        self.set_player_frame(player_frame, player, "wins")
        if self.show_ties:
            self.set_player_frame(player_frame, player, "ties")
        
    
    def get_prop_key(self, name):
        """ Translate full  control name into full Properties file key
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
        if prop_val is None:
            return default
        
        if isinstance(default, bool):
            if prop_val == "1" or prop_val.lower() == "true":
                return True
            return False
        
        if isinstance(default, int):
            if prop_val == "":
                return 0
           
            return int(prop_val)
        elif isinstance(default, float):
            if prop_val == "":
                return 0.
           
            return float(prop_val)
        else:
            return prop_val
        
       
    def set_field_headings(self, field_headings_frame):
        """ Setup player headings, possibly recording widths
        """
        col_infos = self.col_infos
        for info_idx, col_info in enumerate(col_infos):
            field_name = col_info[0]
            if len(col_info) >= 2:
                heading = col_info[1]
            else:
                heading = field_name
            ###width = 20      # Hack
            if len(col_info) >= 3:
                width = col_info[2]
            heading_label = Label(master=field_headings_frame,
                                  text=heading, anchor="w",
                                  justify=CENTER,
                                  width=width)
            heading_label.grid(row=0, column=info_idx, sticky=NSEW)
            field_headings_frame.columnconfigure(info_idx, weight=1)
    

    def set_player_frame(self, frame, player, field):
        """ Create player info line
        Adapted form PlayerControl.set_player_control
        :frame: players frame
        :player: player info
        :field: name of field
        """
        col_infos = self.col_infos
        col_info = None     # Set if name found
        idx = 0             # Bumped after each check
        for cinfo in col_infos:
            if cinfo[0] == field:
                cname = field
                if len(cinfo) >=2:
                    cheading = cinfo[1]
                else:
                    cheading = cname
                if len(cinfo) >= 3:
                    cwidth = cinfo[2]
                else:
                    cwidth = None
                col_info = (cname, cheading, cwidth)
                break
            idx += 1        # Next grid column
        if col_info is None:
            raise SelectError("field name %s not found" % field)
        
        field_name = col_info[0]
        value = player.get_val(field_name)
        width = col_info[2]
        frame = Frame(frame, height=1, width=width)
        frame.grid(row=player.id, column=idx, sticky=NSEW)

        if field_name == "name":
            self.set_player_frame_name(frame, player, value, width=width)
        elif field_name == "label":
            self.set_player_frame_label(frame, player, value, width=width)
        elif field_name == "score":
            self.set_player_frame_score(frame, player, value, width=width)
        elif field_name == "played":
            self.set_player_frame_played(frame, player, value, width=width)
        elif field_name == "wins":
            self.set_player_frame_wins(frame, player, value, width=width)
        elif field_name == "ties":
            self.set_player_frame_ties(frame, player, value, width=width)
        else:
            raise SelectError("Unrecognized player field_name: %s" % field_name)    

    
            
    def add_widget(self, player, field, widget):
        """ add entries widget
        :player: player
        :field: field's name
        """
        widget.config({"fg":player.color, "bg":player.color_bg})
        self.players[player.id].widgets[field] = widget
        
    def set_player_frame_name(self, frame, player, value, width=None):
        content = player.ctls_vars["name"]
        val_entry = Entry(frame, textvariable=content, width=width)
        self.add_widget(player, "name", val_entry)
        ##val_entry.pack(side="left", fill="none", expand=True)
        val_entry.pack(side="left", fill="none", expand=True)

    def set_player_frame_label(self, frame, player, value, width=None):
        content = player.ctls_vars["label"]
        val_entry = Entry(frame, textvariable=content, width=width)
        self.add_widget(player, "label", val_entry)
        val_entry.pack(side="left", fill="none", expand=True)


    def set_player_frame_score(self, frame, player, value, width=None):
        content = player.ctls_vars["score"]
        val_entry = Entry(frame, textvariable=content, width=width)
        self.add_widget(player, "score", val_entry)
        val_entry.pack(side="left", expand=True)

    def set_player_frame_played(self, frame, player, value, width=None):
        content = player.ctls_vars["played"]
        val_entry = Entry(frame, textvariable=content, width=width)
        self.add_widget(player, "played", val_entry)
        val_entry.pack(side="left", expand=True)

    def set_player_frame_wins(self, frame, player, value, width=None):
        content = player.ctls_vars["wins"]
        val_entry = Entry(frame, textvariable=content, width=width)
        self.add_widget(player, "wins", val_entry)
        val_entry.pack(side="left", expand=True)

    def set_player_frame_ties(self, frame, player, value, width=None):
        content = player.ctls_vars["ties"]
        val_entry = Entry(frame, textvariable=content, width=width)
        self.add_widget(player, "ties", val_entry)
        val_entry.pack(side="left", expand=True)

    def update_colors(self):
        """ Update field colors
        """
        for window_player in self.players.values():
            player = window_player.player
            if player.playing:
                wplayer = self.players[player.id]
                widgets = wplayer.widgets
                for widget in widgets.values():
                    widget.config({"fg": player.color, "bg" : player.color_bg})
    
    def update_window(self):
        if self.mw is None:
            return
        
        if self.move_no_label is not None and self.play_control is not None:
            scmd = self.play_control.get_last_cmd()
            if scmd is None:
                self.move_no_label.config(text="Start")
            else:
                move_no_str = "Move: %d" % scmd.move_no
                self.move_no_label.config(text=move_no_str)
        players = self.player_control.get_players()
        for player in players:
            if player.id not in self.players:
                self.add_player(player)              # add if not present
            score_ctl_var = player.ctls_vars["score"]
            score = player.get_score()
            score_ctl_var.set(score)
            SlTrace.lg("score: %d %s" % (score, player), "score")
            played_ctl_var = player.ctls_vars["played"]
            played = player.get_played()
            played_ctl_var.set(played)
            SlTrace.lg("played: %d %s" % (played, player), "score")
            wins_ctl_var = player.ctls_vars["wins"]
            wins = player.get_wins()
            wins_ctl_var.set(wins)
            SlTrace.lg("wins: %d %s" % (wins, player), "score")
        ###self.update_colors()

    def update_score(self, move_no=None, players=None):
        """ Update score board
        :move_no: move number
        :players: player/s, if present, whose score/s is updated
        """
        if move_no is not None:
            move_no_str = "Move: %d" % move_no
            self.move_no_label.config(text=move_no_str)
            
        if players is not None:
            if not isinstance(players, list):
                players = [players]
            for player in players:     # list of one
                score_ctl_var = player.ctls_vars["score"]
                score = player.get_score()
                score_ctl_var.set(score)
                SlTrace.lg("score: %d %s" % (score, player), "score")
                played_ctl_var = player.ctls_vars["played"]
                played = player.get_played()
                played_ctl_var.set(played)
                SlTrace.lg("played: %d %s" % (played, player), "score")
                wins_ctl_var = player.ctls_vars["wins"]
                wins = player.get_wins()
                wins_ctl_var.set(wins)
                SlTrace.lg("wins: %d %s" % (wins, player), "score")
        ###self.update_colors()    
        
        
    def undo_button(self):
        SlTrace.lg("undoButton")
        res = self.play_control.undo(undo_micro_move=self.undo_micro_move)
        return res
                
        
    def redo_button(self):
        SlTrace.lg("redoButton")
        res = self.play_control.redo(undo_micro_move=self.undo_micro_move)
        return res
