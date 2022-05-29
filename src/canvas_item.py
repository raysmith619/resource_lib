#canvas_item.py
import tkinter as tk
master = tk.Tk()

canvas = tk.Canvas(master, width=200, height=200)
canvas.pack()
simple_items = True
filled_square = True

simple_items = False 
if simple_items:
    line = canvas.create_line(1,2,100,100, fill="red", width=10)
    line2 = canvas.create_line(3,4,50,200, fill="green")
    oval = canvas.create_oval(100,100,150, 200, fill="orange")
    sq = canvas.create_rectangle(100,100,150, 150, fill="orange")
if filled_square:    
    sd = 100
    pts = [(0,0), (sd,0), (sd,sd), (0,sd)]
    pts2 = pts[2]
    canvas.create_rectangle(pts[0][0],pts[0][1], pts2[0],pts2[1], fill="green")
for item in canvas.find_all():
    iopts = canvas.itemconfig(item)
    type = canvas.type(item)
    coords = canvas.coords(item)
    print(f"{item}: {type} {coords}")
    for key in iopts:
        val = iopts[key]
        print(f"    {key} {val}")
tk.mainloop()
