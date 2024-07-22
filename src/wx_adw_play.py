#wx_adw_play.py 17Jul2024  crs, Author
"""
Support "playing a sequence of test operations into Display/AudioDrawWindow
wxPython uses the paradyme where control is held by app.mainloop() and user
actions are done via events.  Much of testing is done through a series of
actions.  The code here generates a series of events which executes a list
of code snipits.  A code snipit is
    1. A set of lines preceeded by LINE_MARKER and followed by LINE_MARKER
        OR
    2. One line
The process:
    Setup access to code snipits
    Setup callLater: proc_part
    start wx.MainLoop
    
    proc_part:
        execute part
        if part_list empty:
            wx.App.ExitMainLoop()
        else:
            CallLater(proc_part, appropriate_delay)
        
    
"""

import wx
import re
import time

from select_control import SlTrace

class AdwPlay:
    
    def __init__(self, bd, app=None, frame=None, time_inc=0,
                trace=0,
                line_marker="~",
                globals=None,
                locals=None):
        """ Setup pgm of one-line snipits
        :bd: test object
        :app: app basis
            default: created
        :frame: frame basis
                default: create non-shown frame so
                        Main
        :time_inc: time to sweparate snipit execution
            default: no additional time
        :trace: 1 - list source code for each piece
                default: no listing
        :line_marker: code sequence delimiter
                default: "~"
        :globals: globals dictionary passed to exec
        :locals: locals dictionary passed to exec
        """
        self.bd = bd
        if app is None:
            self.standalone = True
            app = wx.App()
        else:
            self.standalone = False
        self.app = app
        if frame is None:
            frame = wx.Frame(None, title="So MainLoop() works")
        self.frame = frame
        self.time_inc = time_inc
        self.trace = trace
        self.line_marker = line_marker
        if globals is None:
            globals = {}
        globals['pause'] = self.pause       # Add in builtin functions
        globals['SlTrace'] = SlTrace
        self.globals = globals
        self.locals = locals
        self.pause_time = None                   # Onetime add to time_inc
                                            # to implement pause() function
        
    def play_pgm(self, pgm):
        """ Play pgm snipits
        :pgm: string, whose lines are to be played
        """
        self.icurrent = 0
        self.parts = pgm.split("\n")
        wx.CallLater(int(self.time_inc*1000), self.play_part)
        if self.standalone:
            self.app.MainLoop()

    def get_next_part(self):
        """ Get next pgm part
        :returns:  pgm string, None if no part left
        """
        piece = ""      # In case no code
        while self.icurrent < len(self.parts):
            piece = self.parts[self.icurrent]
            if re.match(r'^\s*$', piece):
                self.icurrent += 1
                continue            # Ignore blank lines
            break                   # Non-blank line
        
        if piece == "" and self.icurrent >= len(self.parts):
            return None
        
        self.indent = indent = len(piece) - len(piece.lstrip()) # demand spaces                
        multi_line = False
        parts = []
        lm_str = self.line_marker
        if piece[indent:] == lm_str:
            multi_line = True
            self.icurrent += 1
        
        self.line_no = self.icurrent     # index has been incremented 
        while self.icurrent < len(self.parts):
            piece = self.parts[self.icurrent]            
            self.icurrent += 1
            if multi_line and piece[indent:] == lm_str:
                break       # End of multi-line part
            
            parts.append(piece[indent:])
            if not multi_line:
                break       # End of single line part
            
        return "\n".join(parts) + "\n"

    def pause(self, time_inc):
        """ Pause play, giving rest of activity time to continue
            ONLY functions within play_pgm
        :time_inc: time in seconds
        """
        print(f"TFD: pause({time_inc})")
        self.pause_time = time_inc
                
    def play_part(self):
        """ Play next part
        """
        if self.pause_time is not None:
            wx.CallLater(int(1000*self.pause_time), self.play_part)
            self.pause_time = None  # Clear pausing
            return
        
        part = self.get_next_part()
        if part is None:
            if self.standalone:
                self.app.ExitMainLoop()
            return
        if self.trace > 0:
            print(f"""{self.line_no}:{" "*self.indent}{part}""")
        exec(part, self.globals, self.locals)
        wx.CallLater(0, self.play_part)
        
if __name__ == "__main__":
    SlTrace.setFlags("stdouthasts=True")
    trace = 1   # 1 - list source code
    print("Test Begin")
    aP = AdwPlay(bd=None, time_inc=1, trace=trace)
    pgm_str = """
        # single line
        print(1)
        print(2)
        ~
        pause_time = 10
        SlTrace.lg(f"Pausing for {pause_time} seconds")
        ~
        pause(pause_time)
        SlTrace.lg("after pausing")
        ~
        # Multiline code follows
        print("Multiline code")
        for n in range(1,5+1):
            print("*"*n)
        ~
        print(3);print(4)
        """

    aP.play_pgm(pgm_str)
        
    print("End of Test")
