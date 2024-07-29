# setup_turtle_braille.py
"""
Setup turtle Braille Graphics software
    1. Setup TURTLE_BRAILLE_PATH environment variable and prepend to "PYTHONPATH"
    2. pip install required pypi modules
"""
import os
import sys
from pathlib import Path
import subprocess
import argparse

import win32con
from win32gui import SendMessage
from winreg import (
    CloseKey, OpenKey, QueryValueEx, SetValueEx,
    HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE,
    KEY_ALL_ACCESS, KEY_READ, REG_EXPAND_SZ, REG_SZ
)

from requirements_update import req_update
from is_installed import is_installed

# Program options
interactive = True
update = True
update = False
verbose = False

ppath_ev = "PYTHONPATH"    # Import path

def check_setup():
    """ Check and report current status
    :returns: True iff all is OK
    """
    if not req_update(update=False, verbose=verbose):
        print("Check FAILED")
        return False
    
    #check if some of our modules are visible
    our_mods = [
                "wx_turtle_braille",
                "select_trace",
                ]
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
    #SendMessage(
    #    win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 'Environment')

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

def get_paths(user=True):
    paths = get_env('Path').split(';')
    remove(paths, '')
    paths = unique(paths)
    return paths
    

def remove(paths, value):
    while value in paths:
        paths.remove(value)


def unique(paths):
    """ Treat / and \\ the same
    favor \\ for replacements
    :paths: list of paths
    """
    unique = []
    for value in paths:
        if value not in unique and value.replace('/','\\') not in unique:
            unique.append(value.replace('/','\\'))
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



def install_modules():
    """ Install using requirements_update
    """
    return req_update(update=update, verbose=verbose)

def add_change_tbp():
    """ Add or change turtle Braille Path
    """
    tbp_ev = "TURTLE_BRAILLE_PATH"
    tbp = os.getenv(tbp_ev)
    old_tbp = tbp
    wk_dir = os.path.dirname(__file__)
    new_tbp = wk_dir   # Default
    if interactive:
        inp = input(f""" Select Turtle Braille Base
            1 - distribution: {wk_dir}
            2 - current setting: {tbp}
            ... - full directory path anything else
            [1]:""")
        if inp == "" or inp == "1":
            new_tbp = wk_dir
        elif inp == "2":
            new_tbp = tbp
        else:
            new_tbp = inp
        
    """ Do a simple sanity check before changing
        - looking for this file in new directory
    """
    link_file = os.path.basename(__file__)
    link_via_tbp = os.path.join(new_tbp, link_file)
    if not os.path.exists(link_via_tbp):
        print(f"{link_file} not found in new directory {new_tbp} - we're suspicious - no changes")
        exit(2)

    if update:
        set_env(tbp_ev, new_tbp)        
    prev_path = get_env(ppath_ev)
    print(f"prev_path: {'\n\t'.join(prev_path.split(";"))}")
    paths = prev_path.split(';')
    if old_tbp is not None:
        remove(paths, old_tbp)
    remove(paths, '')

    paths.insert(0, new_tbp)
    paths = unique(paths)
    new_path = ";".join(paths)
    print(f"New Path: {"\n\t".join(new_path.split(";"))}")
    if update:
        set_env(ppath_ev, new_path)

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--interactive', action='store_true', default=interactive,
                    help=("Prompt user before action"
                            " (default:automatic)"))
parser.add_argument('-j', '--update', action='store_true', default=update,
                    help=("Update system"
                            " (default:Do full setup)"))
parser.add_argument('-v', '--verbose', action='store_true', default=verbose,
                    help=("Increase display of activity"
                            " (default:less printout)"))

args = parser.parse_args()             # or die "Illegal options"
interactive = args.interactive
update = args.update
verbose = args.verbose

if update:
    if not req_update(update=update, verbose=verbose):
        print("Module Requirements Update FAILED")
        exit(1)
else:
    if check_setup():
        print("Setup is OK")
    else:
        print("check_setup FAILED")
        exit(1)

add_change_tbp()
if update:
    print("Setup will NOT be complete until Computer REBOOT")
    inp = input("Reboot Now?[Y]")
    if inp == "" or inp.lower()=='y':
        print("Rebooting Now")
        os.system("shutdown /r /t 1")
else:
    print("Must rerun with --update to setup")