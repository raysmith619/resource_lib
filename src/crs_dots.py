"""
Created on October 30, 2018

@author: Charles Raymond Smith
"""
import os
import sys
import time
import traceback
from tkinter import *    
import argparse
import cProfile, pstats, io         # profiling support
import objgraph

import  gc
import tracemalloc
###gc.set_debug(gc.DEBUG_LEAK)
snapshot1 = None
snapshot2 = None

mw = Tk()       # MUST preceed users of SelectControl for tkinter vars ...Var()
                # e.g. SelectPlay -> ScoreWindow -> SelectControl
from select_control import SelectControl
from select_part import SelectPart
from select_window import SelectWindow
from select_play import SelectPlay
from select_trace import SlTrace
###from select_region import SelectRegion
from select_dots import SelectDots
from sc_cmd_file_control import SelectCommandFileControl
from active_check import ActiveCheck
from sc_game_control import SelectGameControl
from sc_player_control import PlayerControl
from sc_score_window import ScoreWindow
from dots_game_file import DotsGameFile

history = "shadow_get_legal_moves"       # History of program
history += ", MoveList"                 # Use of MoveList object 
rF = None                   # Games Results file if any
loop_no = 0                 # Label loop number, starting at 1
sp = None
command_stream = None
game_control = None
def pgm_exit():
    ActiveCheck.clear_active()  # Disable activities
    if rF is not None:
        rF.end_file()
    quit()
    SlTrace.lg("Properties File: %s"% SlTrace.getPropPath())
    SlTrace.lg("Log File: %s"% SlTrace.getLogPath())
    sys.exit(0)

def play_exit():
    """ End playing
    Called from Window control
    """
    ActiveCheck.clear_active()  # Disable activities
    '''
    global sp
    SlTrace.lg("play_exit: Exiting from play")
    if sp is not None:
        sp.delete_window()
        
    SlTrace.lg("play_exit AFTER delete_window")
    sys.exit()
    '''
    pgm_exit()
    

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

###sys.setrecursionlimit(500)
cF = SelectControl(control_prefix="dots_control")       # Late comer for this pgm
cmd_file_name = None        # Command file, if one
###cmd_file_name = "3down.scrc"  # Command file, if one
src_lst = True                  # List source as run
stx_lst = True                # List Stream Trace cmd

loop = False        # Repeat game after end after waiting interval
loop_after = 5      # If looping, delay in seconds
min_xlen = 10       # Minimum xlen(pixels) and ylen
numgame = None        # if not None, Quit after numgames
nx = 5              # Number of x divisions
ny = nx             # Number of y divisions
playing = None      # If present comma separated list of playing (labels)
play_level = None   # If present comma separated list of playing levels
results_dir = None  # Results directory None -> default
results_files = True # True - produce results files
run_game = False	# Run game upon starting
show_id = False     # Display component id numbers
show_players = True # Display players info/control
show_score = True   # Display score / undo /redo
speed_step = -1     # Reduce all waits to this if 0 or greater - debugging, analysis
stroke_move = False # Support stroke move for touch screens
undo_micro_move = cF.make_val("undo_micro_move", False)   # Undo all steps, not just user moves
width = 600         # Window width
height = width      # Window height
board_change = True # True iff board needs redrawing




base_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
SlTrace.setLogName(base_name)
pgm_info = "%s %s\n" % (os.path.basename(sys.argv[0]), " ".join(sys.argv[1:]))
SlTrace.lg(pgm_info)
###SlTrace.setTraceFlag("get_next_val", 1)
""" Flags for setup """
btmove = 1.             #  Seconds between moves
display_game = True     # True - display game as played, else suppress display
profile_running = False # True - run cprofile over running_loop
ew_display = 7
ew_select = 7
ew_standoff = 8
trace = ""

run_resets = True      # Each program run resets scores
show_ties = False
undo_len=200           # Undo length (Note: includes message mcd

parser = argparse.ArgumentParser()

