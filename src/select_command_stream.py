# command_file.py
"""
Command Stream
Facilitates reading human readable commands from files(stream input)
Supports Python(.py) files and internal(.csrc) files 
Specifying input/output file names
Specifying execution parameters such as:
    delay before command execution
    delay after command execution
Executing programs from files
    Stepping through program
Generating listing file
Facilitate integration with game program by
 1. open - open input file
 2. get_cmd - return next command for action by game functions
 
"""
from tkinter import filedialog
from tkinter import *
import re
import os
import time
import traceback

from select_error import SelectError
from select_trace import SlTrace
from dots_commands import DotsCommands
from select_stream_command import SelectStreamCmd, SelectStreamToken
    
class SelectCommandStream:
    CONTROL_NAME_PREFIX = "command_file"
    def __init__(self,
                 open=True,
                 execution_control=None,
                 in_file=None,
                 src_file=None,
                 src_dir=None,
                 src_lst=False,
                 stx_lst=False,
                 lst_file_name=None,
                 cmd_execute=None,
                 stream_stack=None,
                 debugging=False
                 ):
        """ Player attributes
        :in_file: Opened input file handle, if one
        :src_file: source file name .py for python
                        else .csrc built-in language
        :open: Open source file default: True - open file on object creation
        :execution_control: interface execution control
                            if any, (SelectComandFileControl)
                            e.g. stepping
        :run: run file after opening
                default: False
        :run_cmd: command to run when run button hit
                default: self.run
        :src_dir: default src directory
                default: "csrc"
        :src_lst: List src as run
                    default: No listing
        :stx_lst: List expanded commands as run
                    default: No listing
        :lst_file_name: listing file name
                default: base name of src_file_name
                        ext: ".clst"
        :cmd_execute: function to be called to execute each
                         command as obtained from file
        :stream_stack: Stack of SelectCommandStream active
                streams calling this the current one
                None - no callers
        :debugging:  debugging/test less requirements
        """
        self.execution_control = execution_control
        self.src_file_name = src_file
        if src_dir is None:
            src_dir = "../csrc"
        if src_dir is None:
            src_dir = "../csrc"
        SlTrace.setProperty("source_files", src_dir)
        self.file_type = None   # py, csrc file type, when determined
        self.src_dir = src_dir
        self.set_src_lst(src_lst)
        self.set_stx_lst(stx_lst)
        self.cmd_execute = cmd_execute
        if self.src_file_name is not None:
            if not self.check_file(self.src_file_name):
                raise SelectError("File %s not found" % self.src_file_name)
            
        self.in_file = in_file
        self.stcmd_stack = []   # get/unget stcmd stack
        self.tok = None         # Token if found
        self.line = None    # Remaining unparsed line
        self.src_prefix = ""    # Source listing prefix
        self.new_file = True    # Not opened
        self.stream_stack = stream_stack
        self.debugging=debugging
        self.dots_commands = DotsCommands(self)
        
        
    def src_dir_search(self):
        start_dir = self.src_dir
        filedir =  filedialog.askdirectory(
            initialdir = start_dir,
            title = "Select dir")
        name = filedir
        self.src_file_name = name
        self.set_ctl_val("src_dir_name", name)


    def src_file_search(self):
        start_dir = self.src_dir
        filename =  filedialog.askopenfile("r",
            initialdir = start_dir,
            title = "Select file",
            filetypes = (("csrc files","*.csrc"),("all files","*.*")))
        fullname = filename.name
        dir_name = os.path.dirname(fullname)
        base_name = os.path.basename(fullname)
        self.src_dir = dir_name
        self.set_ctl_val("src_dir_name", dir_name)
        self.src_file_name = base_name
        self.set_ctl_val("src_file_name", base_name)
        filename.close()

    def run_button(self):
        """ Called when our button is pressed
        """
        if self.run_cmd is not None:
            return self.run_cmd()
        
        return self.run_file()  # Local - default
    
    
    def run_file(self, src_file=None, cmd_execute=None):
        """
        Run command file (Local version)
        """
        SlTrace.lg("run_file")
        if src_file is None:
            src_file = self.get_val_from_ctl("src_file_name")
        if re.match(r'^\s*$', src_file) is not None:
            SlTrace.lg("Blank src file name - ignored")
            return

        file_type = self.get_file_type(src_file)
        path = self.get_file_path(src_file)
        if self.new_file:
            self.open(src_file)        
        while True:
            cmd = self.get_cmd()
            if cmd is None:
                break
            SlTrace.lg("cmd: %s" % cmd, "cexecute")
            if self.cmd_execute is not None:
                if not self.cmd_execute(cmd):
                    raise SelectError("cmd_execute(%cmd) failure" % cmd)
        


    def run_step_file(self):
        """
        steep command filr
        """
        SlTrace.lg("run_step_file")

    def set_debugging(self, debugging=True):
        self.dots_commands.set_debugging(debugging=debugging)


    def set_play_control(self, play_control):
        """ Connect command stream processing to game control
        :play_control:  game control
        """
        self.dots_commands.set_play_control(play_control)


    def set_cmd_stream_proc(self, cmd_stream_proc):
        """ Connect command stream processing to command processing
        :play_control:  game control
        """
        self.dots_commands.set_cmd_stream_proc(cmd_stream_proc)


    def open(self, src_file=None):
        """ Open command file
        Opens output files, if specified
        :src_file: Source file default, if no extension ext="csrc"
            If no extension: look for .py, then .csrc
            in source_directories
            else look for file in source_directories
        :returns: True iff successful open (note that py type
                flles are are opened when first get_tok is called
        """
        self.lineno = 0         # Src line number
        self.eof = True         # Cleared on open, set on EOF
        if src_file is None:
            if self.src_file_name is None:
                raise SelectError("open: no src_file and no self.src_file_name")
            
            src_file = self.src_file_name
        self.src_file_name = src_file
        if not self.check_file(self.src_file_name):
            return False
        
        self.new_file = False
        if self.file_type == "csrc":
            try:
                if self.src_lst or SlTrace.trace("csrc"):
                    SlTrace.lg("Open %s" % self.src_file_path)
                self.in_file = open(self.src_file_path, "r")
            except IOError as e:
                errno, strerror = e.args
                SlTrace.lg("Can't open command source file %s: %d %s"
                            % (self.src_file_path, errno, strerror))
                self.eof = True
                return False
        self.eof = False
        return True


    def check_file(self, src_file=None):
        """ Check file name / existence
        :src_file:  file name
        """
        path = self.get_file_path(src_file)
        if self.src_lst:
            SlTrace.lg("check_file(%s)" % path)

        ext = None
        match = re.search(r'\.([^.]+)$', path)
        self.file_type = "py"       # Default type
        if match:
            ext = match.group(1)
            if ext == "py":
                self.file_type = "py"
            elif ext == "csrc":
                self.file_type = "csrc"
            else:
                self.file_type = "py"
        self.src_file_path = path
        self.src_file_name = os.path.basename(path)     # Record        
        self.eof = False                # Set True at EOF
        if self.src_lst:
            SlTrace.lg("source path: %s" % path)
        return True


    def get_file_path(self, src_file=None, req=True):
        """ Get absolute file path, if one
        :src_file: name or relative path default: self.src_file_name
        :req: Raise error if not found default: True
        """
        if src_file is None:
            src_file = self.src_file_name
        path = SlTrace.getSourcePath(src_file, report=False, req=False)
        if path is None:
            path = SlTrace.getSourcePath(src_file + ".py", report=False, req=False)
        if path is None:
            path = SlTrace.getSourcePath(src_file + ".csrc", report=False, req=False)
        if path is None:
            if req:
                raise SelectError("open can't find %s(.py, .csrc) in %s"
                              % (src_file, SlTrace.getSourceDirs(string=True)))
        return path    
            

    def reset(self, src_file=None):
        """ Reset stream to allow traversing again
            closes current file, if any, reopen
            :src_file: new file name, if present default: use current name
        """
        if (hasattr(self, "in_file")
                and self.in_file is not None
                and not self.in_file.closed):
            self.in_file.close()
        if not self.open(src_file=src_file):
            raise SelectError("Can't reset command_file %s" % self.src_file)
        
        self.stcmd_stack = []   # get/unget stcmd stack
        self.tok = None         # Token if found
        self.line = None        # Remaining unparsed line
        return True
    
    
    def get_cmd(self):
        """ Get next command: word [[, ] word]* [EOL|;]
         ==> cmd.name == first word
             cmd.args == subsequent words
        :returns: cmd, None on EOF
        """
        if self.stcmd_stack:
            stcmd = self.stcmd_stack.pop()
            return stcmd

        if self.new_file:
            if not self.open():
                raise SelectError("get_cmd failed to open file")
            
        if self.eof:
            return SelectStreamCmd(SelectStreamCmd.EOF)
        
        toks = []
        tok = None
        if self.file_type == 'py':
            return SelectStreamCmd(SelectStreamCmd.EXECUTE_FILE)

        while True:
            tok = self.get_tok()
            SlTrace.lg("get_cmd:tok: %s" % tok, "tok_lst")
            if (tok.type == SelectStreamToken.EOL
                or tok.type == SelectStreamToken.SEMICOLON
                or tok.type == SelectStreamToken.EOF):
                if len(toks) == 0:
                    if tok.type == SelectStreamToken.EOF:
                        break       # EOF
                    continue        # Ignore if no cmd started
                break               # End of command
            if tok.type == SelectStreamToken.QSTRING:
                if len(toks) == 0:
                    toks.append(tok)                # Allow doc_string command
                    break           # Special doc_string cmd
            toks.append(tok)
        
        if len(toks) == 0:
            self.set_eof()
            stcmd =  SelectStreamCmd(SelectStreamCmd.EOF) 
        elif len(toks) == 1 and toks[0].type == SelectStreamToken.QSTRING and toks[0].doc_string:
            stcmd = SelectStreamCmd(SelectStreamCmd.DOC_STRING,
                                    args=toks)     
        else:
            tok = toks.pop(0)
            if not re.match(r'^[_a-z]\w*', tok.str.lower()):
                raise SelectError("'%s' is not a legal stream command name"
                                  % tok.str)
            stcmd = SelectStreamCmd(tok.str.lower(), args=toks)
    
        if self.stx_lst or SlTrace.trace("stx_lst"):
            prefix_base = " " * len(self.src_prefix)    # src name length
            prefix1 = prefix_base + " STCMD:"
            prefix2 = prefix_base + " -----:"    # if subsequent start with this
            cmdstr = str(stcmd)
            cmdstr_lines = cmdstr.splitlines()
            for i in range(len(cmdstr_lines)):
                if i == 0:
                    prefix = prefix1
                else:
                    prefix = prefix2
                SlTrace.lg(prefix + " " + cmdstr_lines[i])
                 
        return stcmd
    

    def get_tok(self):
        """ Get next input token
        Ignores comments(Unquoted # to end of line)
        Tokens end at whitespace, end of line, ";",
            character not part of the token (e.g. ",", ";")
        """
        while True:
            if self.line is None:
                self.line = self.get_line()  # Get next line
            if self.line is None:
                return SelectStreamToken(SelectStreamToken.EOF)
                
            self.line = self.line.lstrip()
            if self.get_tok_comment():
                continue                # Ignore comment
            if self.get_tok_word():
                return self.tok
            if self.get_tok_quote():
                return self.tok
            if self.get_tok_number():
                return self.tok
            if self.get_tok_punct():    # incl SEMICOLON, PERIOD
                return self.tok
            if self.get_tok_eol():
                return self.tok


    def get_tok_comment(self):
        """ Check if we are at a comment
        Returns a token, which is can be ignored
            comment format: "#" to rest of line
        """
        if self.line.startswith("#"):
            tok = SelectStreamToken(SelectStreamToken.COMMENT,
                                    str=self.line)
            self.line = ""        # To end of line
            return tok
        
        
    def get_tok_quote(self):
        """ get quoted str ("...." or '....')
                    \<chr> escapes the included character
        :returns: True if token found, result in self.tok
        """
        # Must do multicharacter quote tests
        # before single character quote tests
        if self.get_tok_str(delim='"""', multi_line=True):
            self.tok.doc_string = True
            return True
        
        if self.get_tok_str(delim="'''", multi_line=True):
            self.tok.doc_string = True
            return True
        
        if self.get_tok_str(delim='"'):
            return True
        if self.get_tok_str(delim=("'")):
            return True
 
        return False

    
    def get_tok_str(self, delim=None, multi_line=False, esc='\\'):
        """ Get string, creating a SelectStreamToken in self.tok
        adjusting self.line to after string trailing delimiter
        :delim: String trailing delimiter default: REQUIRED
        :multi_line: string can be multi-line default: single line
        :esc: escape character defaule "\"
        """
        if delim is None:
            raise SelectError("get_tok_str: missing required delim")
        
        line = self.get_line()
        if line is None or not line.startswith(delim):
            self.line = line
            return False
        
        tok_str = ""
        iend = 0
        iend += len(delim)        # Start after beginning delimiter
        line = line[iend:]
        iend = 0
        while True:
            if line is None:
                line = self.get_line()
                iend = 0
            if line is None:
                break               # EOF
            while iend < len(line):
                ch = line[iend]
                if esc is not None and ch == esc:
                    iend += 1
                    if iend >= len(line):
                        ch = "\n"           # Escaped newline
                    else:
                        ch = line[iend]
                        iend += 1
                    continue                # Go on to character after escaped
                rem_line = line[iend:]
                if rem_line.startswith(delim): 
                    self.tok = SelectStreamToken(SelectStreamToken.QSTRING,
                                                  str=tok_str,
                                                  delim=delim)
                    iend += len(delim)
                    self.line = line[iend:]
                    return True
                
                ch = line[iend]
                tok_str += ch
                iend += 1
            if multi_line:
                tok_str += "\n"         # Add in newline, separating lines
                line = self.get_line()
                iend = 0
                if line is None:
                    break               # EOF
                continue
            break                       # Single line 
        raise SelectError("Missing delimiter (%s)" % delim)
 
                        
    def get_tok_word(self):
        """ get word from input ([a-z_]\w*)
        :returns: True if token found, result in self.tok
        """
        line = self.line
        if len(line) == 0:
            return False
        ib = 0
        iend = ib
        tok_str = ""
        ch = line[ib]
        if not re.match(r'[a-zA-Z_]', ch):
            return False
        
        tok_str = ch
        iend += 1    
        while iend < len(line):
            ch = line[iend]
            if not re.match(r'\w', ch):
                break       # end of word
            tok_str += ch
            iend += 1
        self.tok = SelectStreamToken(SelectStreamToken.WORD,
                                      str=tok_str)
        self.line = line[iend:]
        return True


    def get_tok_number(self):
        """ get nu ber from input ([+-]?\d*(\.\d*)?
        :returns: True if token found, result in self.tok
        """
        line = self.line
        if len(line) == 0:
            return False
        
        match = re.match(r'^[+-]?(\d+|(\d*\.\d*))', line)
        if not match:
            return False
        
        tok_str = match.group()
        self.tok = SelectStreamToken(SelectStreamToken.NUMBER,
                                     tok_str)
        self.line = line[len(tok_str)+1:]
        return True


    def get_tok_punct(self):
        """ get punctuation non-tokenized, non-whitespace
        :returns: True if token found, result in self.tok
                Checks for ;(SEMICOLON), .(PERIOD)
                    else labeled (PUNCT)
        """
        line = self.line
        if len(line) == 0:
            return False
        
        match = re.match(r'^\S', line)
        if not match:
            return False
        
        tok_str = line[0]
        if tok_str == ";":
            tok_type = SelectStreamToken.SEMICOLON
        elif tok_str == ".":
            tok_type = SelectStreamToken.PERIOD
        else:
            tok_type = SelectStreamToken.PUNCT
                
        self.tok = SelectStreamToken(tok_type,
                                     tok_str)
        self.line = line[len(tok_str)+1:]
        return True


    def get_tok_eol(self):
        """ get End of Line
        :returns: True if token found, result in self.tok
        """
        line = self.line
        if len(line) == 0:
            tok_str = "\n"
            self.tok = SelectStreamToken(SelectStreamToken.EOL,
                                     tok_str)
            self.line = None
            return True
            
        return False


    def get_src_file_path(self):
        """ Get current source file path
        """
        
        return self.src_file_path
    

    def get_line(self, chomp=True):
        """ Get next source line
            use self.line if not None
            Set self.line to None
        :chomp: Remove EOL iff at end on reading from file
        """
        if self.line is not None:
            line = self.line
            self.line = None
            return line        # Return unprocessed part
        
        if self.eof:
            return None
        
        line = self.in_file.readline()
        if line is None or line == "":
            self.eof = True
            if self.src_lst or SlTrace.trace("csrc"):
                SlTrace.lg("%s: End of File"
                           % (os.path.basename(self.src_file_name)))
            return None
        
        if chomp:
            if len(line) > 0:
                line = line.splitlines()[0]     # Generic line separator 
        self.lineno += 1
        if self.src_lst or SlTrace.trace("src_lst"):
            self.src_prefix = ("%s %3d:"
                       % (os.path.basename(self.src_file_name),
                          self.lineno))
            SlTrace.lg("%s %s"
                       % (self.src_prefix,
                          line))
        return line


    
    """
    Process input files:
        .py ==> python script
        .bwif ==> BlockWorld scrip
    """
    def procFile(self, src_file=None):
        path = self.get_file_path(src_file)
        file_type = self.get_file_type(src_file)
        try:
            if file_type == "py":
                return self.procFilePy(path)
                
            return self.procFileCsrc(path)
        except:
            raise SelectError("File processing error in " + path)
            return False

    def get_file_type(self, src_file=None):
        """ Get file type (py, csrc) if any
        :src_file: source file name abs or relative
                if no extension: look for no extension, py, or csrc
        """
        path = self.get_file_path(src_file=src_file)
        pat_ftype = re.compile(r'^(.*)\.([^.]+)$')
        file_type = "py"    # if no extension
        match_ftype = pat_ftype.match(path)
        if match_ftype:
            ext = match_ftype.group(2)
            if ext.lower() == "csrc":
                file_type = "csrc"
        return file_type

    
    """
    Process (Execute) standard python/Jython file
    """
    def procFilePy(self, src_file):
        path = self.get_file_path(src_file)
        with open(path) as f:
            try:
                code = compile(f.read(), path, 'exec')
            except Exception as e:
                tbstr = traceback.extract_stack()
                SlTrace.lg("Compile Error in %s\n    %s)"
                        % (path, str(e)))
                return False
            try:
                exec(code)
            except Exception as e:
                etype, evalue, tb = sys.exc_info()
                tbs = traceback.extract_tb(tb)
                SlTrace.lg("Execution Error in %s\n%s)"
                        % (path, str(e)))
                inner_cmds = False
                for tbfr in tbs:         # skip bottom (in dots_commands.py)
                    tbfmt = 'File "%s", line %d, in %s' % (tbfr.filename, tbfr.lineno, tbfr.name)
                    if not inner_cmds and tbfr.filename.endswith("dots_commands.py"):
                        inner_cmds = True
                        SlTrace.lg("    --------------------")         # show bottom (in dots_commands.py)
                    SlTrace.lg("    %s\n       %s" % (tbfmt, tbfr.line))
                return False
            self.eof = True             # Consider at end of file
        return True
    
    """ 
    Run files listed in list file
    Currently only supports a sinle file type in list
    specified by the list file extension
        bwil - list of bwif files ( default)
        bwpyl - list of Jython files
    
    """    
    def runList(self, listFile):
        pat_ftype = re.compile(r'^(.*)\.([^.]+)$')
        match_ftype = pat_ftype.match(listFile)
        if match_ftype:
            ext = match_ftype.group(2)
            if ext.lower() == "pyl":
                return self.runListPy(listFile)
        
        return self.bExec.runList(listFile)


    """
    Run python files listed, one per line
    Ignore comments: text starting # to end of line
    Ignore lines consisting only of whitespace
    """
    def runListPy(self, listFile):
        listPath = self.trace.getSourcePath(listFile)
        if listPath == "":
            self.error("listFile({} was not found".format(listFile))
            return False
        pat_comment = re.compile(r'^([^#]*)#')
        pat_blanks = re.compile(r'^\s*$')
        
        fileno = 0
        with open(listPath) as inf:
            for line in inf:
                m = pat_comment.match(line)
                if m:
                    line = m.group(1)   # Remove comment
                mb = pat_blanks.match(line)
                if mb:
                    continue        #Ignore blank lines
                line = line.strip()
                fileno += 1
                print("Running File {}: {}".format(fileno, line)) # Removing leading and trailing whitespace    
                if not self.procFilePy(line):
                    return False
                if self.timeBetween > 0:
                    time.sleep(self.timeBetween)
        return True


    def is_eof(self):
        """ Are we at end of file?
        """
        return self.eof
 
    
    def set_eof(self, eof=True):
        """ Set as eof
        """
        self.eof = eof
        

    def is_src_lst(self):
        """ Are we listing source lines?
        """
        return self.src_lst

    def set_src_lst(self, lst=True):
        """ Are we listing source lines?
        :lst: Listing default: True
        """
        self.src_lst = lst

    def is_stx_lst(self):
        """ Are we listing executing commands?
        """
        return self.stx_lst

    def set_stx_lst(self, lst=True):
        """ Are we listing execution lines?
        :lst: Listing default: True
        """
        self.stx_lst = lst
 
 
    def is_debugging(self):
        """ Ck if we are debugging input stream
        """
        if self.execution_control is not None:
            return self.execution_control.is_debugging()
        return False
            
        
    def is_step(self):
        """ Are we doing a step
        """
        if self.execution_control is not None:
            return self.execution_control.is_step()
        return False
        
        
    def is_to_line(self, cur_lineno=None, src_lines=None):
        if self.execution_control is not None:
            return self.execution_control.is_to_line(
                    cur_lineno=cur_lineno, src_lines=src_lines)

        return False
    

    def wait_for_step(self):
        """ Wait for next user step/continue/stop command
        """
        if self.execution_control is not None:
            return self.execution_control.wait_for_step()
        return True
    
    
