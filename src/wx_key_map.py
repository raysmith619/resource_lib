#wx_key_map.py
import wx

keyMap = {}
for varName in vars(wx):
    if "&" in varName:
        continue
    if varName.startswith("WXK_"):
        keyMap[varName] = getattr(wx, varName)

for v in sorted(keyMap.values()):
    for key in keyMap:
        if v == keyMap[key]:
            print(v,key)