parser.add_argument('--btmove', type=float, dest='btmove', default=btmove)
parser.add_argument('--display_game', type=str2bool, dest='display_game', default=display_game)
parser.add_argument('--ew_display', type=int, dest='ew_display', default=ew_display)
parser.add_argument('--ew_select', type=int, dest='ew_select', default=ew_select)
parser.add_argument('--ew_standoff', type=int, dest='ew_standoff', default=ew_standoff)
parser.add_argument('-f', '--file', dest='cmd_file_name', default=cmd_file_name)
parser.add_argument('-r', '--run', action='store_true', dest='run_game', default=run_game,
                        help=("Run program upon loading"
                          " (default:%s" % run_game))
parser.add_argument('-l', '--src_lst', action='store_true', default=src_lst,
                    help=("List source as run"
                          " (default:%s" % src_lst))
parser.add_argument('-x', '--stx_lst', action='store_true', default=stx_lst,
                    help=("List commands expanded as run"
                          " (default:%s" % stx_lst))
parser.add_argument('--loop', type=str2bool, dest='loop', default=loop)
parser.add_argument('--loop_after', type=float, dest='loop_after', default=loop_after)
parser.add_argument('--min_xlen=', type=int, dest='min_xlen', default=min_xlen)
parser.add_argument('--numgame=', type=int, dest='numgame', default=numgame)
parser.add_argument('--nx=', type=int, dest='nx', default=nx)
parser.add_argument('--ny=', type=int, dest='ny', default=ny)
parser.add_argument('--play_level=', dest='play_level', default=play_level)
parser.add_argument('--playing=', dest='playing', default=playing)
parser.add_argument('--profile_running', type=str2bool, dest='profile_running', default=profile_running)
parser.add_argument('--results_files', type=str2bool, dest='results_files', default=results_files)
parser.add_argument('--results_dir', dest='results_dir', default=results_dir)
parser.add_argument('--run_game', type=str2bool, dest='run_game', default=run_game)
parser.add_argument('--show_id', type=str2bool, dest='show_id', default=show_id)
parser.add_argument('--show_players', type=str2bool, dest='show_players', default=show_players)
parser.add_argument('--show_score', type=str2bool, dest='show_score', default=show_score)
parser.add_argument('--speed_step', type=float, dest='speed_step', default=speed_step)
parser.add_argument('--stroke_move', type=str2bool, dest='stroke_move', default=stroke_move)
parser.add_argument('--trace', dest='trace', default=trace)
parser.add_argument('--undo_micro_move', type=str2bool, dest='undo_micro_move',
                                     default=undo_micro_move)
parser.add_argument('--undo_len', type=int, dest='undo_len', default=undo_len)
parser.add_argument('--width=', type=int, dest='width', default=width)
parser.add_argument('--height=', type=int, dest='height', default=height)
args = parser.parse_args()             # or die "Illegal options"
SlTrace.lg("args: {}\n".format(args))
SlTrace.lg("history: {}".format(history))
first_set_app = True        # Set False after first
btmove = args.btmove
cmd_file_name = args.cmd_file_name
display_game = args.display_game
loop = args.loop
loop_after = args.loop_after
min_xlen = args.min_xlen
numgame = args.numgame
nx = args.nx
ny = args.ny
nsq = nx * ny
play_level = args.play_level
playing = args.playing
profile_running = args.profile_running
results_dir = args.results_dir
results_files = args.results_files
run_game = args.run_game
show_id = args.show_id
show_players = args.show_players
show_score = args.show_score
speed_step = args.speed_step
src_lst = args.src_lst
stx_lst = args.stx_lst
stroke_move = args.stroke_move
undo_micro_move = args.undo_micro_move
trace = args.trace
if trace:
    SlTrace.setFlags(trace)
undo_len = args.undo_len
width = args.width
height = args.height
ew_display= args.ew_display
ew_select = args.ew_select
ew_standoff = args.ew_standoff

memory_trace = False    # Set true when tracing


