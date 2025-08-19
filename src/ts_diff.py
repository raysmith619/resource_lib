#ts_diff.py  03Aug2025, crs Author
""" Output difference between two time stamps
"""
import sys
from select_trace import SlTrace
SlTrace.setAllQuiet()
if len(sys.argv) < 2:
    SlTrace.lg("Create args for debugging/testing")
    sys.argv.append("20250802_102600")
    sys.argv.append("20250803_095558") 
ts1 = sys.argv[1]
ts2 = sys.argv[2]
tsdiff = SlTrace.ts_diff(ts1,ts2)
SlTrace.lg(f"{tsdiff} seconds")
SlTrace.lg("End of run")

