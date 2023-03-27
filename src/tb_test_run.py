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
tsp = SlTrace.getTs()
out_base_name = re.sub(r'\.[^.]+$', '_' + tsp +'.out', test_list_file)
out_file = os.path.join(test_out_dir, out_base_name)

timeout = 180
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
            print(f"{line} time dout")
            out_str = e.stdout
            err_str = e.stderr
        if out_str is not None:
            print(out_str.decode("utf-8") , file=outfp)
        if err_str is not None:
            print(err_str.decode("utf-8") , file=outfp)
            
    print("\nEnd of Testing Run")
    print("\nEnd of Testing Run", file=outfp)
print(f"Output file: {out_file}")