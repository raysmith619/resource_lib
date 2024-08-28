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

import os
import select
import sys
from threading import Thread
import subprocess
import turtle as tur
from turtle import *

from wx_tk_rem_host import TkRemHost
from select_trace import SlTrace
from wx_canvas_grid import CanvasGrid
from wx_braille_cell_list import BrailleCellList
"""
External functions 
Some day may model after turtle's _make_global_funcs
"""
SlTrace.clearFlags()    # Start quiet
tkh = None
canvas = None
pdisplay = None

def setup_main(port=None):
    global tkh
    global canvas
    global pdisplay
    
    if canvas is None:
        canvas = tur.getcanvas()
    cg = CanvasGrid(base=canvas)
    #root.withdraw()
    cells = cg.get_cell_specs()  # gets (ix,iy,color)*
    cell_list = BrailleCellList(cells)  # converts either to BrailleCell
    bdlist = cell_list.to_string()
    if tkh is None:
        tkh = TkRemHost(canvas_grid=cg, port=port)
    src_dir = os.path.dirname(__file__)
    pdisplay = subprocess.Popen(f"python wx_display_main.py --bdlist {bdlist}"
                                f" --port_in={tkh.port_out}" # Reversed for user
                                f" --port_out={tkh.port_in}" # Reversed for user
                                 " --subprocess",
                    cwd=src_dir,
                    shell=True)

def mainloop(port=None):
    """ tk's mainloop
    :port: host socket port
    """

    global tkh
    global canvas
    
    if pdisplay is None:
        setup_main(port=port)
             
    def check_display():
        """ Check if display process exited
        Recheck after delay
        """
        rc = pdisplay.poll()
        if rc != None:
            SlTrace.lg(f"Subprocess exited with rc:{rc}")
            SlTrace.onexit()    # Close log
            os._exit(0)     # Stop all processes
            return
        tur.ontimer(check_display, 10)
        
    check_display()
    tur.mainloop()
    sys.exit(0)

snap_inc = 0        # Augment port
def snapshot(title, port=None):
    """ Create a TurtleBraille window with a "snapshot" of current turtle display
    :title: Title description default: generated
    """
    if pdisplay is None:
        setup_main(port=port)                # Create first window with current display
        return
    
    cg = CanvasGrid(base=canvas)
    cells = cg.get_cell_specs()  # gets (ix,iy,color)*
    cell_list = BrailleCellList(cells)  # converts either to BrailleCell
    bdlist = cell_list.to_string()
    tkh.snapshot(title=title, bdlist=bdlist)

    
def done(port=None):
    mainloop(port=port)

if __name__ ==  '__main__':
    colors = ["red","orange","yellow","green"]
    n = 0
    for colr in colors:
        n += 1
        width(40)
        color(colr)
        forward(200)
        right(90)
        if n == 1:
            snapshot(f"{n}: {colr}")
    #done()		    # Complete drawings
    