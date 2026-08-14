"""
练习 3：前后端「不对齐」 vs 「对齐」（待办标题 1-200 字）

要练会什么：
  前端规则和后端 Schema 数字不一致时，用户会遇到「网页过了、提交却报错」；
  改成同一套标准后，两边结果一致。

运行方式：
  cd demo\\表单校验_demo
  pip install -r requirements.txt
  python exercise3.py

对照项目文件：
  web/src/views/TodoListView.vue  （rules.title）
  server/app/schemas/todo.py      （TodoCreateRequest.title）
"""

from __future__ import annotations

from pydantic import BaseModel, Field, ValidationError


class TodoCreateRequest(BaseModel):
    """与项目 todo.py 一致"""

    title: str = Field(..., min_length=1, max_length=200)


def validate_title_frontend(title: str, max_len: int) -> str | None:
    """模拟前端 rules；max_len 故意可配，演示不对齐"""
    if not title:
        return "请输入标题"
    if len(title) > max_len:
        return f"标题不能超过 {max_len} 字"
    return None


def validate_title_backend(title: str) -> str | None:
    try:
        TodoCreateRequest(title=title)
        return None
    except ValidationError:
        return "标题长度 1-200"


def run_tests() -> None:
    long_title = "A" * 300

    # --- 阶段 A：故意不对齐（前端 500，后端 200）---
    print("阶段 A：前后端不对齐（前端 max=500，后端 max=200）")
    fe_err = validate_title_frontend(long_title, max_len=500)
    be_err = validate_title_backend(long_title)
    assert fe_err is None, "前端应认为 300 字标题 OK"
    assert be_err is not None, "后端应拒绝 300 字标题"
    print(f"[PASS] 300字标题: 前端={fe_err or 'OK'}, 后端={be_err}")
    print("       -> 用户困惑：网页没报错，一提交服务器却拒绝")

    # --- 阶段 B：修到对齐（前端也改成 200）---
    print()
    print("阶段 B：前后端对齐（前端 max=200，后端 max=200）")
    cases = [
        ("", False, "测1-空标题"),
        ("买牛奶", True, "测2-正常标题"),
        ("A" * 200, True, "测3-200字边界"),
        ("A" * 201, False, "测4-201字超长"),
    ]

    passed = 1  # 阶段 A 算 1 条
    for title, expect_ok, name in cases:
        fe = validate_title_frontend(title, max_len=200)
        be = validate_title_backend(title)
        fe_ok = fe is None
        be_ok = be is None
        assert fe_ok == expect_ok and be_ok == expect_ok, (
            f"{name}: fe={fe}, be={be}, expect_ok={expect_ok}"
        )
        print(f"[PASS] {name}: 前端={fe or 'OK'}, 后端={be or 'OK'}")
        passed += 1

    print("---")
    print(f"{passed}/{len(cases) + 1} checks passed")


if __name__ == "__main__":
    run_tests()
