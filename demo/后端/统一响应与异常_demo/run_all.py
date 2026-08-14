"""一键运行本目录下 Python 练习题"""
import subprocess
import sys
from pathlib import Path

scripts = ["exercise3.py"]

for name in scripts:
    path = Path(__file__).parent / name
    print(f"\n========== {name} ==========")
    result = subprocess.run([sys.executable, str(path)], check=False)
    if result.returncode != 0:
        sys.exit(result.returncode)

print("\n[OK] Python 练习题全部通过")
print("提示: 第 4 题请单独运行: node exercise4.js")
