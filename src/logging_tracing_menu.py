# logging_tracing_menu.py    22Feb2020  crs
# Simple with a menu:
#  1. Named / Dated log files
#  2. Tracing by flag
#  3. Plus change settings easily during running
#
import sys
from select_trace import SlTrace
from trace_control_window import TraceControlWindow


cmd_flags = sys.argv[1] if len(sys.argv)>1 else "flag1,flag2=0,end_loop=0"

SlTrace.setFlags(cmd_flags)
SlTrace.lg(f"cmd_flags:{cmd_flags}")
SlTrace.lg("flag1", "flag1")
SlTrace.lg("flag2", "flag2")
tcw = TraceControlWindow()

for i in range(20):
    if SlTrace.trace("big"):
        SlTrace.lg(f"{i}: big stuff")
    else:
        SlTrace.lg(f"{i}: no so big")
    tcw.sleep(2)
    if SlTrace.trace("end_loop"):
        SlTrace.lg("Manual break")
        break
SlTrace.lg("Ending Program")
