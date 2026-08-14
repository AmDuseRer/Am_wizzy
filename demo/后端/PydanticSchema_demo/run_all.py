"""
一键运行 Pydantic Schema 练习题（第 2、3、5、6 题）

运行方式：
  cd demo\\PydanticSchema_demo
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
        ("exercise2", "练习 2 - 最小 Schema"),
        ("exercise3", "练习 3 - 必填 vs 可选"),
        ("exercise5", "练习 5 - 枚举/格式 pattern"),
        ("exercise6", "练习 6 - 读懂 ValidationError"),
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
