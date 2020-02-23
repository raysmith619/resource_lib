# crs_dots_load.py
"""
@author: Charles Raymond Smith
"""
import os
import sys
import time
import traceback
from tkinter import *    
import argparse

from select_trace import SlTrace

from dots_game_load import DotsGameLoad
from dots_results_commands import DotsResultsCommands

rF = None               # Games Results file if any
def pgm_exit():
    quit()
    SlTrace.lg("Properties File: %s"% SlTrace.getPropPath())
    SlTrace.lg("Log File: %s"% SlTrace.getLogPath())
    sys.exit(0)

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

###sys.setrecursionlimit(500)
cmd_file_name = None        # Command file, if one
###cmd_file_name = "3down.scrc"  # Command file, if one
src_lst = True                  # List source as run
stx_lst = True                # List Stream Trace cmd

ncol = None             # Restrict games to ncol columns
nrow = ncol             # Restrict games to nrow rows
results_dir = None  # Results directory None -> default
###results_dir = r"..\test_gmres"      # Test directory
results_files = True # True - produce results files




base_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
SlTrace.setLogName(base_name)
SlTrace.lg("%s %s\n" % (os.path.basename(sys.argv[0]), " ".join(sys.argv[1:])))
###SlTrace.setTraceFlag("get_next_val", 1)
""" Flags for setup """
trace = ""
test_file = None        # If present - use as single test file to load
show_ties = False
parser = argparse.ArgumentParser()

parser.add_argument('--ncol=', type=int, dest='ncol', default=ncol)
parser.add_argument('--nrow=', type=int, dest='nrow', default=nrow)
parser.add_argument('--results_files', type=str2bool, dest='results_files', default=results_files)
parser.add_argument('--results_dir', dest='results_dir', default=results_dir)
parser.add_argument('--test_file', dest='test_file', default=test_file)
parser.add_argument('--trace', dest='trace', default=trace)
args = parser.parse_args()             # or die "Illegal options"
SlTrace.lg("args: %s\n" % args)
ncol = args.ncol
nrow = args.nrow
results_dir = args.results_dir
results_files = args.results_files
trace = args.trace
if trace:
    SlTrace.setFlags(trace)
test_file = args.test_file

rF = None               # Set below

class PlayerStat:
    """ statistics for type of game
    """
    def __init__(self):
        self.nwin = 0
        self.nloss = 0
        self.ntie = 0
        self.nwin_square = 0        # Total number of squares in wins
        self.nloss_square = 0       # Total number of squares in losses
        self.ntie_square = 0        # Total number of squares in ties
        
class GameStat:
    """ Statistics entry for type of game under consideration
    """
    def __init__(self, nrow=None, ncol=None, nplayer=2):
        self.nrow = nrow
        self.ncol = ncol
        self.nplayer = nplayer
        self.count = 0
        self.stats = []
        for _ in range(nplayer):
            self.stats.append(PlayerStat())
        
game_stat_by_rows = {}       # by row number

def get_stat(nrow=None, ncol=None):
    """ Get stat for nrow, ncol, creating new stat if none
    :nrow: nrow selection
    :ncol: ncol selection
    """
    if nrow in game_stat_by_rows:
        gs_bcol = game_stat_by_rows[nrow]
    else:
        gs_bcol = game_stat_by_rows[nrow] = {}
    if ncol in gs_bcol:
        gm_stat = gs_bcol[ncol]
    else:
        gm_stat = gs_bcol[ncol] = GameStat(nrow=nrow, ncol=ncol)
    return gm_stat




