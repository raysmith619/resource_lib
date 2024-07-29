# setup_turtle_braille.py
"""
Setup Turbo Braille Graphics software
    1. Setup TURBO_BRAILLE_PATH environment variable
    2. pip install required pypi modules
"""
import os
import sys
from pathlib import Path
import subprocess
import importlib
import argparse

from os import system, environ
import win32con
from win32gui import SendMessage
from winreg import (
    CloseKey, OpenKey, QueryValueEx, SetValueEx,
    HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE,
    KEY_ALL_ACCESS, KEY_READ, REG_EXPAND_SZ, REG_SZ
)

from is_installed import is_installed

# Program options
just_checking = False
just_checking = True
verbose = False

# Required installed Modules
            
install_list = ["pyttsx3",
                "pyttsx4", "wxpython", "numpy",
                "pysinewave", "sounddevice",
            ]

def check_setup():
    """ Check and report current status
    :returns: True iff all is OK
    """
    #check if modules are installed
    nmissing = 0
    for mod in install_list:
        if not is_installed(mod):
            print(f"module {mod} is missing")
            nmissing += 1
        else:
            if verbose:
                print(f"module {mod} is installed")
    if nmissing > 0:
        return False
    
    #check if some of our modules are visible
    our_mods = ["COPY_setup_turtle_braille",
                "wx_turtle_braille_link", "wx_turtle_braille",
                "select_trace", "setup_turtle_braille"]
    for our_mod in our_mods:
        if not is_installed(our_mod):
            print(f"Our mod {our_mod} is not visible")
            return False
        else:
            if verbose:
                print(f"Our mod {our_mod} is visible")
    
    return True         # Success
        
def set_env(name, value):
    key = OpenKey(HKEY_CURRENT_USER, 'Environment', 0, KEY_ALL_ACCESS)
    SetValueEx(key, name, 0, REG_EXPAND_SZ, value)
    CloseKey(key)
    SendMessage(
        win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 'Environment')

def env_keys(user=True):
    if user:
        root = HKEY_CURRENT_USER
        subkey = 'Environment'
    else:
        root = HKEY_LOCAL_MACHINE
        subkey = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
    return root, subkey


def get_env(name, user=True):
    root, subkey = env_keys(user)
    key = OpenKey(root, subkey, 0, KEY_READ)
    try:
        value, _ = QueryValueEx(key, name)
    except WindowsError:
        return ''
    return value


def remove(paths, value):
    while value in paths:
        paths.remove(value)


def unique(paths):
    unique = []
    for value in paths:
        if value not in unique:
            unique.append(value)
    return unique


def prepend_env(name, values):
    for value in values:
        paths = get_env(name).split(';')
        remove(paths, '')
        paths = unique(paths)
        remove(paths, value)
        paths.insert(0, value)
        set_env(name, ';'.join(paths))


def prepend_env_pathext(values):
    prepend_env('PathExt_User', values)
    pathext = ';'.join([
        get_env('PathExt_User'),
        get_env('PathExt', user=False)
    ])
    set_env('PathExt', pathext)



def install_modules(install_list):
    """ Install list of modules
    :install_list: list of module names
    """
    pgm_list = ["py", "-m", "pip", "install"]
    pgm_list.extend(install_list)
    print(f"Running: {pgm_list}")
    pgm_run = subprocess.Popen(pgm_list,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                )
    pgm_out, pgm_error = pgm_run.communicate()
    pgm_run.wait()
    print(f"pgm_error: {pgm_error}")
    print(f"output:\n{pgm_out.decode()}")
    
def add_change_tbp():
    """ Add or change Turbo Braille Path
    """
    tbp_ev = "TURBO_BRAILLE_PATH"
    tbp = os.getenv(tbp_ev)
    if tbp is None:
        wk_dir = os.path.dirname(__file__)
        inp = input(f"Set NEW {tbp_ev} to [wk_dir]:")
        if inp != "":
            new_tbp = inp
        else:
            new_tbp = wk_dir
    else:
        inp = input(f"Change {tbp_ev} setting?[{tbp}]:")
        if inp == "":
            print(f"Leaving {tbp_ev} unchanged: {tbp}")
            return
        
        new_tbp = inp
    inp = input(f"Change {tbp_ev} to {new_tbp}? [N]")
    if inp.lower() == "y":
        print(f"setting {tbp_ev} to {new_tbp}")
        
        """ Do a simple sanity check - looking for this file in new directory """
        link_file = os.path.basename(__file__)
        link_via_tbp = os.path.join(new_tbp, link_file)
        if not os.path.exists(link_via_tbp):
            print(f"{link_file} not found in new directory {new_tbp} - we're suspicious")
            exit(2)

        
        set_env(tbp_ev, new_tbp)
        print("To take effect MUST RESTART Shell/GUI.")

parser = argparse.ArgumentParser()
parser.add_argument('-j', '--just_checking', action='store_true', default=just_checking,
                    help=("Just ckeck Setup status"
                            " (default:Do full setup)"))
parser.add_argument('-v', '--verbose', action='store_true', default=verbose,
                    help=("Just ckeck Setup status"
                            " (default:Do full setup)"))

args = parser.parse_args()             # or die "Illegal options"

just_checking = args.just_checking
verbose = args.verbose

if just_checking:
    print("Just Checking Setup Status")
    if check_setup():
        print("Setup is OK")
        exit()
    else:
        print("check_setup FAILED")
        exit(1)
        
add_change_tbp()


install_modules(install_list)