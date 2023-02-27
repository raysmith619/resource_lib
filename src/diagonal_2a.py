# diagonal_2a.py
# Using CanvasGrid for canvas scanning
# Display diagonal line with a dot at each end

from turtle_braille_link import *    # Get our graphics
##from turtle import *		     # Get standard stuff
#SlTrace.setFlags("win_items=True")
#SlTrace.lg("win_items are printed")
len = 300
dot_size = 20
dot_radius = dot_size/2
colors = ["red","orange","yellow","green"]
color("red")
goto(-len+dot_radius,len-dot_radius)
dot(dot_size)
width(10)
color("blue")
setheading(-45)
#forward(len/10)
goto(len-dot_radius,-len+dot_radius)
color("violet")
dot(dot_size)
done()		    # Complete drawing
