#wx_turtle_braille_link.py  24Jul2023  crs convert to using ev TURBO_BRAILLE_PATH
#                               18Dec2023  crs, remove pysinewave
#                               02Nov2023  crs, from turtle_braille_link.property
#                               27Feb2023  crs, using canvas scan
#                               21Feb2023  crs, From turtle_braille_link.py
#                               25Apr2022  crs, Author
""" link to braille turtle
Turtle Braill support is in files found environment variable TURBO_BRAILLE_PATH
        default: complain
"""
import os
import sys

tbp_ev = "TURTLE_BRAILLE_PATH"
tbp = os.getenv(tbp_ev)
if tbp is None:
    print(f"Environment variable {tbp_ev} needs to be set, pointing our code")
    sys.exit(1)
link_file = os.path.basename(__file__)
link_via_tbp = os.path.join(tbp, link_file)
if not os.path.exists(link_via_tbp):
    print(f"{link_file} not found in directory {tbp} - we're suspicious")
    exit(2)

sys.path.append(tbp)

from select_trace import SlTrace
from wx_turtle_braille import *   
#SlTrace.lg("turtle braille support")
SlTrace.clearFlags()

if __name__ == '__main__':
    from wx_turtle_braille_link import *

    colors = ["red","orange","yellow","green"]

    for colr in colors:
        width(40)
        color(colr)
        forward(200)
        right(90)
    done()		    # Complete drawings
    
