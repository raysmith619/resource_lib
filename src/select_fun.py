# select_fun.py
# Select functions
import copy

from select_trace import SlTrace

select_copy_depth = 0

def select_copy(obj, levels=4, use_select_copy=True):
    """ Copy object to allow most manipulations of the copy
    without affecting the original
        Checks for member function "select_copy"  and if present
        and if more_copy is True uses it
            for the copy if present.
        Iterates at most levels with
            1. if member function "select_copy"
                return
            2. if hasattr __dict__
                iterate over __dict__.keys()
            3. direct copy attribute
    :levels: maximum number of levels of recursion
    :use_select_copy: Use select_copy member, if present
            default: True
    """
    if levels < 1:
        return obj      # Above max level, return self
    
    ###if use_select_copy and hasattr(obj, "select_copy"):
    ###    return obj.select_copy(levels=levels-1)
    global select_copy_depth
    select_copy_depth += 1

    SlTrace.lg("select_copy depth=%d obj:type(%s) %s" % (select_copy_depth, type(obj), str(obj)), "select_copy")
    if hasattr(obj, "copy"):
        if hasattr(obj, "part_check"):
            obj.part_check(prefix="select_copy")
        res = obj.copy()
    else:
        res = copy.deepcopy(obj)
    #res = copy.copy(obj)
    SlTrace.lg("select_copy depth=%d return" % select_copy_depth, "select_copy")
    select_copy_depth -= 1
    return res


if __name__ == "__main__":
    class A:
        a1 = "A_a1"
        a2 = "A_a2"
        def __init__(self, a1="a1", b1="b1"):
            self.a1 = a1
            self.b1 = "b1"
    
    class B:
        a = A()
        b1 = "B_b1"
        b2 = "B_b2"
        def __init__(self):
            pass

        def select_copy(self):
            return self
        
    class C:
        c1 = "C_c1"
        a = A()
        b = B()
        def __init__(self):
            pass
       
        def select_copy(self, levels=3):
            return select_copy(self, levels=levels-1)
        
    a = A() 
    b = B() 
    c = C() 
    a_copy_a = select_copy(a)
    b_copy_b = b.select_copy()
    c_copy_c = c.select_copy()
    print("End Test")
    