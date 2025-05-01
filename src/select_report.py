# select_report.py    13Mar2020  crs from http://effbot.org/tkinterbook/tkinter-dialog-windows.htm

"""
Report to user with a modeless message
"""
from tkinter import Tk, Label, Frame
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
        self.initial_focus = master
        ###super().__init__(master_focus, title=title, grab_set=grab_set)   # TFD remove grab_set
        super().__init__(master_focus, title=title)
        
    def body(self, master):

        Label(master, text=self.message).grid(row=0)
        return self.initial_focus # initial focus

if __name__ == "__main__":

    root = Tk()


    ###SelectReport(root, message="SelectReport Testing")
    SelectReport(message="SelectReport Testing Stanalone")
