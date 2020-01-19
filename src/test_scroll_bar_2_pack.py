#test_scroll_bar_2_pack.py
from tkinter import *

t = Tk()

c = Canvas(t)
hsb = Scrollbar(t, orient="h", command=c.xview)
vsb = Scrollbar(t, orient="v", command=c.yview)
c.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

c.pack()
hsb.pack(side=BOTTOM, fill=X)
vsb.pack(side=RIGHT, fill=Y)

###t.grid_rowconfigure(0, weight=1)
###t.grid_columnconfigure(0, weight=1)


for x in range(100, 5000, 100):
    for y in range(100, 5000, 100):
        c.create_text((x,y), anchor=CENTER, text="%d,%d" % (x,y))
c.configure(scrollregion = (0, 0, 5000, 5000))

t.mainloop()
