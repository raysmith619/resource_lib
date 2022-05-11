#braille_display_test2.py
from select_trace import SlTrace
from braille_display import BrailleDisplay

SlTrace.lg("BrailleDisplay Test")
SlTrace.clearFlags()
#SlTrace.lg("\nAfter clearFlags")
#SlTrace.listTraceFlagValues()

bw = BrailleDisplay()

braille_window = True       # Create braille window
points_window = True        # Create window showing points
braille_print = True        # Print braille for figure 
print_braille_cells = False # Print braille cells 
snapshots = True            # Take snapshot after each test
snapshot_clear = True       # Clear screen after snapshot

tests = ("simple_test, long_test"
    "horz_line, vert_line, diag_line"
    "triangle, dot, square, diamond")


if "simple_test" in tests:
    bw.pensize(20)
    bw.color("green")
    bw.forward(200)
    bw.right(90)
    bw.forward(200)
    bw.right(90)
    bw.forward(200)
    bw.right(90)
    bw.forward(200)


bwsn = None                 # Snapshot BrailleDisplay
bwsn_title = None
def setup_snapshot(title=None, keep_bw=False):
    global bw
    global bwsn
    global bwsn_title
    if not keep_bw or bwsn is None:
        
        bwsn = BrailleDisplay()
        bw = bwsn
    bwsn_title = title + " -"
    
def do_snapshot(clear_after=None):
    """ Take snapshot now
    """
    if clear_after is None:
        clear_after = snapshot_clear
    bw.display(title=bwsn_title,
               braille_window=braille_window,
               points_window=points_window,
               braille_print=braille_print,
               print_cells=print_braille_cells)
        
        
if SlTrace.trace("cell"):
    SlTrace.lg("cell limits")
    for ix in range(len(bw.cell_xs)):
        SlTrace.lg(f"ix: {ix} {bw.cell_xs[ix]:5}")
    for iy in range(len(bw.cell_ys)):
        SlTrace.lg(f"iy: {iy} {bw.cell_ys[iy]:5}")
    
sz = 350
color = "purple"
wd = 2
do_fill = True          # Fill where applicable

a_horz_line = True
#a_horz_line = False

a_vert_line = True
#a_vert_line = False

a_diag_line = True
#a_diag_line = False

a_triangle = True
#a_triangle = False

a_dot = True
#a_dot = False

a_square = True
#a_square = False

a_diamond = True
#a_diamond = False

def add_square(fill_color=None):
    """ Simple colored square
    :fill_color: fill color
                default: don't fill
    """
    if fill_color is not None:
        bw.begin_fill()
        bw.fillcolor(fill_color)
    bw.penup()
    bw.goto(-sz,sz)
    bw.pendown()
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
        bw.end_fill()


if a_horz_line:
    if snapshots:
        setup_snapshot("a_horz_line")
    bw.penup()
    bw.pensize(wd)
    bw.goto(-sz, sz)
    bw.pendown()
    bw.goto(sz,sz)
    if snapshots:
        do_snapshot()
if a_vert_line:
    if snapshots:
        setup_snapshot("a_vert_line")
    bw.penup()
    bw.goto(sz,sz)
    bw.color("red")
    bw.pendown()
    bw.right(90)
    bw.forward(2*sz)
    if snapshots:
        do_snapshot()
if a_diag_line:
    if snapshots:
        setup_snapshot("a_diag_line")
    bw.penup()
    bw.goto(-sz,sz)
    bw.color("green")
    bw.pendown()
    bw.goto(sz,-sz)
    if snapshots:
        do_snapshot()
if a_triangle:
    if snapshots:
        setup_snapshot("a_triangle")
    if do_fill:
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
    if do_fill:
        bw.end_fill()
    if snapshots:
        do_snapshot()
if a_dot:
    if snapshots:
        setup_snapshot("a_dot")
    bw.dot(sz, color)
    if snapshots:
        do_snapshot()
    
if a_square:
    if snapshots:
        setup_snapshot("a_square")
    if do_fill:
        bw.fillcolor("violet")
        bw.begin_fill()
    add_square()
    if snapshots:
        do_snapshot()
    if do_fill:
        bw.end_fill()

if a_diamond:
    dsz = .7 * sz
    bw.pensize(25)
    if snapshots:
        setup_snapshot("diamond in square")
    if do_fill:
        bw.fillcolor("yellow")
        bw.begin_fill()
    add_square()
    bw.penup()
    bw.goto(0,dsz)
    bw.pendown()
    bw.color("red")
    bw.goto(dsz,0)
    bw.color("orange")
    bw.goto(0,-dsz)
    bw.color("yellow")
    bw.goto(-dsz,0)
    bw.color("green")
    bw.goto(0,dsz)
    if do_fill:
        bw.end_fill()
    if snapshots:
        do_snapshot()

if not snapshots:
    bw.display(braille_window=braille_window, braille_print=braille_print,
               print_cells=print_braille_cells,
               points_window=points_window)
bw.mainloop()      
