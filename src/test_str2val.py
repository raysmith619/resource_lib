#test_str2val.py
"""
Test the str2val function
"""
from select_trace import SlTrace, SelectErrorInput, str2val

n_test = 0
n_pass = 0
n_fail = 0
show_all = True     # Show all tests

def test_it(string, exp_val, exp_equal=True, exp_except=False):
    """ Test str2val
    :string: input string
    :exp_val: expected value/type
    :exp_equal: expected equal
    :exp_except: True => exception expected
    :returns: True if OK, else False or SelectError raised
    """
    global n_test, n_pass, n_fail
    n_test += 1
    if show_all:
        t_eq_str = f" exp_equal: {exp_equal}" if not exp_equal else ""
        t_except_str = f" exp_except: {exp_except}" if exp_except else ""
        SlTrace.lg(f"{n_test:2d}: test_it {string}, exp_val: {exp_val}{t_eq_str}{t_except_str}")
    try:
        vcvt = str2val(string, exp_val)
        if exp_except:
            n_fail += 1
            SlTrace.lg(f"test_it: failed - no exception for: {string} exp_val:{exp_val}")
            return False
        
        if type(vcvt) != type(exp_val):
            n_fail += 1
            SlTrace.lg(f"test_it: failed - conversion for: {string} ({vcvt}) != exp_val:{exp_val}")
            return False
        
        if vcvt != exp_val and exp_equal:
            n_fail += 1
            SlTrace.lg(f"test_it: failed - {string} ({vcvt}) != {exp_val} when expected equal")
            return False
        
        if vcvt == exp_val and not exp_equal:
            n_fail += 1
            SlTrace.lg(f"test_it: failed - {string} ({vcvt}) == {exp_val} when not expected equal")
            return False
            
    except SelectErrorInput:
        if not exp_except:
            n_fail += 1
            SlTrace.lg(f"test_it: failed - unexpected exception for: {string} exp_val:{exp_val}")
            return False    
    
    n_pass += 1
    SlTrace.lg("Pass")    
    return True

SlTrace.lg("Testing positive cases")
test_it("1", 1)
test_it("True", True)
test_it("2.", 2.)
test_it("abc", "abc")
SlTrace.lg("Testing negative cases")
test_it("12", 1, False)
test_it("False", True, False)
test_it("23.", 2., False)
test_it("abcd", "abc", False)
SlTrace.lg("Testing exception cases")
test_it("12x", 1, exp_except=True)
test_it("Z", True, exp_except=True)
test_it("2x3.", 2, exp_except=True)

SlTrace.lg("\nForce Test Fail")
test_it("1x", 1)
test_it("1", 2)
SlTrace.lg(f"tests: {n_test} passed: {n_pass} failed: {n_fail}")