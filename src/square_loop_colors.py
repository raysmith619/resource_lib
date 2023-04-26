# square_loop_colors.py
# Display a square

from turtle_braille_link import *    # Get our graphics
##from turtle import *		     # Get standard stuff

colors = ["red","orange","yellow","green"]

for colr in colors:
    width(40)
    color(colr)
    forward(200)
    right(90)
done()		    # Complete drawing
6