#turtle_canvas_item.py
import turtle as tu
import tkinter as tk

tt = tu.Turtle()
screen = tu.Screen()

simple_items = True
filled_square = True

simple_items = False 
if simple_items:
    print("simple items")
    sd = 100
    tt.color("red")
    tt.forward(sd)
    tt.color("green")
    tt.right(90)
    tt.forward(sd)
if filled_square:
    print("filled square")    
    sd = 100
    tt.color("blue")
    tt.width(10)
    tt.fillcolor("purple")
    tt.begin_fill()
    for i in range(4):
        tt.forward(sd)
        tt.right(90)
    tt.end_fill()
    
canvas = screen.getcanvas()
for item in sorted(canvas.find_all()):
    iopts = canvas.itemconfig(item)
    type = canvas.type(item)
    coords = canvas.coords(item)
    print(f"{item}: {type} {coords}")
    for key in iopts:
        val = iopts[key]
        print(f"    {key} {val}")
tk.mainloop()
