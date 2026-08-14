"""
练习 3：必填 vs 可选 + 默认值

要练会什么：
  区分「创建时必须填」和「更新时可以只改一部分」。
  对应项目里的 MemoCreateRequest vs MemoUpdateRequest。

运行方式：
  cd demo\\PydanticSchema_demo
  pip install -r requirements.txt
  python exercise3.py

预期输出（大致）：
  [PASS] 创建-只传title: 成功 -> {'title': '购物清单', 'content': '', 'is_pinned': False}
  [PASS] 创建-空标题: 失败 -> String should have at least 1 character
  [PASS] 创建-啥也不传: 失败 -> Field required
  [PASS] 更新-只改置顶: 成功 -> {'title': None, 'is_pinned': True}
  [PASS] 更新-空对象: 成功 -> {'title': None, 'is_pinned': None}
  ---
  5/5 tests passed
"""

from __future__ import annotations

from pydantic import BaseModel, Field, ValidationError


class MemoCreateRequest(BaseModel):
    """创建备忘录：title 必填，其余有默认值"""

    title: str = Field(..., min_length=1)
    content: str = ""
    is_pinned: bool = False


class MemoUpdateRequest(BaseModel):
    """更新备忘录：所有字段均可选（不传 = 不改）"""

    title: str | None = None
    is_pinned: bool | None = None


def check(model: type[BaseModel], data: dict, expect_ok: bool, name: str) -> None:
    try:
        obj = model(**data)
        assert expect_ok, f"{name}: expected failure but succeeded"
        print(f"[PASS] {name}: 成功 -> {obj.model_dump()}")
    except ValidationError as e:
        assert not expect_ok, f"{name}: expected success but failed: {e}"
        err = e.errors()[0]
        print(f"[PASS] {name}: 失败 -> {err['msg']}")


def run_tests() -> None:
    check(MemoCreateRequest, {"title": "购物清单"}, True, "创建-只传title")
    check(MemoCreateRequest, {"title": ""}, False, "创建-空标题")
    check(MemoCreateRequest, {}, False, "创建-啥也不传")
    check(MemoUpdateRequest, {"is_pinned": True}, True, "更新-只改置顶")
    check(MemoUpdateRequest, {}, True, "更新-空对象")

    print("---")
    print("5/5 tests passed")


if __name__ == "__main__":
    run_tests()