SelectPart.set_edge_width_cls(ew_display,
                          ew_select,
                          ew_standoff)

def is_in_pgm_args(flag):
    """ Test if flag present in pgm args
    Looks for flag and -flag and --flag(=value)?
    :flag: flag string
    """
    arg_pat = re.compile(r'-{1,2}(\w+)(=?)(.*)')     # allow single "-" ??
    args = sys.argv[1:]
    idx = 0
    while idx < len(args):
        arg = args[idx]
        arg_match = re.match(arg_pat, arg)
        if not arg_match:
            idx += 1
            continue
        arg_flag = arg_match[1]
        if flag == arg_flag:
            return True         # Found flag
        
        eq_str = arg_match[2]
        if not eq_str:
            idx += 1         # form --flag value - skip value
        idx += 1            # go to next candidate
            
    return False


run_running = False
figure_new = True           # True - time to setup new figure
                            # for possible arrangement
n_arrange = 1               #number of major cycle for rearrange
sqs = None

move_no_label = None

def check_mod(part, mod_type=None, desc=None):
    global sp
    """ called before and after each part modificatiom
    """
    if sp is not None:
        sp.check_mod(part, mod_type=mod_type, desc=desc)
app = None                  # Application window ref
board_frame = None
msg_main_frame = None       # Message enclosing frame
msg_frame = None            # message enclosed frame
        
mw.lift()
mw.attributes("-topmost", True)

###@profile    
def setup_app(game_conrol):
    """ Setup / Resetup app window
    :returns: app reference
    """
    global app, first_set_app
    global mw, width, height
    global run_resets, min_xlen, nx, ny, loop, loop_after, show_ties 
    global speed_step
    global first_app_set
    global board_change
    
    if first_set_app:
        app = SelectWindow(mw,
                        title="crs_dots",
                        pgmExit=play_exit,
                        cmd_proc=True,
                        cmd_file=None,
                        arrange_selection=False,
                        game_control=game_control
                        )
        app.add_menu_command("NewGame", new_game)
        app.add_menu_command("Players", show_players_window)
        app.add_menu_command("Score", show_score_window)
        app.add_menu_command("CmdFile", cmd_file)
        app.add_menu_command("Run", run_cmd)
        app.add_menu_command("Pause", pause_cmd)
    
        if is_in_pgm_args("loop"):
            game_control.set_prop_val("running.loop", loop)
        else:
            loop = game_control.get_prop_val("running.loop", loop)
            
        if is_in_pgm_args("loop_after"):
            game_control.set_prop_val("running.loop_after", loop_after)
        else:
            loop_after = game_control.get_prop_val("running.loop_after", loop_after)
            
        if is_in_pgm_args("run_resets"):
            game_control.set_prop_val("scoring.run_resets", run_resets)
        else:
            run_resets = game_control.get_prop_val("scoring.run_resets", run_resets)
            
        if is_in_pgm_args("show_ties"):
            game_control.set_prop_val("scoring.show_ties", show_ties)
        else:
            show_ties = game_control.get_prop_val("scoring.show_ties", show_ties)
            
        if is_in_pgm_args("speed_step"):
            game_control.set_prop_val("running.speed_step", speed_step)
        else:
            speed_step = game_control.get_prop_val("running.speed_step", speed_step)
            
        if is_in_pgm_args("min_xlen"):
            game_control.set_prop_val("viewing.min_xlen", min_xlen)
        else:
            min_xlen = game_control.get_prop_val("viewing.min_xlen", min_xlen)
            
        if is_in_pgm_args("nx"):
            game_control.set_ctl("viewing.columns", nx)
        else:
            nx = game_control.get_prop_val("viewing.columns", nx)
            
        if is_in_pgm_args("ny"):
            game_control.set_ctl("viewing.rows", ny)
        else:
            ny = game_control.get_prop_val("viewing.rows", ny)

    loop = game_control.get_prop_val("running.loop", loop)
    loop_after = game_control.get_prop_val("running.loop_after", loop_after)
    speed_step = game_control.get_prop_val("running.speed_step", speed_step)
    run_resets = game_control.get_prop_val("scroring.run_resets", run_resets)
    show_ties = game_control.get_prop_val("scoring.show_ties", show_ties)
    min_xlen = game_control.get_prop_val("viewing.min_xlen", min_xlen)    
    nx = game_control.get_prop_val("viewing.columns", nx)    
    ny = game_control.get_prop_val("viewing.rows", ny)
            
    if not is_in_pgm_args("width"):        
        width = app.get_current_val("window_width", width)
        if width < 100:
            width = 100
    width = int(width)
    if not is_in_pgm_args("height"):
        height = app.get_current_val("window_height", height)
        if height < 100:
            height = 100
    height = int(height)
    
    if not is_in_pgm_args("nx"):
        nx = app.get_current_val("figure_columns", nx)
    if not is_in_pgm_args("ny"):
        ny = app.get_current_val("figure_rows", ny)
        

        
        
    return app


