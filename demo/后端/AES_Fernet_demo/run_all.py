"""
一键运行 AES/Fernet 练习 1、2

运行方式（Windows PowerShell）：
  cd demo/AES_Fernet_demo
  pip install -r requirements.txt
  python run_all.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXERCISES = ["exercise1.py", "exercise2.py"]


def main() -> None:
    root = Path(__file__).resolve().parent
    for name in EXERCISES:
        path = root / name
        print(f"\n{'=' * 50}")
        print(f"运行 {name}")
        print("=" * 50)
        result = subprocess.run([sys.executable, str(path)], cwd=str(root))
        if result.returncode != 0:
            raise SystemExit(result.returncode)
    print(f"\n{'=' * 50}")
    print("练习 1、2 全部通过")
    print("=" * 50)


if __name__ == "__main__":
    main()
