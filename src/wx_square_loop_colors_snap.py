# wx_square_loop_colors.py  26Jul2024  crs, use wx_turtle_braille.py directly
# Display a square with colored sides

from wx_turtle_braille import *    # Get our graphics
##from turtle import *		     # Get standard stuff
from select_trace import SlTrace

SlTrace.setFlags("user,host")
colors = ["red","orange","yellow","green"]

nside = 0
snapshot(f"Begining - before square")
for colr in colors:
    nside += 1
    width(40)
    color(colr)
    forward(200)
    right(90)
    snapshot(f"side{nside}: {colr}")
done()		    # Complete drawings
