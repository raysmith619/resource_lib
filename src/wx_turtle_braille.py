#wx_turtle_braille.py       02Nov2023  crs from turtle_braille.property
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
import subprocess
import turtle as tur
from turtle import *
import tkinter as tk

from tk_canvas_grid import TkCanvasGrid
from wx_braille_cell_list import BrailleCellList
"""
External functions 
Some day may model after turtle's _make_global_funcs
"""


def mainloop():
    root = tk.Tk()
    
    canvas = getcanvas()
    cg = TkCanvasGrid(None,base=canvas)
    cells = cg.get_display_cells()  # gets (ix,iy,color)*
    cell_list = BrailleCellList(cells)  # converts either to BrailleCell
    bdlist = cell_list.to_string()
    import os
    src_dir = os.path.dirname(__file__)
    os.chdir(src_dir)
    subprocess.Popen(f"python wx_display_main.py --bdlist {bdlist}", shell=True)     
    #tur.done()
    root.mainloop()
    
def done():
    mainloop()

if __name__ ==  '__main__':
    colors = ["red","orange","yellow","green"]

    for colr in colors:
        width(40)
        color(colr)
        forward(200)
        right(90)
    done()		    # Complete drawings
    