if __name__ == "__main__":
    import os
    import sys
    from tkinter import *    
    import argparse
    from PIL import Image, ImageDraw, ImageFont
    
    
    file = "one_square"             # Number of x divisions
    run = True                      # Number of y divisions
    src_lst = True                  # List source as run
    stx_lst = True                # List Stream Trace cmd
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-f', '--file', default=file)
    parser.add_argument('-r', '--run', action='store_true', default=run,
                        help=("Run program upon loading"
                              " (default:%s" % run))
    parser.add_argument('-l', '--src_lst', action='store_true', default=src_lst,
                        help=("List source as run"
                              " (default:%s" % src_lst))
    parser.add_argument('-x', '--stx_lst', action='store_true', default=stx_lst,
                        help=("List commands expanded as run"
                              " (default:%s" % stx_lst))

    args = parser.parse_args()             # or die "Illegal options"
    
    file = args.file
    src_lst = args.src_lst
    stx_lst = args.stx_lst
    run = args.run
    
    SlTrace.lg("%s %s\n" % (os.path.basename(sys.argv[0]), " ".join(sys.argv[1:])))
    SlTrace.lg("args: %s\n" % args)
        
    root = Tk()
    frame = Frame(root)
    frame.pack()
    SlTrace.setProps()
    cF = SelectCommandStream(
                     src_lst=src_lst,
                     stx_lst=stx_lst,
                     src_file=file)
    cF.set_debugging()

    '''
    from select_game_control import SelectGameControl
    game_control = SelectGameControl(None, title="SelectGameControl Testing")
    from select_play import SelectPlay
    play_control = SelectPlay(cmd_stream=cF,
                              game_control=game_control)
    '''
    while True:
        stcmd = cF.get_cmd()
        if stcmd is None:
            break
        if stcmd.is_type(SelectStreamCmd.EXECUTE_FILE):
            cF.procFile()
            break
    ##cF.open("cmdtest")
        
    root.mainloop()