#base_proc_to_new.py    01Jan2024  crs Author
""" 
Communication between base process to new process
Organizing communication but avoiding restriction
that can't pickle modules
"""
import time
import multiprocessing as mp

class BaseProc:
    def __init__(self, target):
        """ Setup communication between base process and
        new process.
        :target_fun: target function in new process
        """
        qlen = 4
        self.new_process = mp.Process(target=target)
        self.cmd_queue = mp.Queue(qlen)      # Commands from new process
        self.cmd_resp_queue = mp.Queue(qlen)
        self.new_process.start()

class NewProc:
    def __init__(self):
        """ Setup communications for new process
        """

#if __name__ == "__main__":
import time

def new_proc():
    while True:
        print("Hi from new_proc")
        time.sleep(.5)

print("Starting New Process")        
bP = BaseProc(target=new_proc)
while True:
    print("Hi from base process")
    time.sleep(.3)