# square_loop_2a.py
# Using CanvasGrid for canvas scanning
# Display a square

from turtle_braille_link_2 import *    # Get our graphics
##from turtle import *		     # Get standard stuff

colors = ["red","orange","yellow","green"]
goto(0,0)
for colr in colors:
    width(40)
    color(colr)
    forward(200)
    right(90)
done()		    # Complete drawing
