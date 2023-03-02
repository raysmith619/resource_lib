# square_loop_colors_show_canvas.py
# Display a square

from turtle_braille_link import *    # Get our graphics
##from turtle import *		     # Get standard stuff

SlTrace.setFlags("show_canvas_items")
colors = ["red","orange","yellow","green"]

for colr in colors:
    width(40)
    color(colr)
    forward(200)
    right(90)
done()		    # Complete drawing
