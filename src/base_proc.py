#base_proc.py    01Jan2024  crs Author
"""
Inline test
Communication between base process to new process
Organizing communication but avoiding restriction
that can't pickle modules
"""
import time
import multiprocessing as mp

def new_proc():
    print("Inside New Process")        
    while True:
        print("Hi: new_proc")
        time.sleep(.5)

if __name__ == "__main__":
    """ Setup communication between base process and
    new process.
    :target_fun: target function in new process
    """
    qlen = 4
    new_process = mp.Process(target=new_proc)
    cmd_queue = mp.Queue(qlen)      # Commands from new process
    cmd_resp_queue = mp.Queue(qlen)
    print("Starting New Process")        
    new_process.start()
    time.sleep(2)
    while True:
        print("Hi from base process")
        time.sleep(.3)