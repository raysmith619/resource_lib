# resource_lib
Common files / support for other projects
Files and objects used to support other projects
Supporting logging, tracing, properties files

Brief listing of source files (src directory) with purpose.
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
