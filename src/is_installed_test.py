#is_installed_test.py

import sys
import is_installed

module = sys.argv[1] if len(sys.argv) > 1 else "is_installed"
print(f"is_installed: {module}")
if is_installed.is_installed(module):
    print('YES')
else:
    print('NO')
