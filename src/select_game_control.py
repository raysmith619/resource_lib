# command_file.py
"""
Game Control - parameters and such
Facilitates setting and display of game controls
"""
from tkinter import *
import re
import os

from select_error import SelectError
from select_trace import SlTrace
from select_control_window import SelectControlWindow            

    
    
    
class SelectGameControl(SelectControlWindow):
    CONTROL_NAME_PREFIX = "game_control"
    DEF_WIN_X = 500
    DEF_WIN_Y = 300
    
        
            
    def _init(self, *args, title=None, control_prefix=None,
              central_control=None, player_control=None,
               **kwargs):
        """ Initialize subclassed SelectControlWindow singleton
             Setup score /undo/redo window
        """
        if title is None:
            title = "Game Control"
        if control_prefix is None:
            control_prefix = SelectGameControl.CONTROL_NAME_PREFIX
        self.player_control = player_control
        self.central_control = central_control
        super()._init(*args, title=title, control_prefix=control_prefix,
                       **kwargs)

    def set_play_control(self, play_control):
        """ Link ourselves to the display
        """
        self.play_control = play_control
        
            
    def control_display(self):
        """ display /redisplay controls to enable
        entry / modification
        """
        if self._is_displayed:
            return

        super().control_display()       # Do base work        
        
        controls_frame = self.top_frame
        controls_frame.pack(side="top", fill="x", expand=True)
        self.controls_frame = controls_frame

        
        running_frame = Frame(controls_frame)
        running_frame.pack()
        running_frame1 = Frame(running_frame)

        running_frame2 = Frame(running_frame)
        
        self.set_fields(running_frame1, "running", title="Running")
        self.set_check_box(field="loop")
        self.set_entry(field="loop_after", label="After", value=5, width=4)
        self.set_sep()
        self.set_button(field="new_game", label="New Game", command=self.new_game)
        self.set_sep()
        self.set_button(field="stop_game", label="Stop Game", command=self.stop_game)

        self.set_fields(running_frame2, "running", title="")
        self.set_button(field="run", label="Run", command=self.run_game)
        self.set_button(field="pause", label="Pause", command=self.pause_game)
        self.set_sep()
        self.set_entry(field="speed_step", label="Speed step", value=-1, width=4)
        
        scoring_frame = Frame(controls_frame)
        self.set_fields(scoring_frame, "scoring", title="Scoring")
        self.set_check_box(field="run_reset", label="Run Resets", value=True)
        self.set_button(field="reset_score",label="Reset Scores", command=self.reset_score)
        self.set_sep()
        self.set_check_box(field="show_ties", label="Show Ties", value=True)

        
        viewing_frame = Frame(controls_frame)
        self.set_fields(viewing_frame, "viewing", title="Viewing")
        self.set_entry(field="columns", label="columns", value=5, width=3)
        self.set_entry(field="rows", label="rows", value=5, width=3)
        
        self.arrange_windows()

    """ Control functions for game control
    """
    def new_game(self):
        self.set_vals()
        if self.play_control is not None:
            self.play_control.new_game("New Game")

    def reset_score(self):
        """ Reset multi-game scores/stats, e.g., games, wins,..
        """
        if self.play_control is not None:
            self.play_control.reset_score()

    
    def stop_game(self):
        self.set_vals()
        if self.play_control is not None:
            self.play_control.stop_game("Stop Game")


    def run_game(self):
        self.set_vals()
        if self.play_control is not None:
            self.play_control.run_cmd()

    def pause_game(self):
        self.set_vals()
        if self.play_control is not None:
            self.play_control.pause_cmd()

    
if __name__ == '__main__':
        
    root = Tk()
    root.withdraw()       # Hide main window

    SlTrace.setProps()
    cF = SelectGameControl(None, title="SelectGameControl Testing", display=True)
    ##cF.open("cmdtest")
        
    root.mainloop()