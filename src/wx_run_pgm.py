#wx_run_pgm.py      21Jul2024  crs
import subprocess
import signal
import re
import os
import time
from select_trace import SlTrace

n_success = 0
n_fail = 0
pgm_time = 60
pgm_dir = os.path.dirname(__file__)
pgm_files = ["wx_tb_test_goto.py", "wx_tb_test_magnify.py", "wx_tb_test_goto.py"]
for pgm_file in pgm_files:
    pgm_file = os.path.join(pgm_dir,pgm_file)
    try:
        run_ret = subprocess.run(["python",pgm_file],                                
                                timeout=pgm_time)
    except Exception as e:
        SlTrace.lg("Exception: {e}")
        
    ret_code = run_ret.returncode
    out_str = run_ret.stdout
    err_str = run_ret.stderr
    if ret_code == 0:
        n_success += 1
        SlTrace.lg(f"Success: {n_success}", to_stdout=True)
    else:
        n_fail += 1
        SlTrace.lg(f"Failure returncode:{ret_code} fail:{n_fail}", to_stdout=True)