def before_move(scmd):
    global move_no_label
    
    SlTrace.lg("before_move", "move")
    if SlTrace.trace("selected"):
        sp.list_selected("before_move")

    
def after_move(scmd):
    SlTrace.lg("after_move", "move")
    if SlTrace.trace("selected"):
        sp.list_selected("selected after_move")
    
    
def undo():
    global move_no_label
    SlTrace.lg("undoButton")
    if sp is None:
        return False
    res = sp.undo()
    return res
            
    
def redo():
    SlTrace.lg("redoButton")
    if sp is None:
        return False
    else:
        res = sp.redo()
        return res


def end_game():
    if ActiveCheck.not_active():
        return  # We're at the end
    
    if numgame is not None and sp.ngame >= numgame:
        if sp.profile_running:
            sp.pr.disable()
            s = io.StringIO()
            sortby = 'cumulative'
            ps = pstats.Stats(sp.pr, stream=s).sort_stats(sortby)
            ps.print_stats()
            SlTrace.lg(s.getvalue())

        SlTrace.lg("end_game:  game={:d}".
                   format(sp.ngame))
        pl_str = "s" if numgame != 1 else ""
        SlTrace.lg("Ending program after {:d} game{}".format(numgame, pl_str))
        pgm_exit()
        
    if sp.restart_game:
        mw.after(0, new_game)
    elif loop and not sp.game_stopped:
        if loop_after > 0:
            SlTrace.lg("Restarting game after %.0f seconds" % loop_after)
            sp.game_count_down(wait_time=loop_after,inc=1)
        mw.after(0, new_game)
        ###new_game()

        
    
