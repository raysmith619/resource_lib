#tk_rem_access.py   24Jan2024  crs, Author
""" Remote access to tk canvas information
tkinter canvas resides in main process
Subprocess has been called with open pipes to the main (tk) process
obtaining pipes to the subprocess's stdin for requests and
stdout for results.
"""
import pickle
from select_trace import SlTrace

from pipe_to_queue import PipeToQueue

g_cmd_prefix = "#:::#:"
class TkRemHost:
    """Host control containing tkinter canvas
    Only lines starting with cmd_prefix are interpreted as commands
    """
    cmd_prefix = g_cmd_prefix
    
    def __init__(self, canvas, stdin, stdout):
        """ Setup cmd interface
        :canvas: tkinter canvas
        :stdin: stdin pipe
        :stdout: stdout pipe
        """
        self.canvas = canvas
        self.stdin = stdin
        self.stdout = stdout
        self.sto = PipeToQueue(stdout)
    
    def send_resp_str(self, resp):
        """ Send response line
        :resp: response string
        """
        st = resp + "\n"
        wt_line = bytes(st)
        self.stdin.write(wt_line)
    
    def get_cmd_str(self):
        """ Get command, if one
        :returns: cmd string, "" if none
        """
        while True:
            ln = self.sto.get_line()
            if ln == "":
                return ""
            
            if not ln.startswith(TkRemHost.cmd_prefix):
                print(ln)   # Echo non-command line
            
            cmd = ln[len(TkRemHost.cmd_prefix):]
            return cmd

    def cmd_proc(self):
        """ Check for and, if one found, process next command
        """
        cmd_str = self.get_cmd_str()
        if cmd_str == "":
            return  ""    # No command so far
        SlTrace.lg(f"cmd: {cmd_str}")        
    
class TkRemUser:
    """User (remote) control requesting canvas information
    To avoid confusion caused by diagnostic use of stdout
    cmds will be send with a unique prefix
    """
    cmd_prefix = g_cmd_prefix
    def __init__(self, remote=True, simulated=False):
        """ Handle user (wxPython) side of communications
        :remote: connect with remote False: pass calls
                default: True - use stdout, stdin
        :simulated: True: simulate tk input default: False
        """
        self.remote = remote
        
    def send_cmd_str(self, cmd_str):
        """ Send command(request) to host
        via stdout
        :cmd_str: command string
        """
        st = TkRemUser.cmd_prefix + cmd_str
        print(st)
    
    def get_resp_str(self):
        """ Get command response from stdin
        :returns: response string
        """
        if not self.remote:
            return "NO Remote"
        
        while True:
            resp = input()
            if resp != "":
                break
        return resp
    
    def get_braille_cells(self, 
                        x_min=None, y_min=None,
                        x_max=None, y_max=None,
                        ncols=None, nrows=None):
        """ Get braille cells from tk canvas
        """
        
        if self.simulated:
            from braille_cell_text import BrailleCellText
            from wx_braille_cell_list import BrailleCellList
            
            spokes_picture="""
            ,,,,,,,,,,,iii
            ,,,,,,,,,,iiiii
            ,,,,,,,,,,iiiii,,,,,,vvv
            ,,,,,,,,,,iiiii,,,,,vvvvv
            ,,,,,,,,,,,,ii,,,,,,vvvvv
            ,,,bb,,,,,,,,i,,,,,,vvvvv
            ,,bbbbb,,,,,,i,,,,,vv
            ,,bbbbb,,,,,,i,,,,vv
            ,,bbbbbbb,,,,ii,,vv
            ,,,,,,,,bbbb,,i,vv,,,,,,,,rr
            ,,,,,,,,,,bbbbivv,,,,,,,,rrrr
            ,,,,,,,,,,,,,bvvrrrrrrrrrrrrr
            ,,,,,,,,,,ggggyoo,,,,,,,,rrrr
            ,,,,,,,,gggg,,y,oo,,,,,,,,rr
            ,,ggggggg,,,,yy,,oo
            ,,ggggg,,,,,,y,,,,oo
            ,,ggggg,,,,,,y,,,,,oo
            ,,,gg,,,,,,,,y,,,,,,ooooo
            ,,,,,,,,,,,,yy,,,,,,ooooo
            ,,,,,,,,,,yyyyy,,,,,ooooo
            ,,,,,,,,,,yyyyy,,,,,,ooo
            ,,,,,,,,,,yyyyy
            ,,,,,,,,,,,yyy
            """
            spokes_bct = BrailleCellText(text=spokes_picture)
            spokes_cells = spokes_bct.get_cells()
            return spokes_cells
            
        args = locals()
        args["cmd_name"] = "get_braille_cells"
        cmd_str = pickle(args)
        self.send_cmd_str(cmd_str)
        cmd_resp = self.get_resp_str()
        return cmd_resp
   