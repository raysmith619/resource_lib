# dots_game_load.py
"""
Support for the loading of dots game results
See dots_game_file.py for game and file layout
    
    File Format (Customized to be a small subset of python
                to ease processing flexibility)
     """
import sys, traceback
import re
import os
from pathlib import Path
from datetime import date

from select_trace import SlTrace
from select_error import SelectError
from dots_results_commands import history,pgm_info,version,game,moves,results,SkipFile

class DotsGame:

    def __init__(self, name=None,
                 game_no=0, time=0.,
                 nplayer=2, nrow=None, ncol=None, nmove=None, ts=None):
        self.name = name
        self.game_no = game_no
        self.time = time
        self.nplayer = nplayer
        self.nrow = nrow
        self.ncol = ncol
        self.nmove = nmove
        self.ts = ts
        self.game_moves = []
        self.results = []
        self.games = []
        
class DotsGameLoad:
    """ The hook from commands expressed via python command files to 
    the frame worker
    Make it an "ALL CLASS" to ease access via file based calls
    """
    
        
    def __init__(self, file_dir=None, file_prefix="dotsgame",
                 nrow=None,
                 ncol=None,
                 max_file_size=7e6,     # Files bigger will be split
                 file_ext="gmres",
                 test_file=None):
        """ Setup games file output
        :commands: command processor
        :file_dir: file directory default=..\gmres
        :ncol: if present, restrict games to ncol default: load all
        :nrow: if present, restrict games to nrow default: ncol
                Assume, for restriction, all games in file are the same nrow,ncol
        :max_file_size: Maximum file size, bigger files will be split
                    File text before first "game" line will be prepended to each
        :file_prefix: file prefix default: dotsgame
        :file_ext: file extension default: gmres
        :test_file: if present, just load this file
        """
        self.max_file_size = max_file_size
        if file_dir is None:
            file_dir = r"..\gmres"
        if nrow is not None or ncol is not None:
            if nrow is None:        # If only is present set the other to same
                nrow = ncol
            if ncol is None:
                ncol = nrow
        self.nrow = nrow
        self.ncol = ncol
            
        self.file_dir = file_dir
        self.file_prefix = file_prefix 
        self.file_ext = file_ext
        self.test_file = test_file
        self.nfile = 0
        self.games = []
        self.loader = None
        self.history_str = None
        self.pgm_info_str = None
    
    def load_game_file(self, file_name=None):
        """ load game results
        :file_name: path to file
        """
        self.fgames = []
        self.skip_file = False      # True if skipping rest of file
        self.cur_gm = None
        self.nfgame = 0         # Number of games in file
        self.ts1 = None         # Timestamp for first game
        self.tsend = None       # timestamp for last game
        file_size = os.path.getsize(file_name)
        if file_size > self.max_file_size:
            SlTrace.lg("%s must be split (%d bytes)"% (file_name, file_size))
            res = self.split_load_game_file(file_name=file_name)
        else:
            res = self.procFilePyPlus(file_name=file_name)
        if res:
            self.nfile += 1  # Count if successful
        else:
            self.nfile_error += 1
        if self.history_str is not None:
            SlTrace.lg("\npgm history {}".format(self.history_str))
        if self.pgm_info_str is not None:
            SlTrace.lg("run_info {}".format(self.pgm_info_str))
        
        sum_str = " - skipped"
        if self.cur_gm is not None:
            nsq_pgm = self.cur_gm.nrow * self.cur_gm.ncol
            tmin = tmax = self.fgames[0].time
            ttot = 0.
            for gm in self.fgames:
                ttot += gm.time
                if gm.time < tmin:
                    tmin = gm.time
                if gm.time > tmax:
                    tmax = gm.time
            tavg = ttot/len(self.fgames)
            tsqavg = tavg/nsq_pgm
            sum_str = ("     ngame=%d nrow=%d ncol=%d gmavg=%.3f sec (min=%.3f max=%.3f) sqavg=%.3f sec"
                % (self.nfgame, self.cur_gm.nrow, self.cur_gm.ncol, tavg, tmin, tmax, tsqavg))
        SlTrace.lg("    file %s%s" % (file_name, sum_str))
    
    
    def split_load_game_file(self, file_name=None):
        """ load game results, splitting file into self.max_file_size parts,
        placing prefix of portion from beginning to before first "game" line
        :file_name: path to file
        """
        preamble = ""
        with open(file_name) as fin:
            while True:
                line = fin.readline()
                if not line.endswith("\n"):
                    SlTrace.lg("{} Premature EOF"
                               .format(file_name))
                    return False
                if line.startswith("game("):
                    break
                preamble += line
            npart = 0           # Count split parts
            more_base_file = True
            while more_base_file:         # Process splits
                compile_str = preamble
                if line is not None:
                    compile_str += line
                    line = None
                while True:
                    line = fin.readline()
                    if not line.endswith("\n"):
                        more_base_file = False               # EOF
                        break
                    if line.startswith("game("):
                        if len(compile_str) > self.max_file_size:
                            break
                    compile_str += line
                tmp_file = r"..\dots_tmp_load_file.py"
                with open(tmp_file, "w") as ftout:
                    print(compile_str, file=ftout)

                if self.procFilePyPlus(file_name=tmp_file):
                    npart += 1      # Count parts
                else:
                    SlTrace.lg("split failed")
                    return False
                compile_str += line     # Add in first game line        

        SlTrace.lg("End loading split file {} {:d} parts "
                   .format(file_name, npart))
        return True    
        
    
    def load_game_files(self, file_pat=None):
        """ Load games
        :file_pat:  Additional filter (rex) pattern default: All
        """
        self.games = []
        self.nfile = 0  # Number of files loaded
        self.nfile_error = 0  # Number of file errors
        self.ngame = 0  # Number of games loaded
        self.ngame_error = 0  # Number pf game errors

        if self.test_file is not None:
            SlTrace.lg("Loading only test file: %s" % self.test_file)
            self.load_game_file(file_name=self.test_file) 
            SlTrace.lg("End loading %d files" % self.nfile)
            return
        
        SlTrace.lg("Files loaded from directory: {}".format(self.file_dir))
        for root, _, files in os.walk(self.file_dir):
            for file in files:
                if file_pat is not None and not re.match(file_pat, file):
                    continue
                file_name = os.path.join(root, file)
                self.load_game_file(file_name=file_name) 
        SlTrace.lg("End loading %d files" % self.nfile)
    
    
    
    def get_num_files(self):
        """ Get number of results files loaded
        """
        return self.nfile
        
           
    
    def get_num_games(self):
        """ Get number of games loaded
        """
        return len(self.games)
    
    """
    Process command file 
    """

    
    def procFilePyPlus(self, file_name=None, prefix=None):
        """ Process python code file, with prefix text
        :inFile: input file name
        :prefix: optional string to prefix file for compile
        """
        if not os.path.isabs(file_name):
            file_name = os.path.abspath(os.path.join(self.file_dir, file_name))
        path = Path(file_name)
        if not path.is_file():
            SlTrace.lg("file_name {} was not found".format(file_name))
            return False
        compile_str = ""
        if prefix is not None:
            compile_str = prefix
            if not prefix.endswith("\n"):
                compile_str += "\n"         # Insure ending newline

        try:
            fin = open(file_name)
            compile_str += fin.read()
            fin.close()
        except Exception as ex:
            SlTrace.lg("input file %s failed %s" % (file_name, str(ex)))
            return False
                
        try:
            exec(compile_str)
        except SkipFile as e:
            SlTrace.lg("    Skipping file", "SkipFile")
            return True
        
        except Exception as e:
            _, _, tb = sys.exc_info()
            tbs = traceback.extract_tb(tb)
            SlTrace.lg("Error while executing text from %s\n    %s)"
                    % (file_name, str(e)))
            inner_cmds = False
            for tbfr in tbs:  # skip bottom (in dots_commands.py)
                tbfmt = 'File "%s", line %d, in %s' % (tbfr.filename, tbfr.lineno, tbfr.name)
                if not inner_cmds and tbfr.filename.endswith("dots_commands.py"):
                    inner_cmds = True
                    SlTrace.lg("    --------------------")  # show bottom (in dots_commands.py)
                SlTrace.lg("    %s\n       %s" % (tbfmt, tbfr.line))
            return False
        return True


        
                
    """
    Basic game file loading functions
    Generally one per file command
    """
    
    
    def version(self, version_str):
        if self.loader is not None:
            return self.loader.version(version_str)
            
        self.version_str = version_str
    
    
    def history(self, history_str):
        if self.loader is not None:
            return self.loader.history(history_str)
            
        self.history_str = history_str
    
    
    def pgm_info(self, info_str):
        if self.loader is not None:
            return self.loader.pgm_info(info_str)
            
        self.pgm_info_str = info_str
        
    
    def game(self, name=None, game_no=0, time=0, nplayer=2,
                nrow=None, ncol=None, nmove=None, ts=None):
        """ Start processing of game
        :returns:  False if not processing this game
        """
        if self.loader is not None:
            return self.loader.game(name=name, game_no=0, time=0, nplayer=nplayer,
                nrow=nrow, ncol=ncol, nmove=nmove, ts=ts)

        if self.skip_file:
            return False
        
        
        if self.nrow is not None:
            if nrow != self.nrow:
                self.skip_file = True   # Optimize
                raise SkipFile("skipping file")

        if self.ncol is not None:
            if ncol != self.ncol:
                self.skip_file = True   # Optimize
                raise SkipFile("skipping file")
                        
        SlTrace.lg("game(name=%s, game_no=%d, time=%.3f, nplayer=%d, nrow=%d, ncol=%d, nmoves=%d, ts=%s)"
                % (name, game_no, time, nplayer, nrow, ncol, nmove, ts), "game")
        gm = DotsGame(name=name, game_no=game_no, time=time, nplayer=nplayer, nrow=nrow, ncol=ncol, nmove=nmove, ts=ts)
        self.cur_gm = gm         # Current game
        self.nfgame += 1        # Count game
        if self.nfgame == 1:
            self.ts1 = ts
        self.tsend = ts         # last (most recent
        return True
    
    def moves(self, *moves):
        """ Add next set of moves, game or part of game
        :moves: argument list
            Each argument is either:
                a move tuple (original format) (player number, row(1,..., col(1...)
                OR
                a list of  move  tuples, supporting larger (than 255) moves
        """
        if self.loader is not None:
            return self.loader.moves(*moves)


        if self.skip_file:
            return False

        for move in moves:
            if isinstance(move, tuple):
                self.cur_gm.game_moves.append(move) # List of tuples
            elif isinstance(move, list):
                self.cur_gm.game_moves.extend(move) # One move tuple
                SlTrace.lg("Adding list of %d moves" % len(move), "adding_list")
                
                
    def results(self, *res):
        """ End current game's input, specifying results
        :res: comma separated list of result tuples (player_no, nsquares)
        """
        if self.loader is not None:
            return self.loader.results(*res)
        

        if self.skip_file:
            return False

        self.cur_gm.results = res
        gm = self.cur_gm
        self.games.append(gm)            # Add to loaded games
        self.fgames.append(gm)            # Add to file's count
        if SlTrace.trace("game_results"):
            move_no = 0
            for move in gm.game_moves:
                move_no += 1
                SlTrace.lg("%3d: move(player=%d, row=%d, col=%d)" % 
                            (move_no, move[0], move[1], move[2]))
            results_str = "results: "
            for result in gm.results:
                results_str += (" player=%d: squares=%d" % 
                            (result[0], result[1]))
            SlTrace.lg(results_str)




