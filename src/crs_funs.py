# crs_funs.py    05Apr2020    crs
""" Our functions
Useful to us 
"""
import re 
from functools import cmp_to_key

from select_error import SelectError, SelectErrorInput

def anumcmp(a,b):
    """ Alphanumeric comaprison
    Treat as numeric comparison if a and b are numeric else alpha compare
     "12" > "3"
    :returns: 1,0,-1 if a>b, a==b, a<b    
     """
    if re.match(r'^\d+$', a) and re.match(r'^\d+$', b):
        cmp = int(a) - int(b)
        if cmp > 0:
            return 1
        if cmp < 0:
            return -1
        return 0
    if a == b:
        return 0
    
    return 1 if a > b else -1
 
def dotcmp(a,b):
    """ compare doted strings alphanumeric with sections within dots
        considered as numbers if both parts are strictly numeric
        e.g.  a.123.b is greater than a.33.b
    :a: first string
    :b: second string
    :returns: 1,0,-1 if a>b, a==b, a<b
    """
    a_dots = a.split(".")
    b_dots = b.split(".")
    for i in range(len(a_dots)):
        asec = a_dots[i]
        if i >= len(b_dots):
            return 1        # a longer
        bsec = b_dots[i]
        cmp = anumcmp(asec, bsec)
        if cmp > 0:
            return 1
        
        if cmp < 0:
            return -1
    if len(b_dots) > len(a_dots):
        return -1
    
    return 1


def dotcmp_keyfunc():
    """ Return dotcmp as a key function for sorted
    """
    return cmp_to_key(dotcmp)

def dot_sorted(lst):
    """ Sort list of dotted text strings
    :lst: list of text strings
    :returns: sorted list 1.9.1 before 1.10.1
    """
    srt_list = sorted(lst, key=dotcmp_keyfunc())
    return srt_list

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise SelectError('Not a recognized Boolean value %s' % v)

    
def str2val(string, value_or_type):
    """ Convert string to value of type default
    :value_type: default value if string is None or variable type
            used as type expected
    :returns: converted value
            throws SelectErrorInput if conversion error
    """
    try:
        if isinstance(value_or_type, str) or value_or_type is str:
            return string
    
        if isinstance(value_or_type, bool) or value_or_type is bool:
            return str2bool(string)
            
        if isinstance(value_or_type, int) or value_or_type is int:
            return int(float(string))       # Treat floats as ints
        
        if isinstance(value_or_type, float) or value_or_type is float:
            return float(string)
    except Exception:
        ###SlTrace.lg(f"=>str2val input {string} error for type:{type(value)}")
        pass
    
    raise SelectErrorInput(f"str2val input {string} error for type:{type(value_or_type)}")

if __name__ == "__main__":
    from select_trace import SlTrace
    
    def test_it(lin):
        """ Test (actually exercise) on list
        """
        SlTrace.lg(f"List: {lin}")
        srt_list = dot_sorted(lin)
        SlTrace.lg(f"Sorted list: {srt_list}")
        SlTrace.lg()

    SlTrace.lg("Testing dotcmp")
    dot_list = ["a.b.c", "1.2.3", "4.5.6", "7.8.9", "10.11.12", "13.14", "10.11", "4.5", "1", "2"]
    test_it(dot_list)
    
    dot2 = ["a1.b1.c1", "a.10", "a.2", "a.3", "a.21.c", "b.23.c", "b.100.c.d", "a.100.1"]
    test_it(dot2)
    dot2 = ["a1.b1.c1", "a.10", "a.10.1", "a.10.10", "a.9.10", "a.9", "a.2", "a.3", "a.21.c", "b.23.c", "b.100.c.d", "a.100.1"]
    test_it(dot2)
    SlTrace.lg("End of test")
    
