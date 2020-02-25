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
