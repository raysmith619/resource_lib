# dots_game_file.py
"""
Support for the saving and loading of dots game results
    Columns ==>                        Rows--+
    1    2    3    4    5    6               :
    +----+----+----+----+----+          1    V

    +----+----+----+----+----+          2

    +----+----+----+----+----+          3

    +----+----+----+----+----+          4

    +----+----+----+----+----+          5
    
    +----+----+----+----+----+          6
    
    
    File Format (Customized to be a small subset of python
                to ease processing flexibility)
    # file_name
    # date
    
    game(name=game_type_name,
        date=date_time_stamp,
        nrow=number_of_rows
        ncol=number_of_columns
        nplayer=number_of_players # default: 2
        date=date_time_stamp
        )
    moves((player,row,col)[,        # multi row supported
      (player,row,col)]*
      )
    results((player,nsquare)[, (player,nsquare)]*)
    
    """
import sys, traceback
import re
import os
from pathlib import Path
from datetime import date
from datetime import datetime


from select_trace import SlTrace
from select_error import SelectError
    
###dC = None               # Global reference, set before game files read
class DotsGameFile:
    """ The hook from commands expressed via python command files to 
    the frame worker
    """
    version_str = "ver01_rel01"
    
    
    def __init__(self, pgm_info=None, history=None, file_dir=None, file_prefix="dotsgame",
                 file_ext="gmres"):
        """ Setup games file output
        :pgm_info: program information string - args etc.
        :history: history of program, e.g. featurs
        :file_dir: file directory default=..\gmres
        :file_prefix: file prefix default: dotsgame
        :file_ext: file extension default: gmres
        """
        self.history = history
        self.pgm_info = pgm_info
        if file_dir is None:
            file_dir=r"..\gmres"
        self.file_dir = file_dir
        self.file_prefix = file_prefix 
        self.file_ext = file_ext 
        self.moves = []
        self.open_output()
        self.nfile = 0          # Number of files written
        self.nfile_error = 0    # Number of file errors
        self.game_no = 0        # Current game number, starting at 1
        self.ngame = 0          # Number of games written
        self.ngame_error = 0    # Number pf game errors
        self.preamble = r"""
from dots_game_file import *
"""
         
        
    def open_output(self, file_name=None):
        """ Open games file output
        :file_name:  output file name, base name if not absolute
        """
        if file_name is None:
            file_name = self.file_prefix 
            if not file_name.endswith("_"):
                file_name += "_"
            file_name += SlTrace.getTs()
        if not re.match(file_name, r"^.*\.[^.]+$"):
            file_name += "." + self.file_ext
        if not os.path.isabs(file_name):
            file_name = os.path.abspath(os.path.join(self.file_dir, file_name))
        self.file_path = file_name
        path = Path(file_name)
        if path.is_file():
            raise SelectError("gamesfile: %s already exists" % (file_name))
        
        try:
            self.fout= open(self.file_path, "w")
        except Exception as ex:
            SlTrace.lg("open_output(%s) failed: %s" %
                       (self.file_path, str(ex)))
            raise SelectError("No games files")
        print("# %s" % self.file_path, file=self.fout)
        d2 = datetime.now().strftime("%B %d, %Y %H:%M")
        print("# On: %s\n" % d2, file=self.fout)
        print("# pgm_info = {}".format(self.pgm_info), file=self.fout)
        print("", file=self.fout)
        
    
    def start_game(self, game_name="dots", nplayer=2, nrow=None, ncol=None):
        """ Start producing game resultStep
        :game_name: game name default: dots
        :nplayer: Number of players default: 2
        :nrow: number of rows REQUIRED 
        :ncol: number of columns REQUIRED 
        """
        if game_name is not None:
            self.game_name = game_name
        self.nplayer = nplayer
        self.game_results = nplayer*[0]
        if nrow is not None:
            self.nrow = nrow
        if ncol is not None:
            self.ncol = ncol
        self.game_no += 1
        self.move_no = 0              # Track number of moves
        self.moves = []             # Collect move tuples (player, row, col)
        self.time_beg = datetime.now()

        self.game_ts = SlTrace.getTs(dp=4)
        if self.ngame == 0:
            SlTrace.lg(r"""Game file version("%s")""" % self.version_str)
            print(r"""version("%s")""" % self.version_str, file=self.fout)
            print(r'''history(r"""%s""")''' % self.history, file=self.fout)
            print(r'''pgm_info(r"""%s""")''' % self.pgm_info, file=self.fout)

    def next_move(self, player=None, row=None, col=None):
        """ Store next move tuple
        :player: player number 1,2,...
        :row: row number 1,2,... from left
        :col: col number 1,2,... from top
        """
        self.move_no += 1
        if player is None:
            raise SelectError("Missing player on move %d" % self.move_no)

        if row is None:
            raise SelectError("Missing row on move %d" % self.move_no)

        if col is None:
            raise SelectError("Missing col on move %d" % self.move_no)
        
        self.moves.append((player,row,col))


    def end_game(self, results=None):
        """ Process whole game
        :results: list of result tuples (player, nsquare)
        """
        if len(self.moves) == 0:
            return              # No moves - no game

        self.time_end = datetime.now()
        self.time = (self.time_end-self.time_beg).total_seconds()
        if results is not None:
            for result in results:
                player_num = result[0]
                if player_num > len(self.game_results):
                    SlTrace.lg("end_game result player_num:%d > number_of players:%d - ignored"
                               % (player_num, len(self.game_results)))
                    continue
                
                self.game_results[player_num-1] = result[1]

            
        print("""game(name="%s", game_no=%d, time=%.3f, nplayer=%s, nrow=%d, ncol=%d, nmove=%d, ts="%s")"""
              % (self.game_name,
                 self.game_no,
                 self.time,
                 self.nplayer, self.nrow, self.ncol,
                 len(self.moves), self.game_ts), 
              file=self.fout)
        max_line_len = 70
        line_str = "moves(["            
        for i in range(len(self.moves)):
            move = self.moves[i]
            move_str = "(%d,%d,%d)" % (move[0], move[1], move[2])
            if len(line_str) + len(move_str) + 1 > max_line_len:
                if i > 0:
                    line_str += ","
                SlTrace.lg(line_str, "list_moves")
                print(line_str, file=self.fout)
                if not line_str.endswith(",") and not line_str.endswith("["):
                    SlTrace.lg("Possible problem: line_str:%s" % line_str, to_stdout=True)
                line_str = move_str
            else:
                if i > 0:
                    move_str = ", " + move_str
                line_str += move_str
        line_str += "])"
        SlTrace.lg(line_str, "list_moves")
        print(line_str, file=self.fout)
                
        results_str = ""
        for i in range(len(self.game_results)):
            result = self.game_results[i]
            if results_str == "":
                results_str = "results("
            else:
                results_str += ", "
            results_str += "(%d,%d)" % (i+1, result)
        results_str += ")\n"
        print(results_str, file=self.fout)
        self.ngame += 1
        if SlTrace.trace("flush_outputs"):
            self.fout.flush()
        
        
    def end_file(self):
        """ Close results file
        """
        if self.fout is not None:
            self.fout.close()
            SlTrace.lg("Closeing results file %s" % self.file_path)
            self.fout = None
            self.nfile += 1


    def results_update(self, player_num=None, nsquare=None):
        """ Update player's results
        :player_num: player order in game:1 (first),...
        :nsquare: Number of additional squares
        """
        if player_num > len(self.game_results):
            SlTrace.lg("player num:%s is out of range(1-%d) - ignored"
                       % (player_num, len(self.game_results)))
            return
        
        self.game_results[player_num-1] += nsquare
    """
    Process 
    """
    def procFilePyPlus(self, file_name, preamble=None):
        """ Process python code file, with prefix text
        :preamble: text string placed before file contents
                    default: self.preamble (newline appended if none
        :inFile: input file name
        """
        if not os.path.isabs(file_name):
            file_name = os.path.abspath(os.path.join(self.file_dir, file_name))
        path = Path(file_name)
        if not path.is_file():
            self.error("inFile({} was not found".format(file_name))
            return False
        compile_str = ""
        if preamble is None:
            preamble = self.preamble
        if not preamble.endswith("\n"):
            preamble += "\n"
        compile_str = preamble
        try:
            fin = open(file_name)
            compile_str += fin.read()
            fin.close()
        except Exception as ex:
            SlTrace.lg("input file %s failed %s" % (file_name, str(ex)))
            return False
        tmp_file = r"..\dots_tmp_file.py"
        ftout = open(tmp_file, "w")
        print(compile_str, file=ftout)
        ftout.close()
        with open(tmp_file) as ftin:
            try:
                code = compile(ftin.read(), tmp_file, 'exec')
            except Exception as e:
                tbstr = traceback.extract_stack()
                SlTrace.lg("Compile Error in %s\n    (%s)\n    %s)"
                        % (tmp_file, file_name, str(e)))
                return False
        try:
            exec(code)
        except Exception as e:
            etype, evalue, tb = sys.exc_info()
            tbs = traceback.extract_tb(tb)
            SlTrace.lg("Execution Error in %s\n   (%s)\n    %s)"
                    % (tmp_file, file_name, str(e)))
            inner_cmds = False
            for tbfr in tbs:         # skip bottom (in dots_commands.py)
                tbfmt = 'File "%s", line %d, in %s' % (tbfr.filename, tbfr.lineno, tbfr.name)
                if not inner_cmds and tbfr.filename.endswith("dots_commands.py"):
                    inner_cmds = True
                    SlTrace.lg("    --------------------")         # show bottom (in dots_commands.py)
                SlTrace.lg("    %s\n       %s" % (tbfmt, tbfr.line))
            return False
        return True
                

    """
    Basic game file loading functions
    """
    def game(self, name=None, nplayer=2,
                nrow=None, ncol=None, nmove=None, ts=None):
        """ Start processing of game
        """
        SlTrace("game(name=%s, nplayer=%d, nrow=%d, ncol=%d, nmove=%d, ts=%s)"
                % (name, nplayer, nrow, ncol, nmove, ts), "game")
        self.moves = []
        
        
    def moves(self, moves):
        """ Add next set of moves, game or part of game
        :moves: list of  move  tuples (player number, row(1,..., col(1...)
        """
        self.moves.extend(moves)

    def game_results(self, *results):
        """ End current game's input, specifying results
        :results: comma separated list of result tuples (player_no, nsquares)
        """
        self.game_results = results
        self.ngame += 1
        move_no = 0
        if SlTrace.trace("game_results"):
            for move in self.moves:
                move_no += 1
                SlTrace.lg("%3d: move(player=%d, row=%d, col=%d)" %
                            (move_no, move[0], move[1], move[2]))
        results_str = ""
        for result in self.results:
            if results_str == "":
                results_str = "game_results: "
            else:
                results_str += ", "
                
            results_str += (" player=%d, squares=%d" %
                        (result[0], result[1]))
        SlTrace.lg(results_str)

        
if __name__ == "__main__":
    rF = DotsGameFile(file_dir=r"..\test_gmres")

    rF.start_game(game_name="test1", nplayer=2, nrow=7, ncol=7)
    rF.next_move(1,2,2)
    rF.next_move(2,2,3)
    rF.next_move(1,3,4)
    rF.next_move(2,3,4)
    rF.end_game([(1,2), (2,5)])
    
    rF.start_game(game_name="test2", nplayer=2, nrow=5, ncol=7)
    rF.next_move(1,2,3)
    rF.next_move(2,2,4)
    rF.next_move(1,3,5)
    rF.next_move(2,3,6)
    rF.end_game([(1,2), (3,4)])
    rF.end_file()
    SlTrace.lg("End of Test")        