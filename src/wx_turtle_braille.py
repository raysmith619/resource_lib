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
import tkinter as tk
import turtle as tur
from turtle import *

from wx_tk_rpc_host import TkRPCHost
from select_trace import SlTrace
from wx_canvas_grid import CanvasGrid
from wx_braille_cell_list import BrailleCellList
"""
External functions 
Some day may model after turtle's _make_global_funcs
"""
SlTrace.clearFlags()    # Start quiet
tkh = None
root = tk.Tk()
root.withdraw()     # Hide tk window
canvas = None
pdisplay = None

def setup_main(title=None, port=None):
    global tkh
    global canvas
    global pdisplay
    
    if canvas is None:
        canvas = tur.getcanvas()
    cg = CanvasGrid(base=canvas)
    cells = cg.get_cell_specs()
    SlTrace.lg(f"\nsetup_main: cells:{cells}", "cell_specs")
    #root.withdraw()
    if tkh is None:
        tkh = TkRPCHost(canvas_grid=cg, root=root,host_port=port)
    src_dir = os.path.dirname(__file__)
    title = title.replace(" ", "_")
    pdisplay = subprocess.Popen(f"python wx_display_main.py"
                                f" --title {title}"
                                f" --host_port={tkh.host_port}"
                                 " --subprocess",
                    cwd=src_dir,
                    shell=True)
    check_display()
    tkh.wait_for_user()     # Wait till setup, possibly snapshot is done

n_check = 0
def mainloop(title=None, port=None):
    """ tk's mainloop
    :port: host socket port
    """

    global tkh
    global canvas
    
    if pdisplay is None:
        setup_main(title=title, port=port)
    tur.mainloop()
             
def check_display():
    """ Check if display process exited
    Recheck after delay
    """
    global n_check
    if pdisplay is None:
        return              # Start checking when launched
    
    n_check += 1
    rc = pdisplay.poll()
    #SlTrace.lg(f"check_display: {n_check}")
    if rc != None:
        SlTrace.lg(f"Subprocess exited with rc:{rc}")
        root.destroy()
        SlTrace.onexit()    # Close log
        os._exit(0)     # Stop all processes
        return
    tur.ontimer(check_display, 1000)
    #tur.ontimer(check_display, 10)
        
#tur.mainloop()
#sys.exit(0)

snap_inc = 0        # Augment port
def snapshot(title=None, port=None):
    """ Create a TurtleBraille window with a "snapshot" of current turtle display
    :title: Title description default: generated
    """
    SlTrace.lg(f"snapshot title={title} port={port}")
    if pdisplay is None:
        setup_main(title="Setup for snapshots", port=port)                # Create first window with current display
    tkh.snapshot(title=title)

    
def done(port=None):
    mainloop(title="done", port=port)

if __name__ ==  '__main__':
    colors = ["red","orange","yellow","green"]
    n = 0
    for colr in colors:
        n += 1
        width(40)
        color(colr)
        forward(200)
        right(90)
        #if n in [1,2,3,4]:
        if n in []:
            snapshot(f"{n}: {colr}")
    done()		    # Complete drawings
    
    