"""
练习 6：读懂报错 -- 像前端一样知道「错在哪」

要练会什么：
  校验失败时，Pydantic 会告诉你哪个字段、什么规则、什么值。
  FastAPI 返回 422 时也是这类信息。

运行方式：
  cd demo\\PydanticSchema_demo
  pip install -r requirements.txt
  python exercise6.py

预期输出（大致）：
  一共 2 个错误：
    字段: ('ids',)
    原因: List should have at least 1 item after validation, not 0
    传入值: []
    ---
    字段: ('status',)
    原因: String should match pattern '^(pending|completed)$'
    传入值: done
    ---
  [PASS] 检测到 2 个校验错误
  ---
  1/1 tests passed
"""

from __future__ import annotations

from pydantic import BaseModel, Field, ValidationError


class TodoBatchUpdateRequest(BaseModel):
    """批量更新待办：ids 不能为空，status 只能是 pending 或 completed"""

    ids: list[int] = Field(..., min_length=1)
    status: str = Field(..., pattern="^(pending|completed)$")


def run_tests() -> None:
    bad_data = {"ids": [], "status": "done"}

    try:
        TodoBatchUpdateRequest(**bad_data)
        raise AssertionError("expected ValidationError but validation passed")
    except ValidationError as e:
        errors = e.errors()
        print(f"一共 {len(errors)} 个错误：")
        for err in errors:
            print(f"  字段: {err['loc']}")
            print(f"  原因: {err['msg']}")
            print(f"  传入值: {err.get('input')}")
            print("  ---")

        assert len(errors) == 2, f"expected 2 errors, got {len(errors)}"

        locs = {tuple(err["loc"]) for err in errors}
        assert ("ids",) in locs, "missing error for ids"
        assert ("status",) in locs, "missing error for status"

        print(f"[PASS] 检测到 {len(errors)} 个校验错误")

    print("---")
    print("1/1 tests passed")


if __name__ == "__main__":
    run_tests()
