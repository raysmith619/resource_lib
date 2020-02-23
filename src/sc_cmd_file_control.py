# sc_cmd_file_control.py
"""
Command File/Input Control
Facilitates Command File/Input Running
"""
import re
import os
import time
from tkinter import *
from tkinter import filedialog

from select_error import SelectError
from select_trace import SlTrace
from select_control_window import SelectControlWindow
from select_command_stream import SelectCommandStream
from dots_commands import DotsCommands    
from select_stream_command import SelectStreamCmd    
    
    
    
class SelectCommandFileControl(SelectControlWindow):

    CONTROL_NAME_PREFIX = "command_file_control"
    DEF_WIN_X = 500
    DEF_WIN_Y = 300
    

    def _init(self, *args,
                 title="File Control",
                 control_prefix=CONTROL_NAME_PREFIX,
                 run=False,
                 run_cmd=None,
                 new_board=None,
                 in_file=None,
                 src_file = None,
                 src_dir=None,
                 src_lst=False,
                 stx_lst=False,
                 lst_file_name=None,
                 cmd_execute=None,
                 debugging=False,
                 display=True,
                 **kwargs
                 ):
        """ Initialize subclassed SelectControlWindow singleton
        """
        self.run_cmd = run_cmd
        self.src_dir = src_dir
        self.src_lst = src_lst
        self.stx_lst = stx_lst
        self.src_file_name = src_file
        self.run = run
        self.new_board = new_board
        self.cmd_execute = None
        self.running = False
        self.debugging = debugging
        self.step_pressed = False
        self.cont_to_end_pressed = False
        self.cont_to_line_pressed = False
        self.is_to_line_nos = []
        self.is_to_line_pats = []   # Compiled rex
        self.stop_pressed = False
        
        super()._init(*args,
                      title=title, control_prefix=control_prefix,
                      **kwargs)    
        """ Player attributes
        :title: window title
        :in_file: Opened input file handle, if one
        :src_file: source file name .py for python
                        else .csrc built-in language
        :open: Open source file default: True - open file on object creation
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
                default: base name of src_file
                        ext: ".clst"
        :cmd_execute: function to be called to execute command
                        when running file default: none
        :display: True = display window default:True
        """
        if title is None:
            title = "Command Stream Control"
        self.title = title
        if src_file is not None:
            self.set_ctl_val("input.src_file_name", src_file)
        self.command_stream = SelectCommandStream(
            execution_control=self,
            src_file=src_file,
            src_dir=src_dir,
            src_lst=src_lst,
            stx_lst=stx_lst,
            )
        self.control_form()

        if self.run:
            self.run_file()
            
    def control_form(self):
        """ Setup control form
        entry / modification
        """
        win_width =  500
        win_height = 200
        win_x0 = 600
        win_y0 = 100
                    
        ###self.mw.withdraw()       # Hide main window
        win_setting = "%dx%d+%d+%d" % (win_width, win_height, win_x0, win_y0)

        
        self.mw.geometry(win_setting)
        self.mw.title(self.title)
        top_frame = Frame(self.mw)
        self.mw.protocol("WM_DELETE_WINDOW", self.delete_window)
        top_frame.pack(side="top", fill="x", expand=True)
        self.top_frame = top_frame
        inputs_frame = Frame(top_frame)
        inputs_frame.pack()
        
        field_name = "src_dir_name"
        dir_frame = Frame(inputs_frame)
        dir_frame.pack(side="top", fill="x", expand=True)
        self.set_fields(dir_frame, "input", title="")
        if self.src_dir is None:
            self.src_dir = "../csrc"
        self.src_dir = os.path.abspath(self.src_dir)
        self.set_entry(field=field_name, label="Dir", value=self.src_dir, width=60)
        self.set_button(field=field_name + "_search", label="Search", command=self.src_dir_search)

        field_name = "src_file_name"
        file_frame = Frame(inputs_frame)
        self.set_fields(file_frame, "input", title="")
        if self.src_file_name is not None:
            self.set_prop_val("input." + field_name, self.src_file_name)
        else:
            self.src_file_name = self.get_prop_val("input." + field_name, "")
        file_name = self.src_file_name
        self.set_ctl_val("input." + field_name, file_name)
        if os.path.isabs(file_name):
            dir_name = os.path.dirname(file_name)   # abs path => set dir,name
            self.set_ctl_val("input.dir_name", dir_name)    # reset
            file_name = os.path.basename(file_name)
        self.set_entry(field=field_name, label="Src File", value=file_name, width=15)
        self.set_button(field=field_name + "_search", label="Search", command=self.src_file_search)

        self.set_sep()
        field_name = "new_src_file"
        self.set_check_box(field=field_name + "_ck", label="", value=False)
        self.set_entry(field=field_name, label="New Src File", value="NA", width=15)
        
        self.set_vert_sep(top_frame)
        field_name = "running"
        run_frame1 = Frame(top_frame)
        run_frame1.pack(side="top", fill="x", expand=True)
        self.set_fields(run_frame1, field_name, title="Running")
        self.set_button(field="Run", label="Run", command=self.run_button)
        self.set_entry(field="cmd_delay", label="cmd delay", value = .5, width=5)
        self.set_button(field="stop", label="Stop", command=self.stop_button)
        
        run_frame2 = Frame(top_frame)
        run_frame2.pack(side="top", fill="x", expand=True)
        self.set_fields(run_frame2, field_name, title="")
        self.set_sep()
        self.set_check_box(field="new_game", label="New Game", value=False)
        self.set_check_box(field="new_board", label="New Board", value=False)
        self.set_sep()
        self.set_check_box(field="loop", label="Loop", value=False)
        self.set_entry(field="loop_time", label="Loop time", value=5., width=5)
        
        self.set_vert_sep(top_frame)
        field_name = "debugging"
        debugging_frame = Frame(top_frame)
        debugging_frame.pack(side="top", fill="x", expand=True)
        self.set_fields(debugging_frame, field_name, title="Debugging")
        self.set_button(field="step", label="Step", command=self.step_button)
        self.set_button(field="to_end", label="To End", command=self.cont_to_end_button)
        self.set_button(field="to_line", label="To Line", command=self.cont_to_line_button)
        self.set_entry(field="line1", label="lines", value = "", width=10)
        self.set_entry(field="line2", label="", value = "", width=10)
        self.set_entry(field="line3", label="", value = "", width=10)


    def step_button(self):
        """ Debugging step button
        """
        SlTrace.lg("Step Button")
        self.step_pressed = True
        self.cont_to_end_pressed = False
        self.cont_to_line_pressed = False
        if not self.is_running():
            self.start_continue()
 
 
  
 
    def is_debugging(self):
        """ Ck if we are debugging input stream
        """
        return self.debugging

 
    def is_running(self):
        """ Ck if we are running an input stream
        """
        return self.running
       
        
    def is_step(self):
        """ Are we doing a step
        """
        return self.step_pressed
        
        
        
        
    def is_to_line(self, cur_lineno=None, src_lines=None):
        """ Check if continue to line pressed
        """
        
        if not self.cont_to_line_pressed or cur_lineno is None:
            return False
        
        for lno in self.is_to_line_nos:
            if cur_lineno == lno:
                self.cont_to_line_pressed = False
                return True
        
        if src_lines is None:
            return False
        
        line_text = ""
        if cur_lineno > 0 and cur_lineno < len(src_lines):
            line_text = src_lines[cur_lineno-1]
        
        for pat in self.is_to_line_pats:
            sea = pat.search(line_text)
            if sea is not None:
                match_str = sea.group(0)
                SlTrace.lg("%s" % match_str)
                self.cont_to_line_pressed = False
                return True
                
        return False

    

    def wait_for_step(self):
        """ Wait for next user step/continue/stop command
        """
        self.step_pressed = False       # Wait for next
        while True:
            if (self.step_pressed
                    or self.cont_to_end_pressed
                    or self.cont_to_line_pressed
                    or self.stop_pressed):
                return
            if self.mw is not None and self.mw.winfo_exists():
                self.mw.update()
            time.sleep(.01)
        


    def stop_button(self):
        """ Stop file run
        """
        SlTrace.lg("Stop Button")
        self.stop_pressed = True


    def cont_to_end_button(self):
        """ Debugging continue to end button
        """
        SlTrace.lg("TBD")
        self.step_pressed = False
        self.cont_to_end_pressed = True
        self.cont_to_line_pressed = False
        if not self.is_running():
            self.start_continue()


    def cont_to_line_button(self):
        """ Debugging continue to line button
        """
        SlTrace.lg("Continue to Line")
        self.step_pressed = False
        self.cont_to_end_pressed = False
        self.cont_to_line_pressed = True
        self.set_vals()     # Collect edits
        self.is_to_line_nos = []
        self.is_to_line_pats = []   # Compiled rex

        value = self.get_val("debugging.line1", "")
        if re.match(r'[1-9]\d*', value):
            self.is_to_line_nos.append(int(value))
        else:
            self.is_to_line_pats.append(re.compile(value))

        value = self.get_val("debugging.line2", "")
        if re.match(r'[1-9]\d*', value):
            self.is_to_line_nos.append(int(value))
        else:
            self.is_to_line_pats.append(re.compile(value))

        value = self.get_val("debugging.line3", "")
        if re.match(r'[1-9]\d*', value):
            self.is_to_line_nos.append(int(value))
        else:
            self.is_to_line_pats.append(re.compile(value))
        
        if not self.is_running():
            self.start_continue()


    def src_dir_search(self):
        start_dir = self.src_dir
        filedir =  filedialog.askdirectory(
            initialdir = start_dir,
            title = "Select dir")
        name = filedir
        self.src_file_name = name
        self.set_ctl_val("input.src_dir_name", name)


    def src_file_search(self):
        start_dir = self.src_dir
        filename =  filedialog.askopenfile("r",
            initialdir = start_dir,
            title = "Select file",
            filetypes = (("all files","*.*"), ("csrc files","*.csrc")))
        fullname = filename.name
        dir_name = os.path.dirname(fullname)
        base_name = os.path.basename(fullname)
        self.src_dir = dir_name
        self.set_ctl_val("input.src_dir", dir_name)
        self.src_file_name = base_name
        self.set_ctl_val("input.src_file_name", base_name)
        filename.close()
            
            
    def run_button(self):
        """ Called when our button is pressed
        """
        SlTrace.lg("run_button")
        self.start_continue()
        
        
    def start_continue(self):
        """ Start/continue program running
        """
        self.running = True
        
        while True:
            self.set_vals()
            if self.get_val("running.new_game"):
                if self.new_game is not None:
                    self.new_game()
            new_board = self.get_val_from_ctl("running.new_board")
            if new_board:
                if self.play_control is not None:
                    self.play_control.reset()
            src_file = self.get_val_from_ctl("input.src_file_name")
            if self.play_control is not None:
                res = self.play_control.run_file(src_file=src_file)
            else:
                res = self.run_file(src_file)
                
            if not res:
                SlTrace.lg("run file failed")
                return False       # Quit if run fails
            
            is_looping = self.get_val("running.loop") 
            if is_looping:
                loop_time = self.msec(self.get_val("running.loop_time"))
                SlTrace.lg("Looping after %d msec" % loop_time)
                self.mw.after(loop_time)
                continue
            self.running = False
            return True

    
    def run_file(self, src_file=None, cmd_execute=None):
        """ Run stream command file
        :src_file: source file name (absolute path or relative)
            If no extension: search for none, then supported extensions(.csrc, .py)
        :cmd_execute: function to call for each stcmd
        :returns: True iff OK run
        """
        if cmd_execute is not None:
            self.cmd_execute = cmd_execute
        self.command_stream.open(src_file=src_file)
        while True:
            stcmd = self.get_cmd()
            if stcmd is None:
                break
            if stcmd.is_type(SelectStreamCmd.EXECUTE_FILE):
                if not self.procFile(src_file=src_file):
                    raise SelectError("Error in procFile")
                continue        # Next cmd should be EOF
            cmd_delay =  self.msec(self.get_val("running.cmd_delay"))
            self.mw.after(cmd_delay)
            if stcmd.is_type(SelectStreamCmd.EOF):
                break
            if self.cmd_execute is not None:
                if not self.cmd_execute(stcmd):
                    raise SelectError("%s execute failure" % stcmd)

        return True
        

    def reset(self, src_file=None):
        """ Reset stream to allow traversing again
            closes current file, if any, reopen
            :src_file: new file name, if present default: use current name
        """
        self.command_stream.reset(src_file=src_file)


    def set_play_control(self, play_control):
        """ Connect command stream processing to game control
        :play_control:  game control
        """
        self.play_control = play_control        # Local reference
        self.command_stream.set_play_control(play_control)


    def set_cmd_stream_proc(self, cmd_stream_proc):
        """ Connect command stream processing to command processing
        :play_control:  game control
        """
        self.command_stream.set_cmd_stream_proc(cmd_stream_proc)



    def msec(self, time_sec):
        """ Convert time in seconds to time in msec
        :time_sec: time in seconds
        """
        time_msec = int(1000*time_sec)
        return time_msec
    

    def is_eof(self):
        """ Are we at end of file?
        """
        return self.command_stream.is_eof()
    
    def set_eof(self, eof=True):
        """ Set as eof
        """
        self.command_stream.set_eof(eof=eof)
        
        
    def is_src_lst(self):
        """ Are we listing source lines?
        """
        return self.command_stream.is_src_lst()

    def set_src_lst(self, lst=True):
        """ Are we listing source lines?
        :lst: Listing default: True
        """
        self.command_stream.set_src_lst(lst=lst)

    def is_stx_lst(self):
        """ Are we listing executing commands?
        """
        return self.command_stream.is_stx_lst()

    def set_stx_lst(self, lst=True):
        """ Are we listing execution lines?
        :lst: Listing default: True
        """
        self.command_stream.set_stx_lst(lst=lst)



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



    def destroy(self):
        """ Destroy window resources
        """
        if self.mw is not None:
            self.mw.destroy()
        self.mw = None


    
    
    def get_cmd(self):
        """ Get next command: word [[, ] word]* [EOL|;]
         ==> cmd.name == first word
             cmd.args == subsequent words
        :returns: cmd, None on EOF
        """
        return self.command_stream.get_cmd()




    def get_src_file_path(self):
        """ Get current source file path
        """
        return self.command_stream.get_src_file_path()
    

    
    def procFile(self, src_file=None, exe_command=None):
        """
        Process input files:
        :src_file: file input name default use stream_command's
            .py ==> python script
            .bwif ==> BlockWorld scrip
            default: use self.src_file_name
        :exe_command: command to execute for each stream command
        """
        return self.command_stream.procFile(src_file=src_file)

    def set_debugging(self, debugging=True):
        self.debugging=debugging

    
if __name__ == "__main__":
    import os
    import sys
    from tkinter import *    
    import argparse
    
    file = "one_square"
    run = False                     # Do we run file upon start
    src_lst = True                  # List source as run
    stx_lst = True                  # List Stream Trace cmd
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
    fC = SelectCommandFileControl(frame, title="Command Stream",
                     src_lst=src_lst,
                     stx_lst=stx_lst,
                     src_file=file, display=True)
    fC.set_debugging()
    if run:
        root.after(0, fC.run_file)
        
    root.mainloop()
    