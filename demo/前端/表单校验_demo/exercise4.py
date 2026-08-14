"""
练习 4：迷你综合题 -- 前端先验 -> 发请求 -> 后端再验

要练会什么：
  串起来完整流程，理解「前端管体验、后端管安全、规则要对齐」。

运行方式：
  cd demo\\表单校验_demo
  pip install -r requirements.txt
  python exercise4.py

对照项目文件：
  web/src/views/LoginView.vue   （validate + handleLogin）
  server/app/schemas/auth.py    （LoginRequest）
  web/src/stores/auth.js        （login 发请求）
"""

from __future__ import annotations

from pydantic import BaseModel, Field, ValidationError


# ---------- 后端：入境检查表（auth.py）----------
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


def backend_login(data: dict) -> dict:
    """模拟 API：校验通过返回 token，否则 422"""
    try:
        req = LoginRequest(**data)
    except ValidationError as e:
        return {"ok": False, "status": 422, "detail": e.errors()}
    return {"ok": True, "status": 200, "token": f"fake-token-for-{req.username}"}


# ---------- 前端：提交前先验（LoginView.vue rules）----------
def frontend_validate(form: dict) -> list[str]:
    errors: list[str] = []
    username = form.get("username", "")
    password = form.get("password", "")

    if not username:
        errors.append("请输入用户名")
    elif len(username) < 2 or len(username) > 50:
        errors.append("用户名长度 2-50 字符")

    if not password:
        errors.append("请输入密码")
    elif len(password) < 6 or len(password) > 100:
        errors.append("密码长度 6-100 字符")

    return errors


def submit_login(form: dict) -> dict:
    """模拟 LoginView.vue 的 handleLogin"""
    errors = frontend_validate(form)
    if errors:
        return {"ok": False, "stage": "frontend", "messages": errors}
    result = backend_login(form)
    return {"stage": "backend", **result}


def run_tests() -> None:
    passed = 0

    # 测1：正常登录
    r = submit_login({"username": "admin", "password": "Admin@123"})
    assert r["stage"] == "backend" and r["ok"] is True and "token" in r
    print(f"[PASS] 正常登录: stage=backend, token={r['token']}")
    passed += 1

    # 测2：密码太短，前端拦住
    r = submit_login({"username": "admin", "password": "123"})
    assert r["stage"] == "frontend" and r["ok"] is False
    assert "token" not in r
    print(f"[PASS] 密码太短: stage=frontend, messages={r['messages']}")
    passed += 1

    # 测3：绕过前端，直打后端
    r = backend_login({"username": "x", "password": "1"})
    assert r["ok"] is False and r["status"] == 422
    print(f"[PASS] 绕过前端直打后端: status=422, 后端仍拒绝")
    passed += 1

    # 测4（进阶）：故意不对齐 -- 前端 4 字、后端 6 字
    def frontend_validate_loose(form: dict) -> list[str]:
        errors: list[str] = []
        if len(form.get("password", "")) < 4:
            errors.append("密码至少 4 字")
        return errors

    form = {"username": "admin", "password": "12345"}  # 5 字
    fe_ok = len(frontend_validate_loose(form)) == 0
    be_result = backend_login(form)
    assert fe_ok is True and be_result["ok"] is False
    print(f"[PASS] 不对齐演示: 前端放行(5字), 后端拒绝 status={be_result['status']}")
    passed += 1

    print("---")
    print(f"{passed}/4 tests passed")


if __name__ == "__main__":
    run_tests()
