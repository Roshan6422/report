import os
import sys

# Reconfigure stdout for Unicode support on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

path = r"D:\PROJECTS\ha\english\New folder"
if os.path.exists(path):
    print(f"Listing files in {path}:")
    for f in os.listdir(path):
        if f.lower().endswith(".pdf"):
            print(f"File: {f}")
            print(f"  Hex: {f.encode('utf-8').hex()}")
            print(f"  Repr: {f!r}")
else:
    print(f"Path not found: {path}")
