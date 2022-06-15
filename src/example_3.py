#example_3.py
#from: https://stackoverflow.com/questions/48730345/python-rawturtle-not-following-goto-command
#
import turtle
from tkinter import *

FONT = ('Helvetica', 8)

def move(x, y):
    terrapin.setpos(x, y)
    print(terrapin.pos())

def penState(x, y):
    global penDown

    if penDown:
        terrapin.penup()
        penDown = False
    else:
        terrapin.pendown()
        penDown = True

def changeWidth(w):
    terrapin.pensize(w)

def changeColour():
    color = colourBox.get()
    terrapin.color(color)
    colourBox.configure(fg=color)

def doCircle():
    radius = int(circleSizeBox.get())

    if checkFillIsTrue.get():
        terrapin.begin_fill()
        terrapin.circle(radius)
        terrapin.end_fill()
    else:
        terrapin.circle(radius)

window = Tk('Paint')
window.title('onionPaint')

root = Frame(window)
root.pack(side=LEFT)

canvas = Canvas(window, width=500, height=500)
screen = turtle.TurtleScreen(canvas)

terrapin = turtle.RawTurtle(screen)

screen.onclick(move, btn=1)
screen.onclick(penState, btn=2)

canvas.pack(side=RIGHT)

checkFillIsTrue = BooleanVar()
penDown = True

# Pen width box
sizeLabel = Label(root, text="Pen Width")
sizeLabel.grid()
sizeScale = Scale(root, variable='var', orient=HORIZONTAL, command=changeWidth)
sizeScale.grid()

# Colour box
colourLabel = Label(root, text="Color(HEX or name):")
colourLabel.grid()
colourFrame = Frame(root)
colourFrame.grid()
colourBox = Entry(colourFrame, bd=1)
colourBox.pack(side=LEFT)
colourSubmit = Button(colourFrame, text="OK", command=changeColour)
colourSubmit.pack(side=RIGHT)

# Fill
fillLabel = Label(root, text='Fill')
fillLabel.grid()
fillFrame = Frame(root)
fillFrame.grid()
beginFill = Button(fillFrame, text='Begin Fill', command=terrapin.begin_fill)
endFill = Button(fillFrame, text='End Fill', command=terrapin.end_fill)
beginFill.pack(side=LEFT)
endFill.pack(side=RIGHT)

# More shapes
Label(root, text='Shapes').grid()

# Circle form
Label(root, text='Circle', font=FONT).grid()
circleSize = Frame(root)
circleSize.grid()
circleSizeBox = Entry(circleSize, bd=1)
circleSizeBox.insert(0, 'Radius')
circleSizeBox.pack(side=LEFT)
fillCheck = Checkbutton(circleSize, text='Fill', variable=checkFillIsTrue).pack(side=LEFT)
circleSizeSubmit = Button(circleSize, text='Draw', command=doCircle).pack(side=RIGHT)

# Text form
Label(root, text='Text', font=FONT).grid()
textFrame = Frame(root)
textFrame.grid()

window.mainloop()