#braille_display_test2.py
from select_trace import SlTrace
from braille_display import BrailleDisplay

SlTrace.lg("BrailleDisplay Test braille_display_test2")
SlTrace.clearFlags()
#SlTrace.lg("\nAfter clearFlags")
#SlTrace.listTraceFlagValues()
SlTrace.setFlags("point")
import tkinter as tk

display_all = False          # Display all things - True overrides other settings
braille_window = True       # Create braille window
points_window = True        # Create window showing points
braille_print = True        # Print braille for figure 
print_braille_cells = False # Print braille cells
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
tests = ("goto")

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

    bw.pensize(20)
    bw.color("green")
    bw.forward(200)
    bw.right(90)
    bw.forward(200)
    bw.right(90)
    bw.forward(200)
    bw.right(90)
    bw.forward(200)

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
    bw.penup()
    bw.goto(-sz,sz)
    bw.pendown()
    if fill_color is not None:
        bw.begin_fill()
        bw.fillcolor(fill_color)
    side = 2*sz
    bw.setheading(0)
    bw.color("red")
    bw.forward(side)
    bw.color("orange")
    bw.right(90)
    bw.forward(side)
    bw.color("yellow")
    bw.right(90)
    bw.forward(side)
    bw.color("green")
    bw.right(90)
    bw.forward(side)
    if fill_color is not None:
        bw.fillcolor(fill_color)
        bw.end_fill()


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
    bw.color("green")
    bw.pendown()
    bw.goto(sz,sz)
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
    bw.speed("fastest")
    bw.width(10)
    bw.penup()
    bw.goto(bw.x_min+offset, bw.y_max-offset)
    bw.pendown()
    bw.color("red")
    bw.goto(bw.x_max-offset, bw.y_min+offset)
    bw.color("orange")
    bw.goto(bw.x_min+offset,bw.y_min+offset)
    bw.color("yellow")
    bw.goto(bw.x_min+offset, bw.y_max-offset)
    if do_snapshots:
        do_snapshot()


if "horz_line" in tests:
    if do_snapshots:
        setup_snapshot("a_horz_line")
    bw.speed("fastest")
    bw.width(10)
    sz = 200
    left = 200
    top = 100
    left = top = 0
    bw.penup()
    bw.color("red")
    bw.goto(left,top)
    bw.color("orange")
    bw.goto(sz/2,top)
    bw.color("green")
    bw.pendown()
    bw.goto(sz,top)
    bw.color("blue")
    bw.goto(2*sz,top)
    bw.color("indigo")
    bw.goto(3*sz,top)
    if do_snapshots:
        do_snapshot()
if "vert_line" in tests:
    if do_snapshots:
        setup_snapshot("a_vert_line")
    bw.pendown()
    bw.right(90)
    bw.color("red")
    bw.forward(sz/2)
    bw.color("blue")
    bw.forward(sz/2)
    if do_snapshots:
        do_snapshot()
if "diag_line" in tests:
    if do_snapshots:
        setup_snapshot("a_diag_line")
    bw.penup()
    bw.goto(-sz,sz)
    bw.color("green")
    bw.pendown()
    bw.goto(sz,-sz)
    if do_snapshots:
        do_snapshot()
if "triangle" in tests:
    for ft in ["","fill"]:
        if ft == "fill" and "NOFILL" in tests:
            continue # skip fill version
        
        if do_snapshots:
            setup_snapshot("triangle" " " + ft)
            bw.begin_fill()
        bw.penup()
        bw.goto(0,sz)
        bw.pendown()
        bw.pensize(wd)
        bw.color("red")
        bw.goto(sz,-sz)
        bw.color("green")
        bw.goto(-sz,-sz)
        bw.color("blue")
        bw.goto(0,sz)
        if ft == "fill":
            bw.fillcolor("dark gray")
            bw.end_fill()
        if do_snapshots:
            do_snapshot()
if "dot" in tests:
    if do_snapshots:
        setup_snapshot("a_dot")
    bw.dot(sz, color)
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
        bw.pensize(25)
        if ft == "fill":
            add_square("violet")
        else:
            add_square()
        bw.penup()
        bw.goto(0,dsz)
        if ft == "fill":
            bw.begin_fill()
        bw.pendown()
        bw.color("red")
        bw.goto(dsz,0)
        bw.color("orange")
        bw.goto(0,-dsz)
        bw.color("yellow")
        bw.goto(-dsz,0)
        bw.color("green")
        bw.goto(0,dsz)
        if ft == "fill":
            bw.fillcolor("indigo")
            bw.end_fill()
        if do_snapshots:
            do_snapshot()
bw.mainloop()      
