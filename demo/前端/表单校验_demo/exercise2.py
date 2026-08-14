"""
练习 2：模拟「后端校验」（对应 auth.py 的 LoginRequest）

要练会什么：
  数据到服务器门口再查一遍；有人绕过网页直接发请求，后端仍能拦住。

运行方式：
  cd demo\\表单校验_demo
  pip install -r requirements.txt
  python exercise2.py

对照项目文件：
  server/app/schemas/auth.py  （LoginRequest）
"""

from __future__ import annotations

from pydantic import BaseModel, Field, ValidationError


class LoginRequest(BaseModel):
    """与项目 auth.py 完全一致"""

    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


def try_login(data: dict) -> tuple[bool, str]:
    try:
        req = LoginRequest(**data)
        return True, f"username={req.username!r}"
    except ValidationError as e:
        return False, e.errors()[0]["msg"]


def run_tests() -> None:
    cases = [
        ({"username": "admin", "password": "Admin@123"}, True, "测1-正常登录"),
        ({"username": "", "password": "Admin@123"}, False, "测2-用户名为空"),
        ({"username": "admin", "password": "12345"}, False, "测3-密码太短"),
        ({"username": 123, "password": "Admin@123"}, False, "测4-用户名类型错误"),
    ]

    passed = 0
    for data, expect_ok, name in cases:
        ok, detail = try_login(data)
        assert ok == expect_ok, f"{name}: expected ok={expect_ok}, detail={detail}"
        status = "OK" if ok else "422"
        print(f"[PASS] {name}: {status} -> {detail}")
        passed += 1

    print("---")
    print(f"{passed}/{len(cases)} tests passed")


if __name__ == "__main__":
    run_tests()
