# wx_spokes.py  20Jan2024, crs from spokes.py
# Display a star with spokes

from wx_turtle_braille_link import *        # Set for wxPython
#from turtle import *    # Bring in turtle graphic functions
speed("fastest")
for i in range(7):      # Do things 7 times
    if i == 0:
        color("red")
    elif i == 1:
        color("orange")
    elif i == 2:
        color("yellow")
    elif i == 3:
        color("green")
    elif i == 4:
        color("blue")
    elif i == 5:
        color("indigo")
    else:
        color("violet")
    forward(300)
    dot(100)
    backward(300)
    right(360/7)
done()
