# turtle_braille_test.py    24Apr2022  crs, first test
from turtle_braille import *

tests = ("simple_test, long_test"
    "horz_line, vert_line, diag_line"
    "triangle, dot, square, diamond")


if "simple_test" in tests:
    pensize(20)
    color("green")
    forward(200)
    right(90)
    forward(200)
    right(90)
    forward(200)
    right(90)
    forward(200)
#done() # moved to end
    
if "long_test" in tests:
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
    
    bwsn = None                 # Snapshot BrailleDisplay
    bwsn_title = None
    def setup_snapshot(title=None, keep_bw=False):
        global bw
        global bwsn
        global bwsn_title
        if not keep_bw or bwsn is None:
            
            bwsn = BrailleDisplay()
            bw = bwsn
        bwsn_title = title + " -"   # Add descriptive suffix
        
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
        
    sz = 300
    color = "purple"
    wd = 50

    def add_square():
        """ Simple colored square
        """
        nsz = sz * 1.2       # Local enlargement
        bw.penup()
        bw.goto(-nsz,nsz)
        bw.pendown()
        side = 2*nsz
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

    
    if "horz_line" in tests:
        if snapshots:
            setup_snapshot("a_horz_line")
        bw.penup()
        bw.pensize(wd)
        bw.color("red")
        bw.goto(-sz, sz)
        bw.pendown()
        bw.goto(sz,sz)
        if snapshots:
            do_snapshot()
    if "vert_line" in tests:
        if snapshots:
            setup_snapshot("a_vert_line")
        bw.penup()
        bw.pensize(wd)
        bw.goto(sz,sz)
        bw.color("orange")
        bw.pendown()
        bw.right(90)
        bw.forward(2*sz)
        if snapshots:
            do_snapshot()
    if "diag_line" in tests:
        if snapshots:
            setup_snapshot("a_diag_line")
        bw.penup()
        bw.pensize(wd)
        bw.goto(-sz,sz)
        bw.pendown()
        bw.color("yellow")
        bw.goto(sz,-sz)
        if snapshots:
            do_snapshot()
    if "triangle" in tests:
        if snapshots:
            setup_snapshot("a_triangle")
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
        if snapshots:
            do_snapshot()
    if "dot" in tests:
        if snapshots:
            setup_snapshot("a_dot")
        bw.dot(sz, color)
        if snapshots:
            do_snapshot()
        
    if "square" in tests:
        if snapshots:
            setup_snapshot("a_square")
        bw.pensize(wd)
        add_square()
        if snapshots:
            do_snapshot()

    if "diamond" in  tests:
        dsz = .7 * sz
        bw.pensize(wd)
        if snapshots:
            setup_snapshot("diamond in square")
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
        if snapshots:
            do_snapshot()


done()