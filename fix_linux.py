#!/usr/bin/env python3
# update_for_linux.py - Modify files for Linux compatibility

import os
import re


def fix_file(file_path):
    print(f"Fixing file: {file_path}")
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False

    with open(file_path, 'r') as f:
        content = f.read()

    # Common Windows-specific patterns to replace
    patterns = [
        # Remove Windows-specific startupinfo block
        (r'# Use detached process on Windows[^}]*?startupinfo\.wShowWindow = 0  # SW_HIDE\s*\n', ''),
        # Remove Windows-specific creationflags parameter
        (r',\s*creationflags=subprocess\.CREATE_NO_WINDOW', ''),
        # Remove startupinfo parameter
        (r',\s*startupinfo=startupinfo', ''),
        # Remove Windows-specific CREATE_NEW_PROCESS_GROUP block
        (r'# Use CREATE_NEW_PROCESS_GROUP[^}]*?flags = subprocess\.CREATE_NEW_PROCESS_GROUP\s*\n', ''),
        # Remove creationflags=flags parameter
        (r',\s*creationflags=flags', ''),
        # Fix any startupinfo = None lines to be conditional
        (r'startupinfo = None\s*\nif os\.name == \'nt\':', 'if os.name == \'nt\':')
    ]

    original_content = content
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    else:
        print(f"No changes needed for {file_path}")
        return False


files_fixed = 0

# Fix ams.py
if fix_file('ams.py'):
    files_fixed += 1

# Fix website/app.py
if fix_file('website/app.py'):
    files_fixed += 1

# Fix collector.py if it exists
if os.path.exists('collector.py'):
    if fix_file('collector.py'):
        files_fixed += 1

print(f"\nCompleted! {files_fixed} file(s) modified for Linux compatibility.")
print("You can now use these files on your Linux system.")