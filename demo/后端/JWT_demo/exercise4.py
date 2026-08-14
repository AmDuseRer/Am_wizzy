"""
练习 4：拼成「登录 -> 访问 -> 登出」最小流程

要练会什么：
  把练习 2（JWT 验签）和练习 3（白名单）合在一起：
  登录发 token 并登记白名单；访问时先验 JWT 再查白名单；登出作废。

运行方式（Windows PowerShell）：
  cd demo/JWT_demo
  pip install -r requirements.txt
  python exercise4.py

预期输出（大致）：
  [PASS] 正确密码登录成功
  [PASS] 错误密码登录失败
  [PASS] 登录后 get_current_user 成功
  [PASS] 登出后 get_current_user 失败
  [PASS] 禁用账号后访问失败
  ---
  全部测试通过

练完对照项目文件：
  server/app/services/auth_service.py  -> login / logout
  server/app/core/deps.py              -> get_current_user
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import jwt

SECRET = "practice-secret-for-jwt-demo-only-32b"
ALGORITHM = "HS256"

# 模拟 users 表
users: dict[str, dict] = {
    "zhang.san": {
        "id": 1,
        "password": "123456",
        "role": "user",
        "is_active": True,
    }
}

# 模拟 user_tokens 白名单
whitelist: dict[str, dict] = {}


def create_token(user_id: int, username: str, role: str) -> tuple[str, str]:
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "jti": jti,
        "exp": expire,
    }
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    return token, jti


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET, algorithms=[ALGORITHM])


def add_to_whitelist(jti: str, user_id: int) -> None:
    whitelist[jti] = {"user_id": user_id, "is_revoked": False}


def revoke_token(jti: str) -> None:
    if jti in whitelist:
        whitelist[jti]["is_revoked"] = True


def is_token_allowed(jti: str, user_id: int) -> bool:
    record = whitelist.get(jti)
    if not record:
        return False
    if record["user_id"] != user_id:
        return False
    return not record["is_revoked"]


def login(username: str, password: str) -> str:
    user = users.get(username)
    if not user or user["password"] != password:
        raise Exception("用户名或密码错误")
    if not user["is_active"]:
        raise Exception("账号已被禁用")

    token, jti = create_token(user["id"], username, user["role"])
    add_to_whitelist(jti, user["id"])
    return token


def get_current_user(token: str) -> dict:
    if not token:
        raise Exception("未提供有效的认证令牌")

    payload = decode_token(token)
    user_id = int(payload.get("sub", 0))
    jti = payload.get("jti", "")
    username = payload.get("username", "")

    if not is_token_allowed(jti, user_id):
        raise Exception("令牌已失效，请重新登录")

    user = users.get(username)
    if not user or not user["is_active"]:
        raise Exception("用户不存在或已被禁用")

    return {"id": user_id, "username": username, "role": user["role"]}


def logout(token: str) -> None:
    payload = decode_token(token)
    jti = payload.get("jti", "")
    revoke_token(jti)


def run_test(name: str, fn) -> None:
    try:
        fn()
        print(f"[PASS] {name}")
    except AssertionError as exc:
        print(f"[FAIL] {name}: {exc}")
        raise SystemExit(1)


def main() -> None:
    # 每个测试前重置状态
    users["zhang.san"] = {
        "id": 1,
        "password": "123456",
        "role": "user",
        "is_active": True,
    }
    whitelist.clear()

    def test_login_success() -> None:
        token = login("zhang.san", "123456")
        assert isinstance(token, str) and len(token) > 0

    run_test("正确密码登录成功", test_login_success)

    def test_login_wrong_password() -> None:
        try:
            login("zhang.san", "wrong")
            raise AssertionError("错误密码应该登录失败")
        except Exception as exc:
            assert str(exc) == "用户名或密码错误"

    run_test("错误密码登录失败", test_login_wrong_password)

    whitelist.clear()
    users["zhang.san"]["is_active"] = True

    def test_access_after_login() -> None:
        token = login("zhang.san", "123456")
        user = get_current_user(token)
        assert user["username"] == "zhang.san"
        assert user["id"] == 1

    run_test("登录后 get_current_user 成功", test_access_after_login)

    def test_access_after_logout() -> None:
        token = login("zhang.san", "123456")
        logout(token)
        try:
            get_current_user(token)
            raise AssertionError("登出后应该访问失败")
        except Exception as exc:
            assert "令牌已失效" in str(exc)

    run_test("登出后 get_current_user 失败", test_access_after_logout)

    def test_disabled_user() -> None:
        whitelist.clear()
        users["zhang.san"]["is_active"] = True
        token = login("zhang.san", "123456")
        users["zhang.san"]["is_active"] = False
        try:
            get_current_user(token)
            raise AssertionError("禁用账号后应该访问失败")
        except Exception as exc:
            assert "已被禁用" in str(exc)

    run_test("禁用账号后访问失败", test_disabled_user)

    print("---")
    print("全部测试通过")


if __name__ == "__main__":
    main()
