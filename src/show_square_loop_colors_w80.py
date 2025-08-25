# show_square_loop_colors_w80.py  # standard
# Display a square with colored sides

from turtle import *		     # Get standard stuff

colors = ["red","orange","yellow","green"]

for colr in colors:
    width(80)
    color(colr)
    forward(200)
    right(90)
done()		    # Complete drawings
