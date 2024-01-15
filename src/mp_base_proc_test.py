#mp_base_proc_test.py    04Jan2024  crs Author
"""
Multiprocessing base process
Communication between base process to new process
Organizing communication but avoiding restriction
that can't pickle modules
"""
import time
from mp_base_proc import MpBaseProc
""" Setup communication between base process and
new process.
:target_fun: target function in new process
"""
        
def new_proc():
    print("Inside New Process")        
    while True:
        print("Hi: new_proc")
        time.sleep(.5)

bP = MpBaseProc(target=new_proc)
time.sleep(2)
while True:
    print("Hi from base process")
    time.sleep(.3)