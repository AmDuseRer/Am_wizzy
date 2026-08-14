"""
练习 1：理解「注入」概念（纯 Python，无需 FastAPI）

要练会什么：
  函数自己不准备工具，外面先准备好再传进来。
  这相当于 Depends 的核心思想，只是这里由我们自己写调度代码。

运行方式：
  python exercise1.py

预期输出：
  [PASS] morning greeting
  [PASS] evening greeting
  ---
  早上好，小明！
  晚上好，小红！
"""

from __future__ import annotations


def say_hello(name: str, greeting: str) -> str:
    """业务函数：只负责打招呼，不关心 greeting 从哪来"""
    return f"{greeting}，{name}！"


def prepare_morning() -> str:
    return "早上好"


def prepare_evening() -> str:
    return "晚上好"


def run_with_inject(prepare_fn, name: str) -> str:
    """
    调度员：相当于 FastAPI + Depends 帮你干的事
    1. 先调用 prepare_fn 拿到依赖
    2. 再传给业务函数
    """
    greeting = prepare_fn()
    return say_hello(name, greeting)


def run_tests() -> None:
    result_morning = run_with_inject(prepare_morning, "小明")
    result_evening = run_with_inject(prepare_evening, "小红")

    assert result_morning == "早上好，小明！", f"unexpected: {result_morning}"
    assert result_evening == "晚上好，小红！", f"unexpected: {result_evening}"

    print("[PASS] morning greeting")
    print("[PASS] evening greeting")
    print("---")
    print(result_morning)
    print(result_evening)


if __name__ == "__main__":
    run_tests()
