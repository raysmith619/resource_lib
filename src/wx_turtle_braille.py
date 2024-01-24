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
import sys
from threading import Thread
import subprocess
import turtle as tur
from turtle import *
import tkinter as tk

from pipe_to_queue import PipeToQueue
from select_trace import SlTrace
from tk_canvas_grid import TkCanvasGrid
from wx_braille_cell_list import BrailleCellList
"""
External functions 
Some day may model after turtle's _make_global_funcs
"""


def mainloop():
    root = tk.Tk()
    
    canvas = getcanvas()
    cg = TkCanvasGrid(root,base=canvas)
    root.withdraw()
    cells = cg.get_display_cells()  # gets (ix,iy,color)*
    cell_list = BrailleCellList(cells)  # converts either to BrailleCell
    bdlist = cell_list.to_string()
    import os
    src_dir = os.path.dirname(__file__)
    pdisplay = subprocess.Popen(f"python wx_display_main.py --bdlist {bdlist}"
                                 " --subprocess",
                    #stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    cwd=src_dir,
                    shell=True)

    sto = PipeToQueue(pdisplay.stdout)
             
    def check_display():
        """ Check if display process exited
        Recheck after delay
        """
        rc = pdisplay.poll()
        if rc != None:
            SlTrace.lg(f"Subprocess exited with rc:{rc}")
            sto.stop()      # stop reading stdout pipe
            SlTrace.onexit()    # Close log
            os._exit(0)     # Stop all processes
            return
        
        output = sto.get()
        if output != "":
            SlTrace.lg(output)
        root.after(10, check_display)
        
    check_display()
    root.mainloop()
    sys.exit(0)
    
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
    