# wx_spokes.py  16Jul2024  crs use wx_turtle_braille directly
#               20Jan2024, crs from spokes.py
# Display a star with spokes

from wx_turtle_braille import *        # Set for wxPython
#from turtle import *    # Bring in turtle graphic functions
speed("fastest")
colors = ["red","orange","yellow",
          "green","blue","indigo","violet"]
for colr in colors:      # do all colors in list
    color(colr)
    forward(300)
    dot(100)
    backward(300)
    right(360/len(colors))
done()
