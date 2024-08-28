#run_setup_turtle_braille.py    12Aug2024  crs, fix path bug
#                               26Jul2024  crs, Author
""" Run setup program from distibution folder to ease user location
"""
import os
import sys
import subprocess

cur_dir = os.path.join(os.path.dirname(__file__))
setup_pgm = "setup_turtle_braille.py"
setup_pgm_path = os.path.join(cur_dir, setup_pgm)
if not os.path.exists(setup_pgm_path):
    setup_pgm_path = os.path.join(cur_dir, "resource_lib", "src", setup_pgm)

print(f"setup_pgm: {setup_pgm_path}")
if not os.path.exists(setup_pgm_path):
    print(f"setup program not found")
    exit(1)

subprocess.run(['python', setup_pgm_path])                # Just trial
#subprocess.run(['python', setup_pgm_path, "--verbose"])  # lots of info
#subprocess.run(['python', setup_pgm_path, "--update"])  # Update

