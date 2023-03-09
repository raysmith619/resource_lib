# format_exception.py    03Mar2023  crs, from Stackoverflow

"""
exception string
Example:
    from format_exception import format_exception
    
    
    try:
    except AssertionError as err_msg:
        SlTrace.lg(f"Test {test_desc} FAILED: {err_msg}")
    except Exception as e:
        SlTrace.lg(f"Unexpected exception: {e}")
        SlTrace.lg("Printing the full traceback as if we had not caught it here...")
        SlTrace.lg(format_exception(e))
"""

import os
import traceback
import sys

def format_exception(e):
    exception_list = traceback.format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
    exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))

    exception_str = "Traceback (most recent call last):\n"
    exception_str += "".join(exception_list)
    # Removing the last \n
    exception_str = exception_str[:-1]

    return exception_str

    