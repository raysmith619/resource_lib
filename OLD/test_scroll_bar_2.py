#test_scroll_bar_2.py
from tkinter import *

t = Tk()

c = Canvas(t)
hsb = Scrollbar(t, orient="h", command=c.xview)
vsb = Scrollbar(t, orient="v", command=c.yview)
c.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

c.grid(row=0, column=0, sticky="nsew")
hsb.grid(row=1, column=0, stick="ew")
vsb.grid(row=0, column=1, sticky="ns")

t.grid_rowconfigure(0, weight=1)
t.grid_columnconfigure(0, weight=1)

c.configure(scrollregion = (0, 0, 5000, 5000))

for x in range(100, 5000, 100):
    for y in range(100, 5000, 100):
        c.create_text((x,y), anchor=CENTER, text="%d,%d" % (x,y))

t.mainloop()
