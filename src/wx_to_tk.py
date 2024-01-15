#wx_to_tk.py    01Jan2024  crs Author
""" 
Communication between turtle/tkinter window display and
wxPython AudioDisplayWindow(s)
"""
import time
import multiprocessing as mp
import turtle as tur
from select_trace import SlTrace

if __name__ == "__main__":
    mp.freeze_support()

class WxToTk:
    def __init__(self, qlen=4):
        """ Setup communication between base process and
        new process.
        """
        self.qlen = qlen
        self.started = False
    
    def startup(self):
        self.proc = mp.Process(target=self.wx_proc)
        self.cmd_queue = mp.Queue(self.qlen)      # Commands from new process
        self.cmd_resp_queue = mp.Queue(self.qlen)
        if not self.started:
            self.proc.start()

    def wx_proc(self):
        import wx
        if self.started:
            return
        self.started = True
        self.app = wx.App()
        from wx_braille_display import BrailleDisplay
        bd = BrailleDisplay(wx_to_tk=self)
        bd.display()
        self.app.MainLoop()
        
    def done(self):
        tur.done()

if __name__ == "__main__":
    SlTrace.lg(f"Starting up {__name__}")
    import time
    wxtk = WxToTk()
    tur.forward(100)
    wxtk.startup()
    wxtk.done()
 