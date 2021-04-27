# test_canvas_scrollbar.py
from tkinter import *

def add_label(var_frame=None, label=None, max_width=0, background="white"):
    fmt_text = "%-*s" % (max_width, label)
    lb = Label(var_frame, text=fmt_text, background=background)
    lb.pack(side=TOP)




root=Tk()
frame_width=200
frame_height=400
canvas_width = 100
canvas_height = 300
frame_scroll_width = canvas_width*4
frame_scroll_height = canvas_height*4
frame=Frame(root,width=frame_width,height=frame_height)
frame.pack(expand=True, fill=BOTH) #.grid(row=0,column=0)
canvas=Canvas(frame,bg='#FFFFFF',width=canvas_width,height=canvas_height)
canvas.configure(scrollregion=(0,0,frame_scroll_width,frame_scroll_height))
hbar=Scrollbar(frame,orient=HORIZONTAL)
hbar.pack(side=BOTTOM,fill=X)
hbar.config(command=canvas.xview)
vbar=Scrollbar(frame,orient=VERTICAL)
vbar.pack(side=RIGHT,fill=Y)
vbar.config(command=canvas.yview)
canvas.config(width=canvas_width,height=canvas_height)
canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
canvas.pack(side=LEFT,expand=True,fill=BOTH)
for i in range(10):
    label = f"label {i}"
    add_label(canvas, label)
root.mainloop()