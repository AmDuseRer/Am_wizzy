"""
一键运行练习 1-4

运行方式：
  cd demo/异步ORM_demo
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
        ("exercise1", "练习 1 - 感受异步等数据库"),
        ("exercise2", "练习 2 - ORM 类代表表"),
        ("exercise3", "练习 3 - 查询筛选分页"),
        ("exercise4", "练习 4 - get_db 提交与回滚"),
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
