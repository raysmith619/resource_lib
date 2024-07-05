# square_loop_red_thick_growing_tb.py
# Display a square
from turtle_braille_link import * # graphics

color("red")
for i in range(4):  # Do 4 times
    width(40+i*20)
    forward(200)
    right(90)
done()		    # Complete drawing
