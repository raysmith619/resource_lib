# Turtle Braille
We attempt to provide simple support for the blind who which to do simple graphics programming using a subset of the turtle command set.  Our
approach is to accept these turtle commands, passing them on to turtle, and additionally producing the following:
* A braille window which displays the expected braille - lower resolution(e.g. 40 x 25 braille cell) rendition of the turtle display
* A text printout which, if directed to a brailler will produce a physical display similar to the braille window.  

## A set of screen shots for a simple program
![IDLE program window](Docs/braille_turtle_spokes_pgm.PNG)
## Supported turtle commands
Note that we do not handle all turtle commands - mostly those which support simple static low resolution graphics.
def backward(length):
def color(*args):
def dot(size=None, *color):
def filling():
def begin_fill():
def end_fill():
def forward(length):
def goto(x, y=None):
def setpos(x, y=None): 
def setposition(x, y=None): 
def left(angle):
def pendown():
def penup():
def right(angle):
def speed(speed):
def mainloop():
def done():
def pensize(width=None):
def width(width=None):

## Support Files
- turtle_braille.py - direct outer interface to global turtle commands, and turtle object level commands
- braille_display.py - implements turtle commands in the braille setting and the creation of display braille window and text printout
- turtle_braille_link.py - simple link to support user level replacement of "from turtle import *" with "from turtle_braille_link import *" lines
- 
# resource_lib
## Common files / support for other projects
Contains files used to support other projects.
Provides logging, tracing, properties support.


## Brief listing of document files (Docs directory)
- Program_Logging_Tracing.pptx PowerPoint presentation about Logging/Tracing demonstrating the classes SlTrace and TraceControlWindow
## Brief listing of source files (src directory) with purpose.
- arrange_control.py: window sizing/placement support
- java_properties.py: simple properties file support
- logging_absolute_minimum.py: smallest example of logging
- logging_tracing_menu.py: TraceControlWindow class example
- logging_tracing_simplest.py: Simple logging/tracing example
- resource_group.py: support to handle a program's resource groups
- select_control.py class SelectControl
  * Base for independent control
  * Provides a singleton which is universally accessible
  * Facilitates
     * setting and retrieving of game controls
     * persistent storage of values
- select_dd_choice.py Dropdown choice one of n text strings - not sure
- select_error.py General local, to our program/game, error class
- select_trace.py class SlTrace
  * trace/logging package
  * derived from smTrace.java (ours)
  * properties file support
- select_window.py  Program Level Menu control
- tkMath.py Useful window math thanks to: tkMath from recipe-552745-1.py  Ronald Longo
- trace_control_window.py class TraceControlWindow
  * Window support for SlTrace flag manipulation
- variable_control.py class VariableControlWindow
  * Simple Control and Display of program variables
  * Adapted from trace_control_window.py/TraceControl
  * Essentially presents a scrollable list of variable names and values
  * Uses select_control/SelectControl to store and manipulate variable contents
