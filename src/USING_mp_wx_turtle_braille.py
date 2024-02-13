#wx_turtlel_braille.py       02Nov2023  crs from turtle_braille.property
#                           27Feb2023  crs from turtle_braille.py
#                           21Feb2023  crs  From turtle_braille.py
#                           16Apr2022  crs  Author
"""
# Using tk.Canvas scanning
Turtle augmented with braille graphics output
__main__ : main process: tkinter display support via done()

else: multiprocessing process:
    Create braille output 
    Create/control wxPython display AudioDrawWindow
    
"""

import os
import select
import multiprocessing as mp
import sys
from threading import Thread
import subprocess
import turtle as tur
from turtle import *
import tkinter as tk

from pipe_to_queue import PipeToQueue
from wx_tk_rem_host import TkRemHost
from select_trace import SlTrace
from tk_canvas_grid import TkCanvasGrid
from wx_braille_cell_list import BrailleCellList
"""
External functions 
Some day may model after turtle's _make_global_funcs
"""
wx_proc_fun_p = None
def mainloop():
    from wx_braille_display import BrailleDisplay
    
    root = tk.Tk()
    canvas = getcanvas()
    cg = TkCanvasGrid(root,base=canvas)
    root.withdraw()
    cells = cg.get_display_cells()  # gets (ix,iy,color)*
    cell_list = BrailleCellList(cells)  # converts either to BrailleCell
    bdlist = cell_list.to_string()
    global bd
    bd = BrailleDisplay(display_list=bdlist)
    
    #
    # wxPython process's function
    #
    global wx_proc_fun_p
    def wx_proc_fun():
        import wx
        app = wx.App()
        bd.display()
        app.MainLoop()

    if __name__ ==  '__main__':
        wx_proc_fun_p  = wx_proc_fun    
        wx_process = mp.Process(target=wx_proc_fun_p)
        wx_process.start()
        root.mainloop()
    
def done():
    mainloop()

if __name__ ==  '__main__':
    mp.freeze_support()
    colors = ["red","orange","yellow","green"]

    for colr in colors:
        width(40)
        color(colr)
        forward(200)
        right(90)
    done()		    # Complete drawings
    