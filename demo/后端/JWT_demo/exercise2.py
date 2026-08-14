"""
练习 2：签发 + 验签（像服务器发真通行证）

要练会什么：
  服务器用密钥签发 JWT；别人改内容或伪造，验签会失败；过期 token 必须拒绝。

运行方式（Windows PowerShell）：
  cd demo/JWT_demo
  pip install -r requirements.txt
  python exercise2.py

预期输出（大致）：
  [PASS] 正常 token 验签成功，sub=1, username=zhang.san
  [PASS] 篡改 token 后验签失败
  [PASS] 过期 token 验签失败
  [PASS] 错误密钥验签失败
  ---
  全部测试通过

练完对照项目文件：
  server/app/core/security.py  -> create_access_token / decode_access_token
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import jwt

SECRET = "my-secret-key-for-jwt-practice-only-32b"
ALGORITHM = "HS256"


def create_token(user_id: int, username: str, role: str) -> tuple[str, str]:
    """签发 JWT，返回 (token 字符串, jti)"""
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


def verify_token(token: str, secret: str = SECRET) -> dict:
    """验签并解析 payload，失败时抛出 jwt.PyJWTError"""
    return jwt.decode(token, secret, algorithms=[ALGORITHM])


def create_expired_token(user_id: int, username: str) -> str:
    """故意签发一个已过期的 token，用于测试"""
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) - timedelta(seconds=1)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": "user",
        "jti": jti,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def run_test(name: str, fn) -> None:
    try:
        fn()
        print(f"[PASS] {name}")
    except AssertionError as exc:
        print(f"[FAIL] {name}: {exc}")
        raise SystemExit(1)
    except jwt.PyJWTError:
        # 某些测试期望抛出 PyJWTError，由 fn 内部 assert 处理
        raise


def main() -> None:
    # 1. 正常签发 + 验签
    def test_valid_token() -> None:
        token, jti = create_token(1, "zhang.san", "user")
        payload = verify_token(token)
        assert payload["sub"] == "1", payload
        assert payload["username"] == "zhang.san", payload
        assert payload["jti"] == jti, payload
        print(f"  正常 token 验签成功，sub={payload['sub']}, username={payload['username']}")

    run_test("正常 token 验签成功，sub=1, username=zhang.san", test_valid_token)

    # 2. 篡改 token
    def test_tampered_token() -> None:
        token, _ = create_token(1, "zhang.san", "user")
        tampered = token[:-1] + ("a" if token[-1] != "a" else "b")
        try:
            verify_token(tampered)
            raise AssertionError("篡改 token 应该验签失败")
        except jwt.PyJWTError:
            pass

    run_test("篡改 token 后验签失败", test_tampered_token)

    # 3. 过期 token
    def test_expired_token() -> None:
        expired = create_expired_token(1, "zhang.san")
        try:
            verify_token(expired)
            raise AssertionError("过期 token 应该验签失败")
        except jwt.ExpiredSignatureError:
            pass

    run_test("过期 token 验签失败", test_expired_token)

    # 4. 错误密钥
    def test_wrong_secret() -> None:
        token, _ = create_token(1, "zhang.san", "user")
        try:
            verify_token(token, secret="wrong-secret")
            raise AssertionError("错误密钥应该验签失败")
        except jwt.PyJWTError:
            pass

    run_test("错误密钥验签失败", test_wrong_secret)

    print("---")
    print("全部测试通过")


if __name__ == "__main__":
    main()
