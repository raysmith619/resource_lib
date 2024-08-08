#wx_turtle_braille_link.py      26Jul2024  crs, Strip down - Announce USERS to use wx_turtle_braille.py
#                               24Jul2024  crs convert to using ev TURBO_BRAILLE_PATH
#                               18Dec2023  crs, remove pysinewave
#                               02Nov2023  crs, from turtle_braille_link.property
#                               27Feb2023  crs, using canvas scan
#                               21Feb2023  crs, From turtle_braille_link.py
#                               25Apr2022  crs, Author
""" 
Users should use wx_turtle_braille.py
"""
print("""
      PLEASE USE
                    from wx_turtle_braille import *
      INSTEAD
      """)
from wx_turtle_braille import *     # just for backwards compatibility

if __name__ == '__main__':
    from wx_turtle_braille import *

    colors = ["red","orange","yellow","green"]

    for colr in colors:
        width(40)
        color(colr)
        forward(200)
        right(90)
    done()		    # Complete drawings
    
