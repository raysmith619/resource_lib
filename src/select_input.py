# select_input.py    13Mar2020  crs
# from http://effbot.org/tkinterbook/tkinter-dialog-windows.htm

"""
Facilitate input / re-input with a modeless message
"""
from tkinter import Tk, Entry, Label, messagebox

from select_error import SelectError
from select_error_input import SelectErrorInput
from select_trace import SlTrace
from crs_funs import str2val

import tkSimpleDialog

class SelectInput(tkSimpleDialog.Dialog):

    def __init__(self, master=None, title=None, message=None, default=None, grab_set=False):
        """ Get input, validate format
        :master: master window,
        :title: window title
        :message: message for input
        :default: input default val/type
        :grab_set: True - grab events
        """
        self.master = master
        self.message = message
        if default is None:
            raise SelectError("Required default parameter is missing")
        
        self.default = default
        self.standalone = False
        if master is not None and hasattr(master, "tk"):
            master_focus = master
        elif master is not None and hasattr(master, "mw"):
            master_focus = master.mw
        else:
            master_focus = Tk()
            self.standalone = True
            master_focus.withdraw()               # Hide base window
        self.initial_focus = master_focus
        ###super().__init__(master_focus, title=title, grab_set=grab_set)
        super().__init__(master_focus, title=title)
        
    def body(self, master):

        Label(master, text=self.message).grid(row=0)
        Label(master, text="ENTER:").grid(row=1)
        self.e1 = Entry(master)
        self.e1.grid(row=1, column=1)
        return self.e1 # initial focus

    def validate(self):
        val_str = self.e1.get()
        try:
            self.result = str2val(val_str, self.default)
            return 1
        
        except SelectErrorInput:
            messagebox.showwarning(
                "Bad input",
                f"Illegal values {val_str}, please try again"
            )
            return 0
        
if __name__ == "__main__":
    
    root = Tk()


    si = SelectInput(root, message="SelectReport Testing", default=0)
    val = si.result
    SlTrace.lg(f"val = {val}")    
