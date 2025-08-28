# show_square_loop_colors_grid.py  # standard
# Display a square with colored sides

from turtle import *		     # Get standard stuff

colors = ["red","orange","yellow","green"]

for colr in colors:
    width(40)
    color(colr)
    forward(200)
    right(90)

# Do grid to demonstrate dividing up screen
# into regions for text map for Braille
speed(0)
fudge = 40
scr_width = window_width()-fudge
x_boarder = 30
y_boarder = 25
scr_height = window_height()-fudge
x_start = -scr_width/2 + x_boarder
x_end = x_start + scr_width - x_boarder
x_len = x_end - x_start
y_start = -scr_height/2 + y_boarder
y_end = y_start + scr_height - y_boarder
y_len = y_end-y_start
ncol = 40
nrow = 25
width(1)
color("black")
# Horizontal lines
for n in range(1, nrow+1+1):
    penup()
    y_val = y_start + (n-1)*y_len/nrow
    if n < nrow+1:
        text_row_x = x_start - 40
        text_row_y = y_val + .4*y_len/nrow
        goto(x=text_row_x, y=text_row_y)
        write(f"row {n:2}") 
    goto(x=x_start, y=y_val)
    pendown()
    goto(x=x_end, y=y_val)

# Vertical lines    
for n in range(1, ncol+1+1):
    penup()
    x_val = x_start + (n-1)*x_len/ncol
    if n < ncol+1:
        text_row_x = x_val + 0.2*x_len/nrow
        text_row_y = y_start - 20
        goto(x=text_row_x, y=text_row_y)
        write(f"{n:2}") 
    goto(x=x_val, y=y_start)
    pendown()
    goto(x=x_val, y=y_end)
    
done()		    # Complete drawings
