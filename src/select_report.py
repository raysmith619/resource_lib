# select_report.py    13Mar2020  crs from http://effbot.org/tkinterbook/tkinter-dialog-windows.htm

"""
Report to user with a modeless message
"""
from tkinter import Tk, Label
import tkSimpleDialog

class SelectReport(tkSimpleDialog.Dialog):

    def __init__(self, master=None, title=None, message=None, grab_set=False):
        self.master = master
        self.message = message
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
        super().__init__(master_focus, title=title, grab_set=grab_set)
        
    def body(self, master):

        Label(master, text=self.message).grid(row=0)
        return self.initial_focus # initial focus

if __name__ == "__main__":

    root = Tk()


    d = SelectReport(root, message="SelectReport Testing")
