# logging_tracing_simplest.py    22Feb2020  crs
# Simpest use, but we get:
#  1. Named / Dated log filess
#  2. Tracing by flag
#
import sys
import time
from select_trace import SlTrace

cmd_flags = sys.argv[1] if len(sys.argv)>1 else "flag1,flag2=0,big=0"

SlTrace.setFlags(cmd_flags)
SlTrace.lg(f"cmd_flags:{cmd_flags}")
SlTrace.lg("flag1", "flag1")
SlTrace.lg("flag2", "flag2")

for i in range(5):
    if SlTrace.trace("big"):
        SlTrace.lg(f"{i}: big stuff")
    else:
        SlTrace.lg(f"{i}: no so big")
    time.sleep(2)

