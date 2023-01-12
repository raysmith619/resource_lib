# square_loop.py
# Display a square

from turtle_braille_link import *    # Get our graphics
##from turtle import *		     # Get standard stuff

color("green")
width(40)
for i in range(4):  # Do 4 times
    forward(200)
    right(90)
done()		    # Complete drawing
