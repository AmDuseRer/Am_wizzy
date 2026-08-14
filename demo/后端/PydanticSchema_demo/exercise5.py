"""
练习 5：枚举/格式 -- 只允许固定几个值

要练会什么：
  用 pattern 限制字段只能是规定值。
  对应项目里待办的 priority、status 字段。

运行方式：
  cd demo\\PydanticSchema_demo
  pip install -r requirements.txt
  python exercise5.py

预期输出（大致）：
  [PASS] 测1: 成功 -> {'title': '写报告', 'priority': 'high'}
  [PASS] 测2: 失败 -> String should match pattern ...
  [PASS] 测3: 成功 -> {'title': '写报告', 'priority': 'medium'}
  [PASS] 测4: 失败 -> String should have at least 1 character
  ---
  4/4 tests passed
"""

from __future__ import annotations

from pydantic import BaseModel, Field, ValidationError


class TodoCreateRequest(BaseModel):
    """创建待办：priority 只能是 low / medium / high"""

    title: str = Field(..., min_length=1, max_length=200)
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")


def try_create(data: dict) -> tuple[bool, str]:
    try:
        req = TodoCreateRequest(**data)
        return True, str(req.model_dump())
    except ValidationError as e:
        err = e.errors()[0]
        return False, err["msg"]


def run_tests() -> None:
    cases = [
        ({"title": "写报告", "priority": "high"}, True, "测1"),
        ({"title": "写报告", "priority": "urgent"}, False, "测2"),
        ({"title": "写报告"}, True, "测3"),
        ({"title": "", "priority": "low"}, False, "测4"),
    ]

    passed = 0
    for data, expect_ok, name in cases:
        ok, detail = try_create(data)
        assert ok == expect_ok, f"{name}: expected ok={expect_ok}, got ok={ok}, detail={detail}"
        status = "成功" if ok else "失败"
        print(f"[PASS] {name}: {status} -> {detail}")
        passed += 1

    print("---")
    print(f"{passed}/{len(cases)} tests passed")


if __name__ == "__main__":
    run_tests()
