#wx_key_cmd_proc.py 30Jan2024  crs, Author
""" Process key commands
for AutioDrawWindow display
Provids a delay between commands to emulate physical
behavior.
The commands are placed in a queue which is emptied at
a suitable interval.  A separte thread is used to
allow the wx.App processing of events to support
display.
"""
import time
import threading as th
import queue
import wx

from select_trace import SlTrace


class KeyCmdProc:
    def __init__(self, win, key_press, dly=.2):
        """ Setup keyboard cmd processing
        :adw: AudioDrawWindow
        :dly: delay between actions in seconds
                default: .2
        """
        self.key_press = key_press  # key function to call
        self.dly = dly
        self._running = True # processing
        self._doing_command = False     # Not processing cmd
        self._awaiting = False  # True - awaiting callback 
        self.cmd_queue = queue.Queue()  # Command queue
        self.cmd_thread = th.Thread(target=self.thread_process)
        self.cmd_thread.start()
        
    def thread_process(self):
        """ Process cmds
        """
        while self._running:
            if not self.cmd_queue.empty():
                wx.CallAfter(self.delay_next_call)
            time.sleep(1.)
            
    def do_next_command(self):
        """ Process next command from queue, if one
        """
        SlTrace.lg("do_next_command", "cmd")
        self._doing_command = True
        self._awaiting = False
        if self.cmd_queue.empty():
            self._doing_command = False
            return      # Nothing to do
    
        cmd = self.cmd_queue.get()
        self.key_press(cmd)
        self._awaiting = True
        self._doing_command = False
        wx.CallAfter(self.delay_next_call)
    
    def delay_next_call(self):
        SlTrace.lg("delay_next_call", "cmd")
        wx.CallLater(int(self.dly*1000), self.do_next_command)

    def empty(self):
        """ Test if empty (no pending cmds)
        :returns: True iff queue is empty
        """
        return self.cmd_queue.empty()
    
    def stop(self, wait=True):
        """ Stop processing, end thread
        :wait: True wait till empty
                default: True
        """
        if wait:
            wx.CallAfter(self.stop_on_empty)
        else:
            self._running = False

    def stop_on_empty(self):
        """ Stop when empty
        """
        if self.cmd_queue.empty():
            self._running = False
            return
        
        wx.CallLater(100, self.stop_on_empty) 

    def put_key_cmd(self, cmd):
        """Place key cmd in queue to be processed
        """
        self.cmd_queue.put(cmd)
        if not self._awaiting and not self._doing_command:
            self.do_next_command()
            
if __name__ == '__main__':
    import time
    import wx
    
    app = wx.App()
    win = wx.Frame(None)
    win.Show()
    
    def test_1():
        print("Test Start")
            
        def key_press(ch):
            SlTrace.lg(f"key_press({ch})", "cmd_out")
            print(ch)
            
        kcp = KeyCmdProc(win, key_press=key_press, dly=.200)
        
        def key_str(key_str):
            """ Process string via kcp
            :key_str: character string to process
            """
            for ch in key_str:
                kcp.put_key_cmd(ch)

        ab = "abcdefghijklmnopqrstuvwxyz"
        ab = ab[:5]
        chs = ab + ab.upper() 
        key_str(chs)
        chs = chs[::-1]
        key_str(chs)
        wx.CallAfter(print, f"after key_str({chs})")
    
    #SlTrace.setFlags("cmd_out")    
    wx.CallAfter(test_1)
    
    app.MainLoop()