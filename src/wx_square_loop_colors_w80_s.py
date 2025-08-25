# wx_square_loop_colors.py  26Jul2024  crs, use wx_turtle_braille.py directly
# Display a square with colored sides

##from wx_turtle_braille import *    # Get our graphics
from turtle import *		     # Get standard stuff

colors = ["red","orange","yellow","green"]

for colr in colors:
    width(80)
    color(colr)
    forward(200)
    right(90)
done()		    # Complete drawings
