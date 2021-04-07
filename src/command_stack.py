# command_stack
""" General command stack 
Replacement for Stack<EMBCommand>
"""
from select_trace import SlTrace

class CommandStack:
    
    def __init__(self):
        self.our_stack = []
        
    def is_empty(self):
        return len(self.our_stack)==0
    
    def get_cmds(self):
        return self.our_stack
    
    def peek(self):
        if len(self.our_stack) > 0:
            return self.our_stack[-1]
        
        return None 
    
    def push(self, cmd):
        self.our_stack.append(cmd)
        
    def pop(self):
        ret = self.our_stack.pop()
        return ret 
    
    def size(self):
        return len(self.our_stack)
    
    def element_at(self, idx):
        return self.our_stack[-idx-1]   # 0 - top of stack

if __name__ == "__main__":
    cstk = CommandStack()
    SlTrace.lg(f"is_empty:{cstk.is_empty()}")
    for i in range(5):
        cstk.push(i)
        SlTrace.lg(f"peek:{cstk.peek()}")
        SlTrace.lg(f"is_empty:{cstk.is_empty()}")
        SlTrace.lg(f"size:{cstk.size()}")
        SlTrace.lg(f"element_at({i}):{cstk.element_at(i)}")
        
    while not cstk.is_empty():
        SlTrace.lg(f"pop: {cstk.pop()}")
    