if __name__ == "__main__":
    from dots_results_commands import DotsResultsCommands
    file_dir = r"..\test_gmres"
    test_file = None
    do_test_gmres = False
    do_test_file = False
    do_test_err1_file = True
    
    if do_test_err1_file:
        test_file = r"..\dots_load_file_err1.gmres"
        rC = DotsResultsCommands()
        rF = DotsGameLoad(file_dir=file_dir, test_file=test_file)
        rC.set_loader(rF)
        rF.load_game_files()
        SlTrace.lg("%d games in %d files" % (rF.get_num_games(), rF.get_num_files()))
    
    if do_test_file:
        max_file_size = 15000
        file_dir = r"..\gmres"
        test_file = r".\t2.gmres"
        rC = DotsResultsCommands()
        rF = DotsGameLoad(file_dir=file_dir, test_file=test_file,
                          max_file_size=max_file_size)
        rC.set_loader(rF)
        rF.load_game_files()
        SlTrace.lg("%d games in %d files" % (rF.get_num_games(), rF.get_num_files()))
        
    if do_test_gmres:
        file_dir = r"..\test_gmres"
        rC = DotsResultsCommands()
        rF = DotsGameLoad(file_dir=file_dir, test_file=test_file)
        rC.set_loader(rF)
        rF.load_game_files()
        SlTrace.lg("%d games in %d files" % (rF.get_num_games(), rF.get_num_files()))
            
