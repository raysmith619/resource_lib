# square_fill.py
# Display a square
from turtle_braille_link import *        # Set link to library

begin_fill()
color("red")
width(2)
for i in range(4):
    forward(200)
    right(90)
end_fill()
done()
