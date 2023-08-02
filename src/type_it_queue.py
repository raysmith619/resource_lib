#type_it_queue.py   30Jul2023  crs
""" process queue of TypeIt cmds
"""
import threading
import queue
import time

from type_it import TypeIt

class TypeItQueue:
    def __init__(self):
        """ setup queue
        """
        self.running = True
        self.ti_cur = None      # current TypeIt 
        self.ti_queue = queue.Queue(20)  # speech queue of SpeakerControlCmd 
        self.ti_thread = threading.Thread(target=self.ti_proc_thread)
        self.ti_thread.start()

            
    def ti_proc_thread(self):
        """ Process pending speech requests (SpeakerControlCmd)
        """
        print("ti_proc_thread running")
        while self.running:
            if self.ti_busy():
                time.sleep(.1)            
            elif self.ti_queue.qsize() > 0:            
                #print("ti_queue.get()")
                ti = self.ti_queue.get()
                self.ti_run(ti)
                
        print("ti_proc_thread returning")

    def put(self, ti):
        """ Put ti in queue
        :ti: TypeIt  to place in queue
        """
        print(f"put({ti})")
        self.ti_queue.put(ti)

    def is_busy(self):
        if self.ti_queue.qsize() > 0:
            print(f"ti_queue.qsize:{self.ti_queue.qsize()}")
            return True
        
        if self.ti_busy():
            return True
                
        return False

    def ti_busy(self):
        """ Check if there is a current ti
        and it is busy
        """
        if self.ti_cur is not None:
            if self.ti_cur.is_busy():
                return True
            self.ti_cur = None      # done
        
        return False
            
    def ti_run(self, ti):
        self.ti_cur = ti    # Set to be cleared when done
        ti.type_it()
        
    def wait_while_busy(self):
        while self.is_busy():
            print(f"wait_while_busy: {self.ti_cur}")
            time.sleep(.1)
                    
    def stop(self):
        """ Stop queue thead
        """
        self.running = False
        self.ti_thread.join()
        
                            

if __name__ == "__main__":
    print("Test Start")
    tiq = TypeItQueue()

    tiq.put(TypeIt(f"TypeIt(1)", delay=1))
    tiq.put(TypeIt(f"TypeIt(2)", delay=1))
    tiq.put(TypeIt(f"TypeIt(3)", delay=1))
    tiq.wait_while_busy()

    tiq.put(TypeIt(f"TypeIt(4)", delay=1))
    tiq.put(TypeIt(f"TypeIt(5)", delay=1))
    tiq.wait_while_busy()

    tiq.put(TypeIt(f"TypeIt(6)", delay=1))
    tiq.wait_while_busy()
    
    tiq.put(TypeIt(f"TypeIt(7)", delay=1))
    tiq.wait_while_busy()
    tiq.stop()
    print("End of Test")    
        