###@profile    
def set_dots_button():
    global loop_no
    global first_set_app
    global app
    global game_control
    global board_frame, msg_main_frame, msg_frame, sqs
    global width, height, min_xlen, nx, ny
    global n_rearrange_cycles, rearrange_cycle
    global players, sp
    global move_no_label
    global snapshot1, snapshot2         # tracemalloc instances
    global board_change
    global run_game
    
    loop_no += 1 
    SlTrace.lg("\nLoop %d" % loop_no)
    SlTrace.lg("Memory Used: %.0f MB, Change: %.2f MB"
                % (SlTrace.getMemory()/1.e6, SlTrace.getMemoryChange()/1.e6))
    SlTrace.lg("Dots Set Button", "button")

    if SlTrace.trace("pgm_stack"):
        stack = traceback.extract_stack()
        SlTrace.lg("pgm_stack depth=%d" % len(stack))
        if SlTrace.trace("pgm_stack_list"):
            list_len = 14
            print_list = traceback.format_list(stack)
            for line in print_list[-list_len:]:
                SlTrace.lg("  " + line)
    if game_control is None:
        game_control = SelectGameControl()    
    app = setup_app(game_control)
    
    app.update_form()
        
        
        
    min_xlen = app.get_component_val("figure_size", "min", min_xlen)
    min_xlen = float(min_xlen)
    min_xlen = str(min_xlen)
    min_ylen = min_xlen
    
    ###rects.append(rect1)
    ###rects.append(rect2)
    xmin = .1*float(width)
    xmax = .9*float(width)
    xlen = (xmax-xmin)/float(nx)
    min_xlen = float(min_xlen)
    if xlen < min_xlen:
        SlTrace.lg("nx=%d xlen(%.0f) set to %.0f" % (nx, xlen, min_xlen))
        xlen = min_xlen
    ymin = .1*float(height)
    ymax = .9*float(height)
    ylen = (ymax-ymin)/float(ny)
    min_ylen = float(min_ylen)
    if ylen < min_ylen:
        SlTrace.lg("ny=%d ylen(%.0f) set to %.0f" % (ny, ylen, min_ylen))
        ylen = min_ylen

    if board_change:
        if board_frame is not None:    
            board_frame.destroy()
            board_frame = None
        if msg_main_frame is not None:    
            msg_main_frame.destroy()
            msg_main_frame = None
        if sqs is not None:
            sqs.destroy()
            sqs = None
        if sp is not None:
            sp.destroy()
            sp = None
        board_frame = Frame(mw, width=width, height=height, bg="", colormap="new")
        board_frame.pack(side="top", fill=NONE, expand=YES)
        msg_main_frame = Frame(mw)
        msg_main_frame.pack(side="bottom", expand=YES, fill=BOTH)
        msg_frame = Frame(msg_main_frame)
        msg_frame.pack(side="bottom", expand=YES, fill=BOTH)
        board_change = False
    if sqs is None:
        sqs = SelectDots(board_frame, mw=mw,
                        display_game=display_game,
                        nrows=ny, ncols=nx,
                        width=width, height=height,
                        check_mod=check_mod)
        sqs.display()
            
    if sp is None:
        if command_stream is not None:
            command_stream.reset()      # Reset stream
        sp = SelectPlay(board=sqs, msg_frame=msg_frame,
                        display_game=display_game,
                        results_file=rF,
                        mw=mw, start_run=False,
                        numgame=numgame,
                        game_control=game_control,
                        cmd_stream=command_stream,
                        player_control=player_control,
                        profile_running=profile_running,
                        on_exit=pgm_exit,
                        on_end=end_game,
                        move_first=1, before_move=before_move,
                        after_move=after_move,
                        show_ties=show_ties,
                        undo_micro_move=undo_micro_move,
                        undo_len=undo_len)
        if command_stream is not None:
            command_stream.set_play_control(sp)
            command_stream.set_cmd_stream_proc(sp.cmd_stream_proc)
        
        player_control.set_play_control(sp)
        score_window.set_play_control(sp)
    sp.set_stroke_move(stroke_move)
    if first_set_app:
        if run_resets:
            sp.reset_score()
    if show_players:
        show_players_window()
    player_control.set_all_scores(0)
    ###if show_score:
    ###    show_score_window()
    first_set_app = False    
    if SlTrace.trace("memory"):
        ###obj_list = objgraph.show_most_common_types(limit=20)
        ###SlTrace.lg("objgraph=%s" % obj_list)    
        global memory_trace
        if not memory_trace:
            tracemalloc.Filter(True, "select*")
            tracemalloc.start()
            tracemalloc.Filter(True, "select*")
            memory_trace = True
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno', True)
        SlTrace.lg("[ Top 25 ]")
        for stat in top_stats[:25]:
            SlTrace.lg(str(stat))

        nc = gc.collect()
        SlTrace.lg("gc.collect=%d" % nc)
        nc = gc.collect()
        SlTrace.lg("gc.collect=%d" % nc)
        
        ###obj_list = objgraph.show_most_common_types(limit=20)
        ###SlTrace.lg("objgraph=%s" % obj_list)    
        objgraph.show_growth(limit=20, file=SlTrace.getLogFile())
        objgraph.show_growth(limit=20)
        objgraph.get_new_ids(file=SlTrace.getLogFile())
        objgraph.get_new_ids()
        ###obj = objgraph.by_type('SelectPlayer')
        ###objgraph.show_backrefs([obj], max_depth=10)
        SlTrace.lg("gc.garbage:%s" % gc.garbage)
        if snapshot1 is None and snapshot2 is None:
            snapshot1 = tracemalloc.take_snapshot()
        elif snapshot2 is None:
            snapshot2 = tracemalloc.take_snapshot()
        else:
            snapshot1 = snapshot2
            snapshot2 = tracemalloc.take_snapshot()
            
        if snapshot2 is not None:        
            top_stats = snapshot2.compare_to(snapshot1, 'lineno', True)
            SlTrace.lg("[ Top 25 differences]")
            for stat in top_stats[:25]:
                SlTrace.lg(str(stat))
            snapshot1 = snapshot2
            snapshot2 = None
        """
        Setup for next game
        """
    sp.reset()
    if run_game:
        run_game = False            # Clear after running
        mw.after(0, sp.running_loop)

        
