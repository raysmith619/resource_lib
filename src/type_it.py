#type_it.py 30Jul2023  crs, Author
"""
Just type text plus delay
"""
import time

class TypeIt:
    tid = 0
    def __init__(self, text="TI", delay=1):
        """ Just type with delay
        :text: text to type default: TypeIt
        :delay: delay before type default: 1 second
        """
        TypeIt.tid += 1
        self.tid = TypeIt.tid
        self.text = text
        self.delay = delay
        self.busy = False   # True -> busy typting
    
    def __str__(self):
        st = f"{self.text}:{self.tid}"
        return st
        
    def type_it(self):
        self.busy = True
        time.sleep(self.delay)
        print(self.text)
        self.busy = False
    
    def is_busy(self):
        return self.busy
        
if __name__ == "__main__":
    ti = TypeIt()
    ti2 = TypeIt("ti2", delay = 2)
    ti.type_it()
    ti2.type_it()