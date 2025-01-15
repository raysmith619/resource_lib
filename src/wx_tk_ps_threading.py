# wx_tk_ps_threading.py 18Oct2024  crs, Author
""" 
Pseudo Thread for tkinter environment
to  avoid executing tkinter operations outside the main thread
Thread process will be executed via root.after()
"""
import tkinter as tk
import threading as th

class TkPsThread:
    def __init__(self, root, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None):
        """ Mimic thread within tkinter environment
        :root: tkinter window
        :group: IGNORED
        :taret: function to run in background
        :name: IGNORED
        :args: target's positional arguments
        :kwargs: IGNORED
        :daemon: IGNORED
        """
        self.root = root
        self.group = group
        self.target = target
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.daemon = daemon
        self.thread = th.Thread(group=group, name=name, args=args, kwargs=kwargs, daemon=daemon)
        
    def start(self):
        """ start target function
        """
        self.root.after(0, self.target.start)