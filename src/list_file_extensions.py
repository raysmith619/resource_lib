#list_file_extensions.py  30Jul2024  crs
"""
List files which have extensions
"""
import os
import sys
import re
import textwrap

#File types blocked by Gmail are:
ext_blocked_str = """
.ade, .adp, .apk, .appx, .appxbundle, .bat,
.cab, .chm, .cmd, .com, .cpl, .diagcab,
.diagcfg, .diagpkg, .dll, .dmg, .ex, .ex_,
.exe, .hta, .img, .ins, .iso, .isp, .jar,
.jnlp, .js, .jse, .lib, .lnk, .mde, .mjs,
.msc, .msi, .msix, .msixbundle, .msp, .mst,
.nsh, .pif, .ps1, .scr, .sct, .shb, .sys,
.vb, .vbe, .vbs, .vhd, .vxd, .wsc, .wsf,
.wsh, .xll,
"""
search_dir = r"C:\Users\raysm\vscode\Introduction-To-Programming\src"
search_dir = r"C:\Users\Owner\OneDrive\Desktop\intro_2024b"
search_dir = "."
if len(sys.argv) > 1:
    search_dir = sys.argv[1]
else:
    inp = input(f"Enter search directory[{search_dir}]:")
    if inp != "":
        search_dir = inp
if not os.path.exists(search_dir):
    print(f"Can't find {search_dir}")
    exit(1)

if not os.path.isdir(search_dir):
    print(f"{search_dir} is not a directory")
    exit(2)
    
raw_exts = re.findall(r'\.\w+', ext_blocked_str)
exts = [rext[1:] for rext in raw_exts]
print(textwrap.fill(f"exts: {" ".join(exts)}", width=60))

for root, dirs, files in os.walk(search_dir):
    for file in files:
        for ext in exts:
            if file.endswith("."+ext):
                print(ext, os.path.join(root, file))

