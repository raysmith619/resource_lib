# select_dialog.py    13Mar2020  crs from http://effbot.org/tkinterbook/tkinter-dialog-windows.htm


import tkSimpleDialog

class SelectDialog(tkSimpleDialog.Dialog):

    def body(self, master):

        Label(master, text="First:").grid(row=0)
        Label(master, text="Second:").grid(row=1)

        self.e1 = Entry(master)
        self.e2 = Entry(master)

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        return self.e1 # initial focus

    def apply(self):
        first = int(self.e1.get())
        second = int(self.e2.get())
        print(f"first={first}, second={second}")

if __name__ == "__main__":
    from tkinter import *

    root = Tk()


    d = SelectDialog(root)
    print(f"d={d.result}")