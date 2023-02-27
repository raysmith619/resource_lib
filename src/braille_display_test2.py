#braille_display_test2.py

import tkinter as tk
import turtle as tur

from select_trace import SlTrace
from braille_display import BrailleDisplay

display_all = False          # Display all things - True overrides other settings
braille_window = True       # Create braille window
points_window = True        # Create window showing points
points_window = False
braille_print = True        # Print braille for figure 
print_braille_cells = False # Print braille cells
print_braille_cells = True # Print braille cells
tk_items = False            # Display tkinter objs
do_snapshots = True         # Do setup and do shapshot
do_simple_test = False      # Do simple test
do_long_test = True         # do long tests
snapshot_clear = True       # Clear screen after snapshot


"""
simple_test - do simple test(s)
NOFILL - suppress fill test versions, else do fill after
 non-fill
"""

tests = (
    "simple_test,"
    "goto, "
    "horz_line, vert_line, diag_line,"
    "triangle, dot, square, diamond"
    )

tk_items = True
#tests = "snapshots diagz_line" 
#tests = "snapshots square"
#tests = "snapshots goto"


#tests = ("vert_ line, horz_line")
#tests = ("simple_test")
#tests = ("goto")
#tests = "simple_tests"
if "simple_test" in tests:
    do_simple_test = True 
if "no_long_test" in tests:
    do_long_test = False 
elif "do_long_test" in tests:
    do_long_test = True 
            
SlTrace.lg(f"\ntests: {tests}")
main_mw = tk.Tk()
main_mw.title("BrailleDisplay Tests")
main_mw.geometry("800x800")
main_canvas = tk.Canvas(main_mw)
main_canvas.pack(expand=1, fill='both')

if do_simple_test:
    bw = BrailleDisplay(title="braille_display test")

    tur.pensize(10)
    tur.color("red")
    tur.forward(200)
    tur.right(90)
    tur.color("orange")
    tur.forward(200)
    tur.right(90)
    tur.color("yellow")
    tur.forward(200)
    tur.right(90)
    tur.color("green")
    tur.forward(200)

    bw.display(braille_window=braille_window, braille_print=braille_print,
               print_cells=print_braille_cells,
               points_window=points_window,
               tk_items=tk_items)


bwsn = None                 # Snapshot BrailleDisplay
bwsn_title = None
def setup_snapshot(title=None, keep_bw=False):
    global bw
    global bwsn
    global bwsn_title
    if not keep_bw or bwsn is None:
        
        bwsn = BrailleDisplay(title=title)
        bw = bwsn
        #bw.reset()      # Note only one screen
        
    bwsn_title = title + " -"
    
def do_snapshot():
    """ Take snapshot now
    """
    bw.display(title=bwsn_title,
               braille_window=braille_window,
               points_window=points_window,
               braille_print=braille_print,
               print_cells=print_braille_cells,
               tk_items=tk_items)
        
        
if SlTrace.trace("cell"):
    SlTrace.lg("cell limits")
    for ix in range(len(bw.cell_xs)):
        SlTrace.lg(f"ix: {ix} {bw.cell_xs[ix]:5}")
    for iy in range(len(bw.cell_ys)):
        SlTrace.lg(f"iy: {iy} {bw.cell_ys[iy]:5}")
    
sz = 350
color = "purple"
wd = 2

def add_square(fill_color=None):
    """ Simple colored square
    :fill_color: fill color
                default: don't fill
    """
    tur.penup()
    tur.goto(-sz,sz)
    tur.pendown()
    if fill_color is not None:
        tur.begin_fill()
        tur.fillcolor(fill_color)
    side = 2*sz
    tur.setheading(0)
    tur.color("red")
    tur.forward(side)
    tur.color("orange")
    tur.right(90)
    tur.forward(side)
    tur.color("yellow")
    tur.right(90)
    tur.forward(side)
    tur.color("green")
    tur.right(90)
    tur.forward(side)
    if fill_color is not None:
        tur.fillcolor(fill_color)
        tur.end_fill()


"""
                                TESTS
        Chosen by string(s) in tests variable
        "no_long_test" - force no long tests default: do long tests
        "no_snapshots" - suppress snapshots  default: do snapshots for long tests
        
"""

do_snapshots = not "no_snapshots" in tests

