"""
一键运行全部 5 道 Depends 练习题

运行方式：
  cd demo/Depends_demo
  pip install -r requirements.txt
  python run_all.py
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(base_dir))

    modules = [
        ("exercise1", "练习 1 - 纯 Python 注入"),
        ("exercise2", "练习 2 - 基础 Depends"),
        ("exercise3", "练习 3 - 链式 Depends"),
        ("exercise4", "练习 4 - yield 借还"),
        ("exercise5", "练习 5 - 迷你综合"),
    ]

    passed = 0
    for module_name, title in modules:
        print("=" * 60)
        print(title)
        print("=" * 60)
        module = importlib.import_module(module_name)
        module.run_tests()
        passed += 1
        print()

    print("=" * 60)
    print(f"ALL PASSED: {passed}/{len(modules)} exercises")
    print("=" * 60)


if __name__ == "__main__":
    main()
