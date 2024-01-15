#wx_braille_display_link.py 05Jan2023  crs, from display.py
""" Link between turtle/tk process and wxPython display process
"""
import multiprocessing as mp
import time
import tkinter as tk

from select_trace import SlTrace
from braille_error import BrailleError
from wx_braille_display import BrailleDisplay 


class WxCommand:
    """ Command from wx display to tk window process
    """
    GET_DISPLAY_CELLS =  1
    
    def __init__(self, cmd, **kwargs):
        self.cmd = cmd
        for kwarg in kwargs:
            self[kwarg] = kwargs[kwarg]

class WxCommandResp(WxCommand):
    """ Command from wx display to tk window process
    """
    def __init__(self, cmd, **kwargs):
        self.cmd = cmd
        super().__init__(**kwargs)

def wx_proc_proc():
    """ wx display process's function
    """
    import wx
    app = wx.App()
    bd = BrailleDisplay()
    bd.display()
    app.MainLoop()
            
class BrailleDisplayLink:
    """ Create and display graphics using Braille
    """
    def __init__(self):
        """ Setup procesing process
        """
        root =  tk.Tk()
        self.root = root
        qlen = 4
        self.wx_proc = mp.Process(target=wx_proc_proc)
        self.wx_cmd_queue = mp.Queue(qlen)      # Commands from wx display to tk
        self.wx_cmd_resp_queue = mp.Queue(qlen)
        self.wx_proc.start()
        SlTrace.lg("After wx_proc.start()")
        self.wx_cmd_checking()  # continues
        self.root.mainloop()
            

    def wx_cmd_proc(self, wx_cmd):
        """ Process request cmd
        :wx_cmd: command such as canvas contents        
        """
        if wx_cmd.cmd == WxCommand.GET_DISPLAY_CELLS:
            display_cells = self.get_display_cells(**wx_cmd.kwargs)
            wx_cmd_resp = WxCommandResp(cmd=wx_cmd.cmd,
                                        display_cells=display_cells)
            self.wx_cmd_resp_queue.put(wx_cmd_resp)
        else:
            raise BrailleError(f"Unrecognized WxCommand {wx_cmd.cmd}")
            
    def wx_cmd_checking(self):
        """
        Check for and respond to any requests
        Recall after a bit
        """
        while self.wx_cmd_queue.qsize() > 0:
            wx_cmd = self.wx_cmd_queue.get()
            self.wx_cmd_proc(wx_cmd)        
        self.root.after(10, self.wx_cmd_checking)
        

    ############################# wx access to tk window ###################
    def tk_get_display_cells(self, **kwargs):
        """ Get braille cells
        :**kwargs: xmin, ymin, xmax,  ypax, ncols, nrows
        :returns: 
        """
        wx_cmd = WxCommand(WxCommand.GET_DISPLAY_CELLS,
                           **kwargs)
        wx_resp = self.send_wx_cmd(wx_cmd)
        return wx_resp.display_cells
        
    def send_wx_cmd(self, wx_cmd, wait=True):
        """ Send cmd 
        :wx_cmd: WxCommand  to send
        :wait: True - wait for and return response
        :returns: WxCommandResp return
        """
        self.wx_cmd_queue.put(wx_cmd)
        if wait:
            wx_cmd_resp = self.wx_cmd_resp_queue.get()
            return wx_cmd_resp
        
        return
        
    
    """ Turtle "Shaddow" Functions
    """
    def mainloop(self):
        self.do_displays()
                
    def done(self):
        self.mainloop()

    # Special functions
    def set_blank(self, blank_char):
        """ Set blank replacement
        :blank_char: blank replacement char
        :returns: previous blank char
        """
        ret = self.blank_char
        self.blank_char = blank_char
        return ret

if __name__ == "__main__":
    bdl = BrailleDisplayLink()
    