"""
练习 2：最小 Schema -- 合格放行，不合格报错

要练会什么：
  用 Pydantic 写第一张「入境检查表」，体验成功 vs 失败两种结果。

运行方式：
  cd demo\\PydanticSchema_demo
  pip install -r requirements.txt
  python exercise2.py

预期输出（大致）：
  [PASS] 测1: 成功 -> title='买牛奶'
  [PASS] 测2: 失败 -> Field required
  [PASS] 测3: 失败 -> Input should be a valid string  (title 必须是字符串，不能传数字)
  ---
  3/3 tests passed
"""

from __future__ import annotations

from pydantic import BaseModel, ValidationError


class TodoCreateRequest(BaseModel):
    """创建待办时，客户端 POST 的 JSON 体（最简版）"""

    title: str


def try_create(data: dict) -> tuple[bool, str]:
    """尝试校验，返回 (是否成功, 描述信息)"""
    try:
        req = TodoCreateRequest(**data)
        return True, f"title={req.title!r}"
    except ValidationError as e:
        return False, e.errors()[0]["msg"]


def run_tests() -> None:
    cases = [
        ({"title": "买牛奶"}, True, "测1"),
        ({}, False, "测2"),
        ({"title": 123}, False, "测3"),  # 类型不对：JSON 里 title 是数字，Schema 要求 str
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
