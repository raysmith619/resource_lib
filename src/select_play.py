# select_play.py
import os
from tkinter import *
import random    
import time
from datetime import datetime  
from datetime import timedelta
import copy  
import cProfile, pstats, io         # profiling support
###from pstats import SortKey

from select_fun import *
from select_trace import SlTrace
from select_error import SelectError
from sc_player_control import PlayerControl        
from select_command_play import SelectCommandPlay
from select_play_cmd import SelectPlayCommand
from select_command_manager import SelectCommandManager
from select_part import SelectPart
from select_player import SelectPlayer
from select_message import SelectMessage
from active_check import ActiveCheck        
from sc_score_window import ScoreWindow
from select_blinker_state import BlinkerMultiState
from select_kbd_cmd import SelectKbdCmd
from dots_commands import DotsCommands

from gr_input import gr_input

class SelectPlay:
    def __init__(self, board=None, mw=None,
                 display_game=True,
                 profile_running=False,
                 numgame=None,
                 player_control=None,
                 game_control=None,
                 results_file=None,
                 score_window=None,
                 msg_frame=None,
                 start_run=True,
                 on_end=None,
                 on_exit=None,
                 run_check_ms=10,
                 auto_play_check_ms=10,
                 cmd_stream=None,
                 src_lst=False,
                 stx_lst=False,
                 btmove=.1, move_first=None,
                 before_move=None, after_move=None,
                 show_ties=False,
                 undo_len=100,
                 undo_micro_move=False):
        """ Setup play
        :board: playing board (SelectDots)
        :mw: Instance of Tk, if one, else created here
        :numgame: if present, limit play to numgame games
        :msg_frame: base frame for game messages
                    default: create one
                default: no limit
        :display_game: display game play on screen
                    Set False to reduce execution time for
                    execution which does not need/want
                    screen display of game progress
                    default: True
        :profile_running: profile running_loop
                    default: False
        :start_run: Start running default: True
        :run_check_ms: Time for running loop check
                default = 10mec
        :on_exit: function to call on exit / window destroy
        :on_end: function, if present, to call at end of game
        :before_move: function, if any, to call before move
        :after_move: function, if any, to call after move
        :show_ties: ties are shown
        :undo_len: maximum length of undo
            default: 100
        :undo_micro_move: undo/redo each micro move
                        default: undo/redo to previous user move
        :cmd_stream: command stream if any,
                If present, get commands from here
                default: none
        :src_lst: True - list source as run
        :stx_lst: True - list command stream as run
        """
        self.display_game = display_game
        self.numgame = numgame
        self.profile_running = profile_running
        self.playing = True     # Hack to suppress activity on exit event
        if score_window is None:
            score_window = ScoreWindow()
        self.score_window = score_window
        if game_control is None:
            raise SelectError("SelectPlay: manditory game_control is missing")
        self.results_file = results_file
        self.game_control = game_control
        game_control.set_play_control(self)     # Link ourselves to display/control
        self.speed_step = -1
        if board is None:
            raise SelectError("select_play.board missing")
        self.board = board
        
        if msg_frame is None:
            msg_frame = Frame(board.canvas)
            msg_frame.pack(side="bottom", expand=YES, fill=BOTH)
        self.msg_frame_base = msg_frame         # Container for actual frame
        self.msg_frame = None                   # Actual frame
        self.cmd_stream = cmd_stream
        self.cmd_stream_proc = SelectPlayCommand(self, cmd_stream)
        if self.cmd_stream is not None:
            self.cmd_stream.set_play_control(self)
            self.cmd_stream.set_cmd_stream_proc(self.cmd_stream_proc)
        self.undo_len = undo_len
        self.undo_micro_move = undo_micro_move
        self.command_manager = SelectCommandManager(self,
                                            undo_micro_move=self.undo_micro_move,
                                            undo_len=self.undo_len)
        SelectCommandPlay.set_management(self.command_manager, self)
        if mw is None:
            mw = Tk()
        self.mw = mw
        self.mw.protocol("WM_DELETE_WINDOW", self.delete_window)
        self.in_game = False
        self.running = False
        self.run_check_ms = run_check_ms
        self.start_run = start_run
        self.on_exit = on_exit
        self.auto_play_check_ms = auto_play_check_ms
        self.auto_delay_waiting = False
        self.manual_moves = []          # Initialize empty list

        self.btmove = btmove
        if player_control is None:
            player_control = PlayerControl(display=False)
        self.player_control = player_control
        self.player_index = 0
        self.messages = []      # Command messages, if any
        self.first_time = True       # flag showing first time
        self.moves = []
        if board.area.down_click_call is None:
            board.add_down_click_call(self.down_click)
            SlTrace.lg("board.area.down_click_call: %s" % board.area.down_click_call)
        if self.board.area.down_click_call is None:
            raise SelectError("board.area.down_click_call is not set")
        
        board.add_new_edge_call(self.new_edge)
        self.cur_message = None         # Currently displaying message, if any
        self.select_cmd = None
        self.before_move = before_move
        self.after_move = after_move
        self.clear_mods()
        self.move_no_label = None       # Move no label, if displayed
        self.waiting_for_message = False
        ###self.mw.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.kbd_cmd = SelectKbdCmd(self)
        ###self.board.set_down_click_call(self.down_click_made)
        self.on_end = on_end
        if self.start_run:
            self.mw.after(self.run_check_ms, self.running_loop)
        self.restart_game = False        # Signal to restart after end
        self.game_stopped = False              # Stop loop (one time)
        self.show_ties = show_ties
        self.running = False     # Initially not running
        self.run = False         # Initially not running
        self.ngame = 0
        
        if self.profile_running:
            self.pr = cProfile.Profile()
            self.pr.enable()
        
        
    def running_loop(self, run_check_ms=None):
        """ Run game (loop) untill self.running set false
        :run_check_ms: loop checking time default: current checking time
        """
        if self.board.area.down_click_call is None:
            raise SelectError("board.area.down_click_call is not set")
        if self.numgame is not None and self.ngame >= self.numgame:
            SlTrace.lg("running_loop: ngame={:d} > numgame {:d}".
                       format(self.ngame, self.numgame))
            self.running = False
            self.run = False
            return
 
        self.running = True     # Still in game
        self.run = True         # progressing (not paused)
        self.first_time = True 
        self.game_start_ts = SlTrace.getTs(6)
        self.game_control_updates()
        if run_check_ms is not None:
            self.run_check_ms = run_check_ms
        BlinkerMultiState.enable()
        
        while self.running:
            SlTrace.lg("running_loop", "running_loop")
            if ActiveCheck.not_active():
                break
            SlTrace.lg("running_loop active", "running_loop")
            self.mw.update_idletasks()
            if (self.cmd_stream is not None
                    and not self.cmd_stream.is_eof()):
                self.run_file()
                continue    # Check if more 
            if self.running and self.run:
                if self.board is None:
                    SlTrace.lg("sp.board is None")
                    break
                SlTrace.lg("running_loop self.running and self.run", "running_loop")
                if self.first_time:
                    if self.numgame is not None and self.ngame > self.numgame:
                        self.running = False
                        self.run = False
                        break
                    self.start_game()
                    self.first_time = False
                else:
                    SlTrace.lg("running_loop self.start_move", "running_loop")
                    if self.start_move():
                        SlTrace.lg("running_loop successful start_move", "running_loop")
                        self.next_move_no()
                    SlTrace.lg("running_loop after start_move", "running_loop")
            else:
                self.mw.update()        
                
        SlTrace.lg("running_loop after loop", "running_loop")
        BlinkerMultiState.disable()
                                
        if self.on_end is not None:
            SlTrace.lg("running_loop doing on_end", "running_loop")
            self.mw.after(0, self.on_end)       # After run processing

    
    def run_file(self, src_file=None):
        """ Run file command
        :src_file: source file name
                 default: self.src_file_name
        """
        res = self.cmd_stream.run_file(src_file=src_file,
                    cmd_execute=self.play_stream_command)
        return res

        
        
    def user_cmd(self, cmd):
        """ User level command, by which the user/operators
        interact with the game
        Initially to facilitate command file processing but
        may provide a single point of control to facitate simulation
        and testing.
        :cmd: User level command specification
        """
        keysym = cmd.name
        if keysym == "undo": keysym = "u"
        if keysym == "redo": keysym = "r"
        if re.match(r'Up|Down|Left|Right|Enter|Plus|Minus'
                    + r'i|j|u|r', keysym):
            self.key_press_cmd(ec_keysym=keysym)
        else:
            raise SelectError("Don't recognize cmd: %s"
                              % cmd)
        self.show_display()
            
            
        
    def new_edge_mark(self, edge, highlight=True):
        """ Set new position (edge)
        :edge: location
        :highlight: True highlight edge default: True
        """
        if self.keycmd_edge_mark is not None:
            self.keycmd_edge_mark.highlight_clear()     # Clear previous
            
        if highlight:
            edge.highlight_set()
        self.keycmd_edge_mark = edge
        
        
    def make_new_edge(self, edge=None, dir=None, rowcols=None, display=True):
        if edge is not None:
            self.new_edge(edge)
            return
        
        row = rowcols[0]
        col = rowcols[1]
        SlTrace.lg("make_new_edge: %s row=%d col=%d" % (dir, row, col), "edge")
        edge = self.get_part(type="edge", sub_type=dir, row=row, col=col)
        if edge is None:
            SlTrace.lg("No edge(%s) at row=%d col=%d" % (dir, row, col))
            self.beep()
            return
        
        self.new_edge(edge)
        if display:
            self.display_update()
                
    def get_xy(self):
        """ get current mouse position (or last one recongnized
        :returns: x,y on area canvas, None if never been anywhere
        """
        return self.board.get_xy()


    def get_part(self, id=None, type=None, sub_type=None, row=None, col=None):
        """ Get basic part
        :id: unique part id
        :returns: part, None if not found
        """
        return self.board.get_part(id=id, type=type, sub_type=sub_type, row=row, col=col)
    
    
    def get_selects(self):
        """ GEt list of selected part(ids)
        :returns: list, empty if none
        """
        return self.board.get_selects()


    def get_selected_part(self):
        """ Get selected part
        :returns: part, None if none selected
        """
        return self.board.get_selected_part()
                
    
    def get_parts_at(self, x, y, sz_type=SelectPart.SZ_SELECT):
        """ Check if any part is at canvas location provided
        If found list of parts
        :Returns: SelectPart[]
        """
        return self.board.get_parts_at(x,y,sz_type=sz_type)


    def run_cmd(self):
        """ Run / continue game
        """
        self.run = True


    def run_cmd_file(self, src_file=None):
        """ Run command stream file
        Assumes running in running_loop
        :src_file: source file name default (None) cmd_file entry
        """
        if src_file is not None:
            self.cmd_stream.set_ctl_val("src_file_name", src_file)
            
        self.cmd_stream.reset(src_file=src_file)
        self.cmd_stream.run_cmd_file(src_file=src_file)
        ###self.cmd_stream.set_eof(False)
        
    
    def pause_cmd(self):
        """ Pause game
        """
        self.run = False


    def play_stream_command(self, stcmd=None):
        """ Play next command from command stream
        :returns: True if OK, False if error or EOF
        :stcmd: stream command default: get next command
        """
        if self.cmd_stream is None:
            return False
        if stcmd is None:
            stcmd = self.cmd_stream.get_cmd()
        if stcmd is None:
            return False
        
        res = self.cmd_stream_proc.do_stcmd(stcmd)
        return res
                
        
    def annotate_squares(self, squares, edge=None, player=None):
        """ Annotate squares in board with players info
        Create command and execute which reflects change
        :squares: list of squares to annotate
        :edge: edge used to complete square
        :player: player whos info is used
                Default: use current player
        """
        self.get_cmd("annotate_squares")
        self.add_prev_parts(edge)
        if player is None:
            player = self.get_player()
        if not isinstance(squares, list):
            squares = [squares]
        for square in squares:
            square.part_check(prefix="annotate_squares")
        for square in squares:
            ###sc = select_copy(square)
            sc = square
            self.add_prev_parts(square)
            sc.set_centered_text(player.label, display=False,
                                     color=player.color,
                                     color_bg=player.color_bg)
            if SlTrace.trace("annotate_square"):
                SlTrace.lg("annotate_square: %s\n%s"
                         % (sc, sc.str_edges()))
            self.add_new_parts(sc)
        self.complete_cmd()
        return

    def show_display(self):
        self.mw.update_idletasks()



    def set_changed(self, parts):
        """ Set part as changed since last display
        :parts:    part/id or list part(s) changed
        """
        self.command_manager.set_changed(parts)
        
        
    def clear_changed(self, parts):
        """ Clear part as changed
        :parts: part/id or list cleared
        """
        self.command_manager.clear_changed(parts)

            
    def get_changed(self, clear=False):
        """ Get list of changed parts
        :clear: clear list on return
                default: False
        """
        return self.command_manager.get_changed(clear=clear)

        
    def setup_score_window(self):
        """ Setup interaction with Move/Undo/Redo
        """
        if self.score_window is not None:
            self.score_window.destroy()
                        
        self.score_window = ScoreWindow()


    def close_score_window(self):
        """ close score window
        """
        if self.score_window is None:        
            return
        
        self.score_window.destroy()
        self.score_window = None
        
        

    def get_canvas(self):
        return self.board.canvas

    def get_height(self):
        return self.get_canvas().winfo_height()

    def get_width(self):
        canvas = self.get_canvas()
        if canvas is None:
            return 0

        return canvas.winfo_width()

    def announce_player(self, tag):
        """ Announce current player, execute command
        Begins move
        """
        player = self.get_player()
        prev_player = self.get_prev_player()
        if player != prev_player:
            was_str = " was %s" % prev_player
        else:
            was_str = ""
        SlTrace.lg("announce_player: %s %s%s"
                    % (tag, player, was_str), "execute")
        scmd = self.get_cmd("announce_player", has_prompt=True)
        self.set_prev_player(prev_player)
        self.set_new_player(player)
        text = "It's %s's turn." % player.name
        self.trace_scores("announce_player:")
        SlTrace.lg(text, "player")
        self.add_message(text, color=player.color)
        self.do_cmd()       # Must display now
        if self.before_move is not None:
            self.before_move(scmd)
        self.enable_moves()
        self.trace_scores("announce_player before auto:")
        if player.auto:
            self.auto_play_pause()


    def add_message(self, text, cmd=None,
                    color=None, font_size=40,
                    time_sec=None):
        """ Put message up. If time is present bring it down after time seconds
        NOTE: message is displayed when command is executed
        :cmd: command for message
                default: add to current command, if one
                        else create and execute new command
        :time: time for message
                default: leave message there till next message
        """
        if not isinstance(text, str):
            raise SelectError("add_message: text is not str - "
                              + str(text))
        message = SelectMessage(text, color=color,
                                  font_size=font_size,
                                  time_sec=time_sec)
        if cmd is None:
            cmd = self.select_cmd
        if cmd is None:
            cmd = self.get_cmd("add_message")
            cmd.add_message(message)
            self.do_cmd()               # Remove command from consideration
        else:
            cmd.add_message(message)


    def destroy(self):
        """ Relinquish game resources, e.g. window(s)
        """
        if self.cur_message is not None:
            self.cur_message.destroy()
            self.cur_message = None
        if self.board is not None:
            self.board.destroy()
            self.board = None
        if self.game_control is not None:
            self.game_control.destroy()
            self.game_control = None
        if self.player_control is not None:
            self.player_control.destroy()
            self.player_control = None
        if self.score_window is not None:
            self.score_window.destroy()
            self.score_window = None
            


       
    def delete_window(self):
        """ Process Trace Control window close
        """
        self.mw.eval('::ttk::CancelRepeat')
        SlTrace.lg("Closing windows")
        '''    
        ActiveCheck.clear_active()  # Disable activities
        if self.score_win is not None:
            self.score_win.destroy()
            self.score_win = None
        if self.mw is not None and self.mw.winfo_exists():
            self.mw.quit()
            self.mw.destroy()
            self.mw = None
        '''
        if self.on_exit is not None:
            self.on_exit()
        
        sys.exit()      # Else quit
        
        
    def disable_moves(self):
        """ Disable(ignore) moves by user
        """
        self.board.disable_moves()
        
        
    def enable_moves(self):
        """ Enable moves by user
        """
        self.board.enable_moves()


    def display_print(self, tag, trace):
        SlTrace.lg("display_print: " + tag, trace)
        

    def display_update(self):
        SlTrace.lg("display_update: ", "execute")
        self.command_manager.display_update()
        
    
    def select_print(self, tag, trace):
        SlTrace.lg("select_print: "  + tag, trace)    


    def display_messages(self, messages):
        """ Display cmd messages
        :messages:  messages to be displayed in order
        """
        if self.mw is None:
            return
        
        if not self.display_game:
            return
        
        for message in messages:
            self.do_message(message)
    
    
    def show_score_window(self):
               
        if not self.display_game:
            return

        if self.mw is None:
            return
        if self.score_window is None:
            self.score_window = ScoreWindow(play_control=self.player_control, show_ties=self.show_ties)
        self.score_window.update_window()
    
    
    def clear_score_window(self):
        if self.mw is None:
            return
        
        if self.score_window is not None:
            self.score_window.delete_window()
    
    
    def update_score(self, move_no=None, players=None, edge=None):
        """ Update score
            Update results_file if appropriate
        """
        if self.results_file is not None:
            row = edge.row
            col = edge.col
            pln = self.get_player_num()
            self.results_file.next_move(player=pln, row=row, col=col)
        
        if self.mw is None:
            return

        if not self.display_game:
            return
        
        if self.score_window is None:
            return
        
        self.score_window.update_score(move_no=move_no, players=players)


    def update_score_window(self):
        """ Update score window based on current states
        """

        if not self.display_game:
            return

        if self.score_window is not None:
            self.score_window.update_window()
        
    def wait_message(self, message=None):
        """ Wait till message completed
        :message: message being displayed
                default: current message
        """
        if not self.mw.winfo_exists():
            return

        if not self.display_game:
            return
                
        self.waiting_for_message = True
        if message is None:
            message = self.cur_message
        if (message is not None
                and message.end_time is not None):
            while True:
                now = datetime.now()
                if  now >= message.end_time:
                    self.cur_message = None
                    SlTrace.lg("End of message waiting", "message")
                    break
                if self.mw is not None and self.mw.winfo_exists():
                    self.mw.update()
                self.mw.after(int((message.end_time-now)*1000))   # rather than loop time.sleep(.01)
        if self.cur_message is not None:
            self.cur_message.destroy()
            self.cur_message = None
        self.waiting_for_message = False


    def is_waiting_for_message(self):            
        """ Check if waiting for message
        Used to ignore to fast actions
        """
        return self.waiting_for_message


    def ignore_if_busy(self):
        """ beep if we're too busy to proceed
        :returns: True if busy
        """
        if self.is_waiting_for_message():
            self.beep()
            return True
        return False


    def beep(self):
        import winsound
        winsound.Beep(500, 500)

    
    def do_message(self, message):
        """ Put message up. If time is present bring it down after time seconds    
        :time: time for message
                default: leave message there till next message
        :cmd: Add to cmd if one open
        """
        
        if not self.display_game:
            return
        
        
        SlTrace.lg("do_message(%s)" % (message.text), "execute")
        if not self.run:
            return
        
        if (self.mw is None or not self.mw.winfo_exists()
            or self.msg_frame_base is None
            or not self.msg_frame_base.winfo_exists()):
            return
        
        self.wait_message(message)
        if self.msg_frame is not None:
            self.msg_frame.destroy()        # Remove all message frames
            self.msg_frame = None
        self.msg_frame = Frame(self.msg_frame_base)
        self.msg_frame.pack(side="top", expand=YES, fill=BOTH)
        text = message.text
        color = message.color
        font_size = message.font_size
        if font_size is None:
            font_size=40
        time_sec = message.time_sec

        
        if (self.mw is None or not self.mw.winfo_exists()
            or self.msg_frame is None
            or not self.msg_frame.winfo_exists()):
            return
        
        if self.mw is not None and self.mw.winfo_exists():
            if self.cur_message is not None:
                self.cur_message.destroy()
                self.cur_message = None
        width = self.get_width()
        if width < 500:
            width = 500
        message.msg = Message(self.msg_frame, text=text, width=width) # Seems to be pixels!
        message.msg.config(fg=color, bg='white',
                        anchor=S,
                        font=('times', font_size, 'italic'))
        message.msg.pack(side="top")
        ###message.msg.pack(side="bottom")
        self.cur_message = message
        if time_sec is not None:
            if self.speed_step >= 0:
                time_sec = self.speed_step          # Modify for view / debugging
            end_time = datetime.now() + timedelta(seconds=time_sec)
            message.end_time = end_time

    def end_message(self):
        """ End current message, if any
        Used to speed up such things as redo/undo
        """
        if self.cur_message is not None:
            self.cur_message.end_time = datetime.now()
            self.wait_message()
 
            
    def mark_edge(self, edge, player, move_no=None):
        """ Mark edge - set up current command
        Select  new edge, clearing other selected
        :edge: edge being marked
        :player: player selecting edge
        """
        edge.highlight_clear(display=False)
        edge.turn_on(player=player, move_no=move_no, display=False)
        return
    
    
    def message_delete(self):
        """ Delete message if present
        Usually called after wait time
        """
        SlTrace.lg("Destroying timed message", "message")
        if self.cur_message is not None:
            SlTrace.lg("Found message to destroy", "message")
            self.cur_message.destroy()
            self.cur_message = None

    def get_messages(self):
        """ Get current message, if any
        else returns None
        """
        return self.messages


    def displayPrint(self):
        SlTrace.lg("do_cmd(%s) display TBD"  % ("cmd???"), "execute")
        


    def selectPrint(self):
        SlTrace.lg("do_cmd(%s) select TBD"  % (self.action), "execute")

    

    def get_cmd(self, action=None, has_prompt=False, undo_unit=False,
                flush=False, display=True):
        """ Get current command, else new command
        :action: - start new command with this action name
                defalt use current cmd
        :has_prompt: True cmd contains prompt
        :undo_unit: True - this command is single undoable unit
                    default: False
        :flush: execute any command in progress
                default: False
        :display: display at end of command default: False
        """
        if flush and self.select_cmd is not None:
            self.do_cmd()
        if action is None:
            cmd = self.select_cmd
            if cmd is None:
                raise SelectError("get_cmd: No name for SelectCommand")
            return cmd
        else:
            if self.select_cmd is not None:
                raise SelectError("get_cmd: previous cmd(%s) not completed"
                                   % self.select_cmd)
        self.select_cmd = SelectCommandPlay(action, has_prompt=has_prompt,
                                             undo_unit=undo_unit,
                                             display=display)
        return self.select_cmd


    def get_current_edge(self):
        """ Get current marker direction, (row, col)
        """
        edge = self.get_selected_part()
        if edge is None:
            edge = self.get_part(type="edge", sub_type="h", row=1, col=1)
        return edge


    def get_last_cmd(self):
        """ Get executed or redone
        """
        return self.command_manager.get_last_command()


    def get_undo_cmd(self):
        """ Get most recent undo cmd
        """
        return self.command_manager.get_undo_cmd()
    
    
    def is_in_cmd(self):
        """ Check if building a command
        """
        return self.select_cmd is not None
    
    
    def check_mod(self, part, mod_type=None, desc=None):
        """ Part modification notification
        Modifications are stored for later use/inspection in
        self.prev_mods for MOD_BEFORE
        self.new_mods for MOD_AFTER
        :part: part modified
        :mod_type: SelectPart.MOD_BEFORE, .MOD_AFTER
        :desc: description of modification e.g., turn_on
        """
        SlTrace.lg("check_mod: %s %s %d"
                    % (part, desc, mod_type), "execute")
        if mod_type == SelectPart.MOD_BEFORE:
            self.add_prev_mods(part)
        else:
            self.add_new_mods(part)

    def add_prev_mods(self, parts):
        """ Add part before any modifications
        :parts: part or list before modification
        """
        if not isinstance(parts, list):
            parts = [parts]
        for part in parts:
            self.prev_mods.append(select_copy(part))

    def add_new_mods(self, parts):
        """ Add parts before any modifications
        :parts: one or list before modification
        """
        if not isinstance(parts, list):
            parts = [parts]
        for part in parts:
            self.new_mods.append(select_copy(part))
        
        
    def clear_mods(self):
        """ Clear modifications
        """
        self.prev_mods = []
        self.new_mods = []


    def cmd_select(self, parts=None, keep=False, display=False):
        """ Select parts with given ids
        :parts: part/id or list of part/ids for parts to select
        :keep: keep currently selected if True default: False
        """
        self.flush_cmds()
        scmd = self.get_cmd("cmd_select", display=display)
        prev_selects = list(self.get_selects())
        scmd.add_prev_selects(prev_selects)
        if keep:
            scmd.add_new_selects(prev_selects)
        scmd.add_new_selects(parts)
        self.do_cmd()
        
        
        
    def cmd_select_clear(self, parts=None):
        """ Select part(s)
        :parts: part/id or list
                default: all selected
        """
        scmd = self.get_cmd()
        scmd.select_clear(parts)


    def cmd_select_set(self, parts, keep=False):
        """ Select part(s)
        :parts: part(s) to select/deselect
        :keep: keep previous selected
                default = falsu
        """
        scmd = self.get_cmd()
        scmd.select_set(parts, keep=keep)
        
        
    def select_clear(self, parts=None):
        """ Select part(s)
        :parts: part or list of parts
                default: all selected
        """
        self.board.area.select_clear(parts=parts)


    def select_set(self, parts=None, keep=False):
        """ Select part(s)
        :parts: part(s) to select/deselect
        """
        self.board.area.select_set(parts=parts, keep=keep)
        

    def set_new_player(self, player):
        scmd = self.select_cmd
        if scmd is None:
            raise SelectError("set_new_player with no SelectCommand")
        scmd.set_new_player(player)
            

    def set_prev_player(self, player):
        scmd = self.select_cmd
        if scmd is None:
            raise SelectError("set_prev_player with no SelectCommand")
        scmd.set_prev_player(player)
    
    
    def set_stroke_move(self, use_stroke=True):
        """ Enable/Disable use of stroke moves
        Generally for use in touch screens
        """
        self.board.set_stroke_move(use_stroke)
            
    
    def add_prev_parts(self, parts):
        scmd = self.select_cmd
        if scmd is None:
            raise SelectError("add_prev_parts with no SelectCommand")
        scmd.add_prev_parts(parts)
    
    
    def add_new_parts(self, parts):
        scmd = self.select_cmd
        if scmd is None:
            raise SelectError("add_new_parts with no SelectCommand")
        scmd.add_new_parts(parts)

    def undo_micro_move_command(self, new_value):
        self.undo_micro_move = new_value
        SlTrace.lg(f"selectPlay: New undo_micro_move: {new_value}")
        self.command_manager.undo_micro_move_command(new_value)


    def undo(self, undo_micro_move=None):
        """ Undo most recent command
        :undo_micro_move: undo micromove
                    default: command_manager.undo_micro_move
        :returns: True iff successful
        """
        while self.is_waiting_for_message():
            self.end_message()
            
        if self.ignore_if_busy():
            return False
        self.clear_highlighted()
        return self.command_manager.undo(undo_micro_move=undo_micro_move)


    def redo(self, undo_micro_move=None):
        """ Undo most recent command
        :undo_micro_move: undo micromove
                    default: command_manager.undo_micro_move
        :returns: True iff successful
        """
        while self.is_waiting_for_message():
            self.end_message()
            
        if self.ignore_if_busy():
            return False
        
        return self.command_manager.redo(undo_micro_move=undo_micro_move)
        
    
    
    def do_cmd(self):
        if self.select_cmd is None:
            raise SelectError("do_cmd with no SelectCommand")
        self.select_cmd.do_cmd()
        if self.after_move is not None:
            self.after_move(self.select_cmd)

        self.select_cmd = None      # Clear for next time
        self.mw.update_idletasks()
        self.mw.update()        
        
        
    def complete_cmd(self):
        """ Complete command if one in progress
        """
        if self.select_cmd is not None:
            self.do_cmd()


    def auto_play_pause(self):
        """ Pause for auto player
        Returns after delay
        """
        if ActiveCheck.not_active():
            return
        
        if not self.playing:
            return              # Suppress activity

        player = self.get_player()
        if not player.auto:
            return
        self.auto_delay_waiting = True
        pause = player.pause
        if self.speed_step >= 0:
            pause = self.speed_step
        delay_ms = int(pause*1000)
        self.mw.after(delay_ms)
        return


    def manual_play(self, player):
        """ Do manual play, checking for action
        :player: player to move
        :returns: return True iff a move was sensed, else False
        """
        if self.manual_moves:
            move = self.manual_moves.pop()
            self.new_edge(move)
            return True

        self.mw.update()        
        
        return False
            
    def auto_play(self, player):
        """ Do automatic move based on "level" of player
        """
        SlTrace.lg("auto_play player: %s" % self.get_player(), "player_trace")
        self.trace_scores("auto_play:")
        legal_moves = self.get_legal_moves()
        if legal_moves.number() == 0:
            self.end_game("No more moves!")
            return False
        SlTrace.lg("auto_play player: %s" % self.get_player(), "player_trace")
        
        level = self.adjust_level_to_stay_even(player)
        SlTrace.lg("auto_play player: %s" % self.get_player(), "player_trace")
        if level > 0:
            self.auto_play_positive(player)
        elif level < 0:
            self.auto_play_negative(player)
        else:
            self.auto_play_random(player)
        SlTrace.lg("auto_play player END: %s" % self.get_player(), "player_trace")
        return True                         # Next move number


    def adjust_level_to_stay_even(self, player):
        """ Adjust playing level to stay even, if steven != 0
        :player: current player - us
            player.steven:
                0 - no checking
                > 0 reverse level if you score is to high
                < 0 reverse level if you score is to low
                abs() < 1 use fraction as fraction advantage
                        e.g. stay_even==.1 if score > .1*opponent
                abs() >= 1 use stay_even as number advantage
                        e.g. stay_even==2 if score > 2 + opponent

        """
        SlTrace.lg("adjust_level_to_stay_even player: %s" % self.get_player(), "player_trace")
        level = player.level
        steven = player.steven
        if steven == 0:
            return level        # No adjustment wanted
        SlTrace.lg("adjust_level_to_stay_even player: %s" % self.get_player(), "player_trace")
       
        our_score = player.get_score()
        SlTrace.lg("adjust_level_to_stay_even player: %s" % self.get_player(), "player_trace")
        next_player = self.get_next_player(set_player=False)
        SlTrace.lg("adjust_level_to_stay_even player: %s" % self.get_player(), "player_trace")
        next_score = next_player.get_score()
        SlTrace.lg("adjust_level_to_stay_even player: %s" % self.get_player(), "player_trace")
        diff = abs(our_score - next_score)
        steven_abs = abs(steven)
        diff_limit = steven_abs
        if steven_abs < 1:
            diff_limit = steven_abs * (our_score+next_score)/2
        
        if diff > diff_limit:
            if our_score > next_score:
                level = -abs(level)     # reduce our level
            elif our_score < next_score:
                level = abs(level)
        SlTrace.lg("adjust_level_to_stay_even player: %s" % self.get_player(), "player_trace")
        return level


    def auto_play_positive(self, player):
        """ Positive player - trying to "win"
        """
        level = player.level
        LEVEL_SQUARE = 1                # Complete a square
        LEVEL_NO_GIVE_SQUARE = 2        # Provide possible square to next play
        legal_moves = self.get_legal_moves()
        if level >= LEVEL_SQUARE:
            square_moves = self.get_square_moves(legal_moves)
            if square_moves.number() > 0:
                next_move = square_moves.rand_obj()
                self.new_edge(next_move)
                SlTrace.lg("positive play move for %s: %s" % (player, next_move), "play_strategy")
                return

        if level >= LEVEL_NO_GIVE_SQUARE:
            safe_square_moves = self.get_square_distance_moves(min_dist=2, move_list=legal_moves)
            if safe_square_moves.number() > 0:
                next_move = safe_square_moves.rand_obj()
                self.new_edge(next_move)
                SlTrace.lg("positive play safe move for %s: %s" % (player, next_move), "play_strategy")
                return
                   
        self.auto_play_random(player)         # Default - just play one


    def auto_play_negative(self, player=None):
        """ Negative player - trying to "loose"
        """
        if player is None:
            player = self.get_player()

        level = player.level
        LEVEL_SQUARE = 1                # Complete a square
        LEVEL_NO_GIVE_SQUARE = 2        # Provide possible square to next play
        legal_moves = self.get_legal_moves()
        if abs(level) >= LEVEL_SQUARE:
            squares = []
            not_square_moves = []
            not_safe_moves = []     # give win to next player
            for move in legal_moves:
                if not self.is_square_complete(move, squares, ifadd=True):
                    not_square_moves.append(move)
                    if self.square_complete_distance(move) <= 2:
                        not_safe_moves.append(move)
            if abs(level) >= LEVEL_NO_GIVE_SQUARE:
                if len(not_safe_moves) > 0:
                    nr = random.randint(0, len(not_safe_moves)-1)
                    next_move = not_safe_moves[nr]
                    self.new_edge(next_move)
                    SlTrace.lg("negative play safe for %s: %s" % (player, next_move), "play_strategy")
                    return
                    
            if len(not_square_moves) > 0:
                nr = random.randint(0, len(not_square_moves)-1)
                next_move = not_square_moves[nr]
                self.new_edge(next_move)
                SlTrace.lg("negative play square for %s: %s" % (player, next_move), "play_strategy")
                return
            
            
            
        self.auto_play_random(player)
    

    def auto_play_random(self, player=None):
        """ Play the random next legal move
        """
        if player is None:
            player = self.get_player()
        legal_moves = self.get_legal_moves()
        next_move = legal_moves.rand_obj()
        self.new_edge(next_move)
        
        
    def get_legal_moves(self):
        return self.board.get_legal_moves()


    def get_num_legal_moves(self):
        return self.board.get_num_legal_moves()


    def get_square_moves(self, moves):
        """ Get, from moves, those which would complete a square
        :moves: move list default: all legal moves
        """
        return self.board.get_square_moves(moves)


    def get_square_distance_moves(self, min_dist=2, move_list=None):
        """ Get moves which provide a minimum distance to sqaree completion
        """
        return self.board.get_square_distance_moves(min_dist=min_dist, move_list=move_list)
    
    
    def start_move(self):
        """ Start move
        :returns: True iff move has been made, and next move is coming
        """
        if not self.run:
            return False
        

        if self.get_num_legal_moves() == 0:
            SlTrace.lg("NO more legal moves!", "nolegalmoves")
            ###return False       
        
        if self.new_move:
            self.announce_player("start_move")
            if SlTrace.trace("selected"):
                self.list_selected("After start_move")
            self.new_move = False
        player = self.get_player()
        if player.auto:
            self.auto_play_pause()
            if self.auto_play(player):
                return True
        else:
            if self.cmd_stream and not self.cmd_stream.is_eof():
                if self.stream_cmd_play(player=player):
                    return True
            else:    
                if self.manual_play(player):
                    return True
        
        return False        # No move -no new move


    def stream_cmd_play(self, player=None):
        """ Play next command from command stream
        :player: player for whom it is a move
        :returns: True if executed
        """
        stcmd = self.cmd_stream.get_cmd()
        if stcmd is None:
            return False
        
        res = self.cmd_stream_proc.do_stcmd(stcmd)
        return res


    def end_game(self, msg=None):
        """ End the game
        :msg: message /reason
        """
        self.ngame += 1
        self.game_end_ts = SlTrace.getTs(6)
        SlTrace.lg("end of game {:d}   {:.2f}".format(self.ngame,
                         SlTrace.ts_diff(ts1=self.game_start_ts, ts2=self.game_end_ts)))
        self.flush_cmds()
        self.score_game()
        scmd = self.get_cmd("end_of_game")
        if msg is None:
            self.add_message("End of Game", 1)
            
        self.add_message("Game Over")
        self.do_cmd()
        self.pause_cmd()
        self.running = False        # Stop this game
        if self.results_file is not None:
            self.results_file.end_game()
        ###if self.on_end is not None:
        ###    ###self.on_end()
        ###    self.mw.after(0, self.on_end)


    def save_properties(self):
        """ Save profile
        """
        SlTrace.save_propfile()
        

    def new_game(self, msg=None):
        """ Stop the game and start a new game - orderly but no stats/saving
        :msg: message /reason
        """
        if msg is None:
            msg = "new game"
        SlTrace.lg(msg)
        self.stop_game(msg)
        self.restart_game = True        # Signal to restart

    def stop_game(self, msg=None):
        """ Stop the game - orderly but no stats/saving
        :msg: message /reason
        """
        SlTrace.lg("stop game")
        self.flush_cmds()
        scmd = self.get_cmd("stop_game")
        if msg is None:
            self.add_message("Stop Game", 1)
        self.do_cmd()
        self.running = False
        self.game_stopped = True       # Stop (one time)

    def flush_cmds(self):
        """  
        Complete commands in progress
        """
        if self.select_cmd is not None:
            self.do_cmd()


    def game_control_updates(self):
        """ Facilitate immediate changes from game_control
        """
        if self.game_control is not None:
            self.speed_step = self.game_control.get_prop_val("running.speed_step", -1)


    def game_count_down(self, wait_time=5, inc=1, text="%.0f seconds till new game"):
        """ Count down with display
        :time: length of count down(seconds)
        :inc: time between display
        :text: text with %f time till end
        """
        temp_run = self.run     # Save for restore
        self.run = True         # enable cmd execution
        ###wait_time = 500
        tbegin = datetime.now()
        tgoing = 0
        while tgoing < wait_time:
            now = datetime.now()
            tgoing = (now - tbegin).total_seconds()
            tleft = wait_time-tgoing
            if tleft > 0:
                msg_text = text % tleft
                scmd = self.get_cmd("game_wait")
                self.add_message(msg_text)
                self.do_cmd()
        self.run = temp_run
        self.message_delete()
    
    def score_game(self):
        """ Score current game, updating statistics
        played: number of games played
        wins: number of games with top score (or tie)
        """
        players = self.player_control.get_players()
        game_control = self.game_control
        if game_control is not None:
            game_control.set_vals()         # Update any changed game control settings
        if len(players) == 0:
            return      # No players
        n_top_score = 0
        top_score = players[0].get_score()
        for player in players:
            if player.get_score() > top_score:
                top_score = player.get_score()
        for player in players:
            player_score = player.get_score()
            if player_score == top_score:
                n_top_score += 1
                        
        for player in players:
            player_score = player.get_score()
            player_played = player.get_played()
            player_ties = player.get_ties()
            player_wins = player.get_wins()
            new_played = player_played+1
            player.set_played(new_played)
            player.set_prop("played")
            if player_score == top_score:
                if n_top_score > 1:
                    new_ties = player_ties + 1
                    player.set_ties(new_ties)
                    player.set_prop("ties")
                else:
                    new_wins = player_wins + 1
                    player.set_wins(new_wins)
                    player.set_prop("wins")
        self.update_score_window()

            
    def start_game(self):
        self.in_game = True
        self.new_move = True
        self.manual_moves = []          # Initialize empty list
        self.player_control.set_all_scores(0, only_playing=True)
        SlTrace.lg("start_game", "execute")
        self.set_move_no(0)
        self.get_cmd("start_game", flush=True)
        if self.results_file is not None:
            nplaying = self.player_control.get_num_playing()
            self.results_file.start_game(game_name="dots",
                    nplayer=nplaying, nrow=self.board.nrows,
                    ncol=self.board.ncols)
            
        self.add_message("It's A New Game",
                         time_sec=1)
        ###self.set_move_no(1)
        self.do_cmd()
        self.set_move_no(1)


    def set_move_no(self, move_no):
        self.command_manager.set_move_no(move_no)


    def get_move_no(self):
        """ Get current move number
        """
        return self.command_manager.get_move_no()
        
        
    def next_move_no(self):
        self.new_move = True
        self.command_manager.next_move_no()
        
        

    def is_square_complete(self, edge, squares=None, ifadd=False):
        """ Determine if this edge completes a square(s)
        :edge: - potential completing edge
        :squares: list, to which any completed squares(regions) are added
                Default: no regions are added
        :returns: True iff one or more squares are completed
        """
        return self.board.is_square_complete(edge, squares=squares, ifadd=ifadd)


    def square_complete_distance(self, edge,
                                  squares_distances=None):
        """ Determine minimum number of moves, including this
        move to complete a square
        :edge: - potential completing edge
        :squares_distances: list, of (distance, square) pairs
                Default: no entries returned
                if no connected squares - empty list returned
        :returns: closest distance, NOT_CLOSE if no squares
        """
        return self.board.square_complete_distance(edge, squares_distances=squares_distances)


    def down_click(self, part, event=None):
        """ Process down_click
        :part: on which down click occured
        :returns: None - all events are considered processed here
        """
        self.clear_highlighted(display=False)       # Clear all, reset if appropriate
        if part.is_turned_on():
            return
        
        if part.is_edge():
            self.manual_moves.append(part)
            return
        
        return
    
    

    def new_edge(self, edge):
        """ Process new edge selection
                1. Adjust edge apperance appropriately
                2. Announced new edge creation by user
                3. Make command undo unit
        :edge: updated edge component
        """
        SlTrace.lg("new_edge player: %s" % self.get_player(), "player_trace")
        if not edge.connecteds:
            SlTrace.lg("new_edge id=%d no connecteds" % edge.part_id)
            return
        
        self.disable_moves()                    # Disable input till ready
        self.clear_redo()
        prev_player = self.get_player()
        self.trace_scores("new_edge:")
        SlTrace.lg("New edge %s by %s"
                    % (edge, prev_player), "new_edge")
        self.complete_cmd()                     # Complete current command if one
        prev_selects = self.get_selected_part()
        self.cmd_select(edge)
        scmd = self.get_cmd("new_edge", undo_unit=True)
        scmd.set_prev_player(prev_player)
        scmd.add_prev_selects(prev_selects)
        ###edge.highlight_clear()                  # So undo won't re-highlight
        scmd.add_prev_parts(edge)               # Save previous edge state 
        self.mark_edge(edge, prev_player, move_no=scmd.move_no)
        edge.highlight_clear()                  # unhighlight after move
        self.add_new_parts(edge)
        self.update_score(self.next_move_no(), prev_player, edge)
        self.do_cmd()                               # move complete
        if SlTrace.trace("selected"):
            self.list_selected("After new_edge")
        self.clear_mods()

        prev_player = self.get_player()
        next_player = prev_player                    # Change if appropriate
        regions = []
        if self.is_square_complete(edge, regions):
            self.update_results_score(edge, regions)
            self.completed_square(edge, regions)
            nsq = len(regions)
            if nsq == 1:
                plu = ""
            else:
                plu = "s" 
            SlTrace.lg("%d Dot%s Completed" % (nsq, plu), "square")
        else:
            next_player = self.get_next_player()      # Advance to next player
            SlTrace.lg("Next player: %s" % next_player, "player_trace")
        if SlTrace.trace("selected"):
            self.list_selected("After square check")
        if next_player != prev_player:
            scmd = self.get_cmd("new_player")
            scmd.set_new_player(next_player)
            self.do_cmd()
        if SlTrace.trace("selected"):
            self.list_selected("After next_player set")
        self.enable_moves()
        self.trace_scores("new_edge end:")
        SlTrace.lg("new_edge END player: %s" % self.get_player(), "player_trace")


    def clear_highlighted(self, parts=None, display=True):
        self.board.area.clear_highlighted(parts=parts, display=display)

    def clear_redo(self):
        """ Clear redo (i.e. undo_stack for possible redo)
        """
        self.command_manager.clear_redo()
        
        

    def player_control(self):
        """ Setup player control
        """
        self.board.player_control()

    def get_next_player(self, set_player=True):
        """ Get next player to move
        :set: True set this as the player
        """
        return self.player_control.get_next_player(set_player=set_player)
    
    def get_player(self):
        """ Get current player to move
        """
        return self.player_control.get_player()
    
    def get_player_num(self):
        """ Get current player to move's number 1,2 in order of play
        """
        return self.player_control.get_player_num()

        
    
    def get_players(self, all=False):
        """ Get players
        :all: all players default: just currently playing
        """
        return self.player_control.get_players(all=all)


    def get_prev_player(self):
        """ Get previous player, i.e. player of most recent move
        """
        prev_cmd = self.get_last_cmd()
        if prev_cmd is None:
            return None         # No previous player
        prev_player = prev_cmd.new_player
        return prev_player
    
    
    
    def set_player(self, player):
        self.player_control.set_player(player)
        
        
    
    def completed_square(self, edge, squares):
        player = self.get_player()
        player_name = player.name
        player_label = player.label
        if len(squares) == 1:
            text = ("%s completed a square with label %s"
                     % (player_name, player_label))
        else:
            text = ("%s completed %d squares with label %s"
                    % (player_name, len(squares), player_label))
        if SlTrace.trace("square"):
            SlTrace.lg(text)
        SlTrace.lg("completing edge: %s" % edge, "square")
        self.annotate_squares(squares, edge=edge, player=player)
        self.update_score_squares(player, squares=squares)
        self.trace_scores("after self.update_score")
        self.add_message(text, font_size=20, time_sec=1)
        text = ("%s gets another turn." % player_name)
        SlTrace.lg(text, "move")
        self.add_message(text, font_size=20, time_sec=1)
        SlTrace.lg("completed_square_end", "square")
        self.trace_scores("completed_square end")

    def trace_scores(self, prefix=None):
        """ Trace(log) playing scores
        :prefix: leading text to identify place
                default: none
        """
        if not SlTrace.trace("score"):
            return
        
        if prefix is None:
            prefix = "trace_scores"
        if not prefix.endswith(":"):
            prefix += ":"
        for player in self.get_players():
            SlTrace.lg("%sscore: %d for %s"
                        % (prefix, player.score, player), "score")


    def reset(self):
        """ Reset to new game settings
        """
        if self.board is not None:
            self.board.reset()
        

    def reset_score(self):
        """ Reset multigame scores/stats
        """
        SlTrace.lg("reset_score")
        for player in self.get_players():
            player.set_wins(0)
            player.set_played(0)
            player.set_ties(0)
        self.player_control.set_ctls()
        if self.display_game and self.score_window is not None:
            self.score_window.update_window()


    

    def select(self, ptype, row=None, col=None, keep=False):
        """ Select part
        :ptype: part type: "h" horizontal edge
                            "v" vertical edge
        :row: row in grid
        :col" column in grid
        :keep: Keep previously selected default: clear previously selected
        :returns: True iff successful
        """
        part = self.get_part(sub_type=ptype, row=row, col=col)
        if part is None:
            return False
        
        self.select_set(part)
        return True
             
    def set_score(self, score, player=None):
        """ Set player score
        :score: New score
        :player: player to update default: current player
        NOTE: There is a problem using player.set_score directly - update is lost
        """
        if player is None:
            player = self.get_player()
        plr = self.player_control.get_player(player.position)
        plr.set_score(score)
        
        
            
    def update_score_squares(self, player, squares):
        """ Update player's score based on squares completed
        Create and execute command
        :squares:  completed squares
        """
        scmd = self.get_cmd("update_score")
        if not isinstance(squares, list):
            squares = [squares]
        prev_score = player.get_score()
        new_score = prev_score + len(squares)
        SlTrace.lg("prev_score:%d new_score:%d %s" % (prev_score, new_score, player), "score")
        self.set_score(new_score, player=player)
        self.trace_scores("after set_score(%d, %s)" % (new_score, player))
        scmd.add_prev_score(player, prev_score)
        scmd.add_new_score(player, new_score)
        self.complete_cmd()
        self.update_score_window()


    def update_results_score(self, edge, regions):
        """ Update results for possible saving to results data base
        :edge: causing action - currently ignored
        :regions: square(s) completed
        """
        if self.results_file is None:
            return                      # No update
        
        pln = self.get_player_num()
        self.results_file.results_update(player_num=pln, nsquare=len(regions))
    
    
    def update_score_from_cmd(self, new_score, prev_score):
        """ Update score from command execution
        :new_score: player, score tupple if one
        :prev_score: previous player, score tupple - ignored
        """
        if new_score is None:
            return          # No change
        
        player = new_score[0]
        score = new_score[1]
        player.set_score(score)
            
                
    def remove_parts(self, parts):
        """ Remove deleted or changed parts
        :parts: parts to be removed
        """
        self.board.remove_parts(parts)
        self.set_changed(parts)
    
    def insert_parts(self, parts):
        """ Add new or changed parts
        :parts: parts to be env_added
        """
        self.board.insert_parts(parts)
        self.set_changed(parts)
            