rC = DotsResultsCommands()
rF = DotsGameLoad(file_dir=results_dir, test_file=test_file, nrow=nrow, ncol=ncol)
rC.set_loader(rF)
rF.load_game_files()
SlTrace.lg("%d games in %d files" % (rF.get_num_games(), rF.get_num_files()))        

     
for gm in rF.games:
    nrow = gm.nrow
    ncol = gm.ncol
    gm_stat = get_stat(nrow=nrow, ncol=ncol)
    gm_stat.count += 1
    for res in gm.results:
        pn = res[0]
        pn_nsquare = res[1]
        if pn == 1:
            pn1 = pn
            pn1_nsquare = pn_nsquare
        elif pn == 2:
            pn2 = pn
            pn2_nsquare = pn_nsquare
        else:
            SlTrace("Results for other than 2 planers: %d - ignored" % pn)
        continue

    for res in gm.results:
        pn = res[0]
        pl_stat = gm_stat.stats[pn-1]
        if pn == 1:
            pn_nsquare = pn1_nsquare
            pon_nsquare = pn2_nsquare
        elif pn == 2:
            pn_nsquare = pn2_nsquare
            pon_nsquare = pn1_nsquare
        else:
            SlTrace("Results for other than 2 planers: %d - ignored" % pn)
            continue
        win = pn_nsquare > pon_nsquare
        tie = pn_nsquare == pon_nsquare
        loss = pn_nsquare < pon_nsquare
        if win:
            pl_stat.nwin += 1
            pl_stat.nwin_square += pn_nsquare
        if tie:
            pl_stat.ntie += 1
            pl_stat.ntie_square += pn_nsquare
        if loss:
            pl_stat.nloss += 1
            pl_stat.nloss_square += pn_nsquare
            

        
SlTrace.lg(" Game Statistics by number of rows, cols") 
SlTrace.lg("%4s %4s %s" % ("rows", "cols", "Games"))   
for gsrow in sorted(game_stat_by_rows):
    stat_by_cols = game_stat_by_rows[gsrow]
    for gscol in stat_by_cols:
        gm_stat = get_stat(nrow=gsrow, ncol=gscol)
        ngame = gm_stat.count
        SlTrace.lg("%4d %4d %5d" % (gsrow, gscol, ngame))


SlTrace.lg(" Detailed Game Statistics by number of rows, cols") 
fmt_str = 3 * "{:4s}({:4s}) [({:4s})]  "
stat_str = fmt_str.format(" win","%","%sqs",  "loss","%","%sqs",  "tie","%","%sqs")
SlTrace.lg("%4s %4s %5s  %2s  %s" % ("rows", "cols", "games", "pl", stat_str))   
for gsrow in sorted(game_stat_by_rows):
    stat_by_cols = game_stat_by_rows[gsrow]
    for gscol in stat_by_cols:
        gm_stat = get_stat(nrow=gsrow, ncol=gscol)
        ngame = gm_stat.count
        gm_sq = gsrow*gscol
        for pl in range(1,len(gm_stat.stats)+1):
            pl_stat = gm_stat.stats[pl-1]
            pl_pct_win = 0. if gm_stat.count == 0 else 100.*pl_stat.nwin/gm_stat.count 
            pl_pct_loss = 0. if gm_stat.count == 0 else 100.*pl_stat.nloss/gm_stat.count 
            pl_pct_tie = 0. if gm_stat.count == 0 else 100.*pl_stat.ntie/gm_stat.count 
            pl_tot_win_gm_sq = pl_stat.nwin * gm_sq
            pl_pct_win_sq = 0. if pl_tot_win_gm_sq == 0 else 100.*pl_stat.nwin_square/pl_tot_win_gm_sq 
            pl_tot_loss_gm_sq = pl_stat.nloss * gm_sq
            pl_pct_loss_sq = 0. if pl_tot_loss_gm_sq == 0 else 100.*pl_stat.nloss_square/pl_tot_loss_gm_sq 
            pl_tot_tie_gm_sq = pl_stat.ntie * gm_sq
            pl_pct_tie_sq = 0. if pl_tot_tie_gm_sq == 0 else 100.*pl_stat.ntie_square/pl_tot_tie_gm_sq 
            fmt_str = 3 * " {:4d}({:4.1f}) [({:4.1f})]"
            stat_str = fmt_str.format(pl_stat.nwin, pl_pct_win, pl_pct_win_sq,
                           pl_stat.nloss, pl_pct_loss, pl_pct_loss_sq,
                           pl_stat.ntie, pl_pct_tie, pl_pct_tie_sq)
            SlTrace.lg("%4d %4d %5d  %2d %s" % (gsrow, gscol, ngame, pl, stat_str))
        SlTrace.lg(70*"-")