#wx_turtle_braille_link.py      18Dec2023  crs, remove pysinewave
#                               02Nov2023  crs, from turtle_braille_link.property
#                               27Feb2023  crs, using canvas scan
#                               21Feb2023  crs, From turtle_braille_link.py
#                               25Apr2022  crs, Author
""" link to braille turtle
Turtle Braill support is in files found in lib/src_dir/
        default: resource_lib_proj/src/
This directory is searched for in sys.path.  If found,
the directory is appended to sys.path.
The working files expected include:
    turtle_braille.py
    braille_display.py
    braille_display_test2.py    # for selftest
    
    select_trace.py
    crs_funs.py
    select_error.py
    select_report.py
    java_properties.py

HACK to add additional sister directory to lib_dir
We add sister to lib_dir

Using CanvasGrid for canvas scanning
"""
import sys
import os
from pathlib import Path

lib_dirs = [ "resource_lib", "resource_lib_proj"]
lib_dir_found = False
for sys_dir in sys.path:
    if lib_dir_found:
        break
    for lib_dir in lib_dirs:
        if lib_dir in Path(sys_dir).parts:
            print(f"Found {lib_dir} in sys.path: {sys.path}")
            lib_dir_found = True
            break

src_dir = "src"
src2_dir = "pysinewave_master"  # second path for pysinewave latest
                                # MUST be sister to lib_dir
src2_dir = None                 # Disable looking

is_testing = True
is_testing = False

src1_in_path = False     # Set if found
src2_in_path = False    # Set if found

if is_testing:  #??? TBD This doesn't look quite right
    print(f"Initial testing - removing {lib_dir} if present")
    print(f"sys.path:")
    new_syspath = []
    print(f"removing:{lib_dir}")
    for path in sys.path:
        print(path)
        if lib_dir in path:
            print("skipping:{path}")
            continue
        else:
            new_syspath.append(path)
    sys.path = new_syspath

for path in sys.path:
    path_dirs =  Path(path).parts
    if (len(path_dirs) >= 2
        and path_dirs[-2] == lib_dir
        and path_dirs[-1] == src_dir):
        print(f"{lib_dir}/{src_dir} is already in path")
        print(f"path:{path}")
        src1_in_path = True
    if src2_dir:
        if (len(path_dirs) >= 2
            and path_dirs[-1] == src2_dir):
            print(f"{src2_dir} is already in path")
            print(f"path2:{path}")
            src2_in_path = True

if not src1_in_path or not src2_in_path:              
    wd = os.getcwd()
    print(f"cwd:{wd}")
    wd_dirs = Path(wd).parts
    print(f"wd_dirs:{wd_dirs}")
    wdir = None
    n = len(wd_dirs)
    found_lib = False
    found_src2 = False
    for i in range(n-1, 0,-1):
        dirck = os.path.join(*wd_dirs[0:i],
                                 lib_dir,src_dir)
        if is_testing:
            print(f"dir_check:{dirck}")
        if not found_lib and os.path.exists(dirck):
            dir_check = dirck
            print(f"Found:{dir_check}")
            found_lib = True
            if src2_dir is not None:
                dir2ck = os.path.join(*wd_dirs[0:i], src2_dir)
                if not found_src2 and os.path.exists(dir2ck):
                    dir2_check = dir2ck
                    print(f"Found:{dir2_check}")
                    found_src2 = True
    if not found_lib:
        print(f"Didn't find {os.path.join(lib_dir,src_dir)}")
        sys.exit(1)
        
    if src2_dir and not found_src2:
        print(f"Didn't find {dir2ck}")
        sys.exit(1)
        
    print(f"Adding import path: {dir_check}")
    sys.path.append(dir_check)
    if found_src2:    
        print(f"Adding import path: {dir2_check}")
        sys.path.append(dir2_check)    

from select_trace import SlTrace
from wx_turtle_braille import *   
#SlTrace.lg("turtle braille support")
SlTrace.clearFlags()
