#tkinter_goto.py
""" Experimenting with turtle goto in tkinter
"""
import turtle as tu
import tkinter as tk

ts = tu.getscreen()
tt = tu.Turtle()
ts.tracer(0)
tt.penup()
tt.goto(x=100,y=100)
ts.update()


ts.mainloop()