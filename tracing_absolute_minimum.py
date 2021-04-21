# tracing_absolute_minimum.py    22Feb2020  crs

from select_trace import SlTrace
SlTrace.setFlags("good=1,bad=0")
SlTrace.lg("we see good", "good")
SlTrace.lg("we don't see bad", "bad")
