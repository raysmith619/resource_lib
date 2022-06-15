#turtle_canvas_item.py
import turtle as tu
import tkinter as tk

tt = tu.Turtle()
screen = tu.Screen()
tt.hideturtle()
sd = 100

penup_test = False
simple_items = False
filled_square = False

penup_test = True
if penup_test:
    print("penup test")
    tt.penup()
    tt.color("red")
    tt.forward(sd)
    tt.pendown()
    tt.color("green")
    tt.forward(sd)
    
if simple_items:
    print("simple items")
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

item_samples = {}
canvas = screen.getcanvas()
def show_item(item):
    """ display changing values for item
    """
    iopts = canvas.itemconfig(item)
    itype = canvas.type(item)
    coords = canvas.coords(item)
    if itype in item_samples:
        item_sample_iopts = item_samples[itype]
    else:
        item_sample_iopts = None
    print(f"{item}: {itype} {coords}")
    for key in iopts:
        val = iopts[key]
        is_changed = True     # assume entry option changed
        if item_sample_iopts is not None:
            is_equal = True # Check for equal item option
            sample_val = item_sample_iopts[key]
            if len(val) == len(sample_val):
                for i in range(len(val)):
                    if val[i] != sample_val[i]:
                        is_equal = False
                        break
                if is_equal:
                    is_changed = False
        if is_changed: 
            print(f"    {key} {val}")
    item_samples[itype] = iopts
        
for item in sorted(canvas.find_all()):
    show_item(item)
tk.mainloop()
