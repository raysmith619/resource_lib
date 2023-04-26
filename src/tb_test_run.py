# tb_test_run.py    09Mar2023  crs, Author
"""
Process TurtleBraille test files
Programs are found in list file
of the format: # comment line - ignored 
                python_test_file
Program outputs are placed in tb_test_run.out
"""

import subprocess
import re
import os
import time

from select_trace import SlTrace


"""
test list files
    1. support single line comments starting with # going to end of line
    2. support triple single quote (''') starting with zero or more white space
        ending on a line containing ''' anywhere in the line.  The complete line
        is ignored
"""

test_list_file = "tb_test_list.tests"
test_out_dir = "../tests"
test_out_dir = os.path.abspath(test_out_dir)
SlTrace.setLogToStd(False)      # Clean display
SlTrace.setLogStdTs(on=False)      # No Ts on printed linesw
SlTrace.clearFlags()

run_time_start = time.time()
n_run = 0
n_success = 0
n_fail = 0
n_timeout = 0

if SlTrace.trace("stdOutHasTs"):
    print("Has flag stdOutHasTs")
#if SlTrace.trace("dbg_sound"):
#    cls.setFlags("stdOutHasTs=True,decpl=True,sound=True,pos_tracking=True")
            

tsp = SlTrace.getTs()
out_base_name = re.sub(r'\.[^.]+$', '_' + tsp +'.out', test_list_file)
out_file = os.path.join(test_out_dir, out_base_name)

timeout = 160
#timeout = 20
# Get test list file lies
tlf_lines = None
with open(test_list_file) as tlfp:
    tlf_lines = tlfp.readlines()
in_triple_single_quote  = False
with open(out_file, "w") as outfp:
    # Process input test file
    for line in tlf_lines:
        if in_triple_single_quote:
            if re.match(r"'''", line):   # Anywhere in line
                in_triple_single_quote = False  # End it 
            continue            # Ignore all lines, including end
            
        line = re.sub(r'\n$', '', line)     # remove eol if one
        line = re.sub(r'\s*#.*', '', line)
        if re.match(r'^\s*$', line):
            continue
        
        if re.match(r"'''", line):
            in_triple_single_quote = True 
            continue            # Ignore current line
        
        print(line, file=outfp)
        print(line)
        file_time = line.split(";")
        pgm_file = file_time[0]
        pgm_time = file_time[1] if len(file_time) > 1 else None
        pgm_file = pgm_file.strip()
        if pgm_time is None:
            pgm_time = timeout
        else:
            pgm_time = float(pgm_time.strip())
        out_str = None
        err_str = None
        try:
            time_start = time.time()
            n_run += 1
            run_ret = subprocess.run(["python",pgm_file],capture_output=True,
                                     timeout=pgm_time)
            ret_code = run_ret.returncode
            out_str = run_ret.stdout
            err_str = run_ret.stderr
            if ret_code == 0:
                n_success += 1
                SlTrace.lg(f"Success: {n_success}", to_stdout=True)
            else:
                n_fail += 1
                SlTrace.lg(f"Failure returncode:{ret_code} fail:{n_fail}", to_stdout=True)
            time_end = time.time()
            SlTrace.lg(f"{pgm_file} run time: {time_end-time_start:.02f} seconds",
                       to_stdout=True)
        except subprocess.TimeoutExpired as e:
            n_timeout += 1
            SlTrace.lg(f"{line} time out: {n_timeout}", to_stdout=True)
            out_str = e.stdout
            err_str = e.stderr
        if out_str is not None:
            SlTrace.lg(out_str.decode("utf-8"))
        if err_str is not None:
            SlTrace.lg(err_str.decode("utf-8"))
            
    run_time_end = time.time()        
    SlTrace.lg(f"\nEnd of Testing Run time: {run_time_end-run_time_start:.1f}",
                to_stdout=True)
    SlTrace.lg(f"run: {n_run} success: {n_success} fail: {n_fail} timeout: {n_timeout}",
                to_stdout=True)
    
SlTrace.lg(f"Output file: {out_file}", to_stdout=True)