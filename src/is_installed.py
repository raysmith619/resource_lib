#is_installed.py    25Jul2024  crs, Author
""" 
Check if python module is installed
Check is done in a separate file so the check is done in
a new process in order to look a new context
"""
import os
import sys
import importlib
import subprocess

# Markers sent within stdout text to insure recognition
YES_MARKER = "||| YES - MODULE FOUND |||"
NO_MARKER = "||| NO  - MODULE MISSING |||"

def is_installed_local(module):
    """ Check if installed
    :module: module name
    """
    if module == "wxpython":
        module = "wx"       # Different import name
        
    importlib.invalidate_caches()   # Incase newly installed
    try:
        mod = importlib.import_module(module)
        if mod is None:
            print(f"module: {module} is None")
            return False
    except Exception as e:
        print(f"module: {module} Error: {e}")
        return False
    
    return True


def is_installed(module):
    """ Check if installed
    Does the import is a called process to test the basic environment
    :module: module name
    """
    src_dir = os.path.dirname(__file__)
    up_dir = os.path.dirname(src_dir)   # not with all src files
    is_installed_pgm = os.path.join(src_dir, 'is_installed.py')
    res = subprocess.run(['python', is_installed_pgm, module],
                    cwd=up_dir,
                    capture_output=True, text=True)
    stdout = res.stdout
    if YES_MARKER in stdout:
        return True
    else:
        print("\nERROR")
        print(f"is_installed_pgm: {is_installed_pgm}")
        print(f"    cwd:{up_dir}")
        print(f"    {module}: stdout: {stdout}")
        print(f"    {module}: stderr: {res.stderr}")
    return False


if __name__ == '__main__':
    
    module = sys.argv[1] if len(sys.argv) > 1 else "wx_turtle_braille"
    if is_installed_local(module):
        print(YES_MARKER)
    else:
        print(NO_MARKER)

    
    