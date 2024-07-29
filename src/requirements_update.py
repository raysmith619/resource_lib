#requirements_update.py    28Jul2024  crs
""" Test current module list against given requirements
Update requirements as requested
"""
import os
import re
import pip
import subprocess
from pathlib import Path

cur_dir = os.path.join(os.path.dirname(__file__))
do_verbose = False

def req_update(target=None, current=None, update=True,
               force=False, verbose=False):
    """ Check / Update installed modules
    :target: target requirements file
            default: requrements.txt
    :current: current requirements file default: freeze getting current
    :update: update modules with install default: True - update
    :force: update all target requirements, ignore current/target differences
        default: False - just missing/out-of-date requirements
    :verbose: True - show modules, Default: False
    :returns: True iff OK
    """
    global do_verbose           # verbose - we should probably make this into a class
    do_verbose = verbose
    if current is None:
        cur_req_str = freeze_call()
    else:
        cur_req_path = os.path.join(cur_dir, current)
        cur_req_str = Path(cur_req_path).read_text()

    if force:
        cur_req_str = "" # Assume no preexisting modules
    
    target_req_file = target
    if target_req_file is None:
        target_req_file = "requirements.txt"
    target_req_path = os.path.join(cur_dir, target_req_file)
    with open(target_req_path, 'rt') as fp:
        target_req_str = fp.read()
    cur_req_mod_d = req_str_to_dict(cur_req_str)
    target_req_mod_d = req_str_to_dict(target_req_str)
    need_upgrade_d = get_upgrade(cur_req_mod_d, target_req_mod_d)
    if force or len(need_upgrade_d) > 0:
        if force:
            upgrade_d = target_req_mod_d
        else:
            upgrade_d = need_upgrade_d
        
        upgrade_req_str = ""
        for mod in upgrade_d:
            ver_list = upgrade_d[mod]
            vers_str = ""
            for vn in ver_list:
                if vers_str != "":
                    vers_str += "."
                vers_str += str(vn)
            mod_str = mod + "==" + vers_str
            upgrade_req_str += mod_str+"\n"
        print("pip update string:")
        print(upgrade_req_str)
        if update:
            print("Upgrading")
            update_req_path = os.path.join(cur_dir, "requirements_update.txt")
            with open(update_req_path, 'w') as fp:
                fp.write(upgrade_req_str)
            pip_install_pgm_list = ["python", "-m", "pip", "install", "-r", update_req_path]
            run_ret = subprocess.run(pip_install_pgm_list,
                        cwd=cur_dir,capture_output=True, text=True)
            ret_code = run_ret.returncode
            out_str = run_ret.stdout
            err_str = run_ret.stderr
            if ret_code != 0:
                print("pip install requirements call failed")
                print(f"err:\n{err_str}")
                print(f"out:\n{out_str}")
                return False
    else:
        return True     # Success
        
        
        
def get_upgrade(cur_req_mod_d, target_req_mod_d):
    """ Find set of target module members in need of upgrade
    :cur_req_mod_d: dictionary of current required modules
    :target_req_mod_d: dictionary of target required modules
    :returns: dictionary of modules in need of upgrade
    """
    if do_verbose:
        print(f"cur_req_mod_d:\n{mod_lst_str(cur_req_mod_d)}")
        print(f"target_req_mod_d:\n{mod_lst_str(target_req_mod_d)}")
    need_update_d = {}
    for tmod in target_req_mod_d:
        if tmod not in cur_req_mod_d:
            need_update_d[tmod] = target_req_mod_d[tmod]
            continue
        
        if target_req_mod_d[tmod] > cur_req_mod_d[tmod]:
            need_update_d[tmod] = target_req_mod_d[tmod]
    if do_verbose:
        print(f"need_update:\n{mod_lst_str(need_update_d)}")
        
    return need_update_d

def mod_lst_str(mod_lst):
    """ Get string representation of mod list dictionary
    :mod_lst: dictionary of mod_name : version list
    :returns: string representation
    """
    mod_dict_str = ""
    for mod_name in mod_lst:
        mod_ver = ".".join(map(str, mod_lst[mod_name]))
        mod_line = f"    {mod_name}=={mod_ver}\n"
        mod_dict_str += mod_line
    return mod_dict_str
    
def req_str_to_dict(req_str):
    """ Convert requirement string to dictionary of module:[version numbers]
        string format
            module==1.2.3
            module==4.5
            ...
        dictionary format:
            module : [v.v.v]
            module : [v,v]
        return module version dictionary
        """
    mod_ver_d = {}
    for module_str in req_str.split("\n"):
        mod_match = re.match(r'^(\w+)==((\d+)((\.\d+)*))', module_str)
        if mod_match is not None:
            module = mod_match.group(1)
            module_ver1 = mod_match.group(3)
            module_sub_ver = mod_match.group(4)
            #print(f"module_line: {module_str} {module} '{module_ver1}' '{module_sub_ver}' ")
            mod_sub_ver_match = re.match(r'(\.\d+)+', module_sub_ver)
            ver_list = [int(module_ver1)]
            if mod_sub_ver_match is not None:
                mod_sub_vers = re.findall(r'\.\d+', module_sub_ver)
                for sub_ver in mod_sub_vers:
                    ver_list.append(int(sub_ver[1:]))
            mod_ver_d[module] = ver_list
            #print(f"module_line: {module_str} {module}: {mod_ver_d[module]} ")
    return mod_ver_d        

def freeze_call(cur_dir=None):
    """ Call pip freeze to get requirements
    :cur_dir: run directory
            Default: this file's directory
    :returns: freeze output string, None if error
    """
    pgm_list = ["python", "-m", "pip", "freeze"]
    cur_dir = os.path.join(os.path.dirname(__file__))

    run_ret = subprocess.run(pgm_list,
                   cwd=cur_dir,capture_output=True, text=True)
    ret_code = run_ret.returncode
    out_str = run_ret.stdout
    err_str = run_ret.stderr
    if ret_code != 0:
        print("requirement test freeze call failed")
        print(f"err:\n{err_str}")
        print(f"out:\n{out_str}")
        return None
    
    return out_str
    
if __name__ == '__main__':
    print("Self Test")
    print("Using requirement.txt, freeze")
    req_update(update=False, verbose=True)
    print("Using requirement_t1.txt, freeze")
    req_update(update=False, verbose=True, target="requirements_t1.txt")
    print("Using requirement_t1.txt, freeze - Update attempt - should fail")
    req_update(target="requirements_t1.txt")
    