# wx_square_loop_colors_snap_tracking.py  24Jan2025  crs, track
# Display a square with colored sides

from wx_turtle_braille import *    # Get our graphics
##from turtle import *		     # Get standard stuff
from select_trace import SlTrace
import canvas_copy
SlTrace.setFlags("snapshot")
SlTrace.setFlags("user,host,rpc")
colors = ["red","orange","yellow","green"]
canvas = getcanvas()
cv_str = canvas_copy.canvas_show_items(canvas,
                    show_coords=False,
                    show_options=True,
                    use_value_cache=True)

SlTrace.lg(f"Beginning: cv_str:{cv_str}", "canvas_copy")
nside = 0
snapshot(f"Begining - before square")
for colr in colors:
    nside += 1
    width(40)
    color(colr)
    forward(200)
    right(90)
    cv_str = canvas_copy.canvas_show_items(canvas,
                    show_coords=False,
                    show_options=True,
                    use_value_cache=True)
    SlTrace.lg(f"side{nside}: {colr}: cv_str:{cv_str}", "canvas_copy")
    snapshot(f"side{nside}: {colr}")
done()		    # Complete drawings
