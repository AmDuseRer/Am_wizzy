"""
表单校验（前后端对齐）-- 一键运行 4 道练习题

运行方式（Windows PowerShell）：
  cd demo\\表单校验_demo
  pip install -r requirements.txt
  python run_all.py
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

# Windows 控制台默认 GBK，强制 UTF-8 避免中文乱码
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(base_dir))

    modules = [
        ("exercise1", "练习 1 - 前端校验（模拟 LoginView rules）"),
        ("exercise2", "练习 2 - 后端校验（LoginRequest Schema）"),
        ("exercise3", "练习 3 - 不对齐 vs 对齐（待办标题）"),
        ("exercise4", "练习 4 - 迷你综合（前端先验 + 后端再验）"),
    ]

    for module_name, title in modules:
        print("=" * 60)
        print(title)
        print("=" * 60)
        module = importlib.import_module(module_name)
        module.run_tests()
        print()

    print("=" * 60)
    print(f"ALL PASSED: {len(modules)}/{len(modules)} exercises")
    print("=" * 60)
    print()
    print("练完后对照项目文件：")
    print("  1. web/src/views/LoginView.vue  +  server/app/schemas/auth.py")
    print("  2. web/src/views/TodoListView.vue + server/app/schemas/todo.py")
    print("  3. web/src/views/MemoListView.vue + server/app/schemas/memo.py")


if __name__ == "__main__":
    main()
