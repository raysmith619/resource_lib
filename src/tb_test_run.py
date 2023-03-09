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

from select_trace import SlTrace

test_list_file = "tb_test_list.tests"
test_out_dir = "../tests"
test_out_dir = os.path.abspath(test_out_dir)
tsp = SlTrace.getTs()
out_base_name = re.sub(r'\.[^.]+$', '_' + tsp +'.out', test_list_file)
out_file = os.path.join(test_out_dir, out_base_name)

timeout = 180
#timeout = 20
# Get test list file lies
tlf_lines = None
with open(test_list_file) as tlfp:
    tlf_lines = tlfp.readlines()

with open(out_file, "w") as outfp:
    # Process input test file
    for line in tlf_lines:
        line = re.sub(r'\n$', '', line)     # remove eol if one
        line = re.sub(r'\s*#.*', '', line)
        if re.match(r'^\s*$', line):
            continue
        print(line, file=outfp)
        print(line)
        out_str = None
        err_str = None
        try:
            run_ret = subprocess.run(["python",line],capture_output=True,
                                     timeout=timeout)
            ret_code = run_ret.returncode
            out_str = run_ret.stdout
            err_str = run_ret.stderr
            if ret_code == 0:
                print("Success")
            else:
                print(f"Failure returncode:{ret_code}")
                print(f"Failure returncode:{ret_code}", file=outfp)
        except subprocess.TimeoutExpired as e:
            print(f"{line} timedout")
            out_str = e.stdout
            err_str = e.stderr
        if out_str is not None:
            print(out_str.decode("utf-8") , file=outfp)
        if err_str is not None:
            print(err_str.decode("utf-8") , file=outfp)
            
    print("\nEnd of Testing Run")
    print("\nEnd of Testing Run", file=outfp)
print(f"Output file: {out_file}")