if "diagz_line" in tests:
    # Simple right to up diagonal from initial point(0,0)
    if do_snapshots:
        setup_snapshot("a_diagz_line")
    tur.color("green")
    tur.pendown()
    tur.goto(sz,sz)
    if do_snapshots:
        do_snapshot()
        
if "goto" in tests:
    """
    y
    yr
    y r
    y  r
    y   r
    y    r
    ooooooo
    """
    
    offset = 25      # offset from edge
    if do_snapshots:
        setup_snapshot("goto")
    tur.speed("fastest")
    tur.width(10)
    tur.penup()
    tur.goto(bw.x_min+offset, bw.y_max-offset)
    tur.pendown()
    tur.color("red")
    tur.goto(bw.x_max-offset, bw.y_min+offset)
    tur.color("orange")
    tur.goto(bw.x_min+offset,bw.y_min+offset)
    tur.color("yellow")
    tur.goto(bw.x_min+offset, bw.y_max-offset)
    if do_snapshots:
        do_snapshot()


if "horz_line" in tests:
    if do_snapshots:
        setup_snapshot("a_horz_line")
    tur.speed("fastest")
    tur.width(10)
    sz = 200
    left = 200
    top = 100
    left = top = 0
    tur.penup()
    tur.color("red")
    tur.goto(left,top)
    tur.color("orange")
    tur.goto(sz/2,top)
    tur.color("green")
    tur.pendown()
    tur.goto(sz,top)
    tur.color("blue")
    tur.goto(2*sz,top)
    tur.color("indigo")
    tur.goto(3*sz,top)
    if do_snapshots:
        do_snapshot()
if "vert_line" in tests:
    if do_snapshots:
        setup_snapshot("a_vert_line")
    tur.pendown()
    tur.right(90)
    tur.color("red")
    tur.forward(sz/2)
    tur.color("blue")
    tur.forward(sz/2)
    if do_snapshots:
        do_snapshot()
if "diag_line" in tests:
    if do_snapshots:
        setup_snapshot("a_diag_line")
    tur.penup()
    tur.goto(-sz,sz)
    tur.color("green")
    tur.pendown()
    tur.goto(sz,-sz)
    if do_snapshots:
        do_snapshot()
if "triangle" in tests:
    for ft in ["","fill"]:
        if ft == "fill" and "NOFILL" in tests:
            continue # skip fill version
        
        if do_snapshots:
            setup_snapshot("triangle" " " + ft)
            tur.begin_fill()
        tur.penup()
        tur.goto(0,sz)
        tur.pendown()
        tur.pensize(wd)
        tur.color("red")
        tur.goto(sz,-sz)
        tur.color("green")
        tur.goto(-sz,-sz)
        tur.color("blue")
        tur.goto(0,sz)
        if ft == "fill":
            tur.fillcolor("dark gray")
            tur.end_fill()
        if do_snapshots:
            do_snapshot()
if "dot" in tests:
    if do_snapshots:
        setup_snapshot("a_dot")
    tur.dot(sz, color)
    if do_snapshots:
        do_snapshot()
    
if "square" in tests:
    for ft in ["","fill"]:
        if ft == "fill" and "NOFILL" in tests:
            continue # skip fill version

        if do_snapshots:
            setup_snapshot("square" " " + ft)
        if ft == "fill":
            add_square("violet")
        else:
            add_square()
        if do_snapshots:
            do_snapshot()

if "diamond" in tests:
    for ft in ["","fill"]:
        if ft == "fill" and "NOFILL" in tests:
            continue # skip fill version

        if do_snapshots:
            setup_snapshot("diamond in square" " " + ft)
        dsz = .7 * sz
        tur.pensize(25)
        if ft == "fill":
            add_square("violet")
        else:
            add_square()
        tur.penup()
        tur.goto(0,dsz)
        if ft == "fill":
            tur.begin_fill()
        tur.pendown()
        tur.color("red")
        tur.goto(dsz,0)
        tur.color("orange")
        tur.goto(0,-dsz)
        tur.color("yellow")
        tur.goto(-dsz,0)
        tur.color("green")
        tur.goto(0,dsz)
        if ft == "fill":
            tur.fillcolor("indigo")
            tur.end_fill()
        if do_snapshots:
            do_snapshot()
SlTrace.lg("End of Test")
#tur.mainloop()      