def show_score_window():
    """ Setup score /undo/redo window
    """
    global sp
    if sp is not None:
        sp.show_score_window()

    
def vs(val):
    if type(val) == str:
        return val
    
    return str(val)

def new_edge(edge):
    """ Top level processing of new edge (line
    :edge: added edge
    """
    SlTrace.lg("We have added an edge (%s)" % (edge), "new_edge")
    ###sp.cmd_save(SelectCmd("new_edge", part=edge, player=sp.get_player()))
    sp.new_edge(edge)


def new_board():
    """ Reset board
    """
    global board_change
    SlTrace.lg("Reset board")
    if sqs is not None:
        sqs.setup_area()


def show_players_window():
    """ View/Change players
    """
    SlTrace.lg("PlayerControl")
    sp.player_control.control_display()


def cmd_file():
    """ Setup command file processing
    """
    SelectCommandFileControl(title="Command File", src_file=cmd_file_name,
                     cmd_execute=sp.user_cmd)    


def run_cmd():
    """ Run / continue game
	"""
    global sp
    global run_game
    run_game = True
    if sp is not None:
        sp.run_cmd()
        mw.after(0, sp.running_loop)   # One call from mainloop
    
def new_game():
    """ Start new game
    """
    SlTrace.lg("Starting New Game")
    if sp is not None:
        sp.reset()
        run_cmd()
        ###mw.after(0, sp.running_loop)   # One call from mainloop
    

def run_cmd_file(src_file=None):
    if sp is not None and command_stream is not None:
        command_stream.run_file(src_file=src_file, cmd_execute=sp.play_stream_command)


def pause_cmd():
    """ Pause game
	"""
    global sp
    if sp is not None:
        sp.pause_cmd()

if results_files:
    rF = DotsGameFile(file_dir=results_dir, history=history, pgm_info=pgm_info)
    SlTrace.lg("Game Results File %s" % rF.file_path)
    
if cmd_file_name is not None:
    command_stream = SelectCommandFileControl(src_file=cmd_file_name,
                                 run_cmd=run_cmd_file, new_board=new_board,
                                 src_lst=src_lst, stx_lst=stx_lst)

player_control = PlayerControl(title="Player Control", display=True)
if play_level is not None:
    player_control.set_play_level(play_level)
if playing is not None:
    player_control.set_playing(playing)
game_control = SelectGameControl(title="Game Control", display=True)

def undo_micro_move_command(new_value):
    global undo_micro_move
    
    undo_micro_move = cF.set_val("undo_micro_move", new_value)
    SlTrace.lg(f"New undo_micro_move: {undo_micro_move}")
    if sp is not None:
        sp.undo_micro_move_command(undo_micro_move)
    
score_window = ScoreWindow(title="Score", player_control=player_control,
                           undo_micro_move=undo_micro_move,
                           undo_micro_move_command=undo_micro_move_command,
                           display=True)   
set_dots_button()

mainloop()
SlTrace.lg("After mainloop()")