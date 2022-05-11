#turtle_braille_link.py   25Apr2022  crs, Author
""" link to braille turtle
"""
import sys
import os
from pathlib import Path

lib_dir = "resource_lib_proj"
src_dir = "src"
is_testing = True
is_testing = False

in_path = False     # Set if found
if is_testing:
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
        in_path = True

if not in_path:              
    wd = os.getcwd()
    print(f"cwd:{wd}")
    wd_dirs = Path(wd).parts
    print(f"wd_dirs:{wd_dirs}")
    wdir = None
    n = len(wd_dirs)
    found_lib = False
    for i in range(n-1, 0,-1):
        dir_check = os.path.join(*wd_dirs[0:i],
                                 lib_dir,src_dir)
        if is_testing:
            print(f"dir_check:{dir_check}")
        if os.path.exists(dir_check):
            print(f"Found:{dir_check}")
            found_lib = True
            break
    if not found_lib:
        print(f"Didn't find {os.path.join(lib_dir,src_dir)}")
        sys.exit(1)
        
    print(f"Adding import path: {dir_check}")
    sys.path.append(dir_check)    

from turtle_braille import *   
SlTrace.lg("turtle braille support")
SlTrace.clearFlags()
