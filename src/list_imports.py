#list_lines.py  23Jul2024  crs
"""
List lines in file that have a pattern
Hopefully to develpe a replacement for perl -ane '{.....} *.py
"""
import os,re

list_local = False      # True - list local imported files

wk_dir = os.path.dirname(__file__)  # Our directory
#wk_dir = os.path.join(wk_dir, "..", "..", "..", "resource_lib","src")
print(f"wk_dir: {os.path.normpath(wk_dir)}")
files =[f for f in os.listdir(wk_dir) if re.match(r'^.*\.py$', f)]
im_name_vals = {}
for f in files:
    fpath = os.path.join(wk_dir, f)
    with open(fpath) as  fp:
        for line in fp:
            match_import = re.match(r'^\s*import\s+(\w+(,\s*\w+)*)', line)
            match_from_import = re.match(r'^\s*from\s+(\w+)\s+import\s+(\w[\w,\s]*\w)', line)
            if match_import:
                import_name_str = match_import.group(1)
                #print(import_names)
                import_names = re.split(r',\s*', import_name_str)
                for import_name in import_names:
                    im_name_vals[import_name] = None
            elif match_from_import:
                import_name = match_from_import.group(1)
                import_val_str = match_from_import.group(2)
                import_vals = re.split(r',\s*', import_val_str)
                for iv in import_vals:
                    #print(import_name, iv)
                    im_name_vals[import_name] = iv
for import_name in sorted(im_name_vals):
    local_name = os.path.join(wk_dir, import_name+".py")
    wx_local_name = os.path.join(wk_dir, "wx_"+import_name+".py")
    if os.path.exists(local_name) or os.path.exists(wx_local_name):
        if list_local:
            print(f"    {import_name} exists locally in {os.path.basename(local_name)}")
            print("   ",import_name, im_name_vals[import_name])
    else:
        print(import_name, im_name_vals[import_name])