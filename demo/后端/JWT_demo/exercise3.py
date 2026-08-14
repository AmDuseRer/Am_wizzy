"""
练习 3：白名单是什么（用字典模拟 user_tokens 表）

要练会什么：
  光有 JWT 不够，还要查「这张证是否还有效」。用内存字典模拟数据库白名单。

运行方式（Windows PowerShell）：
  cd demo/JWT_demo
  pip install -r requirements.txt
  python exercise3.py

预期输出（大致）：
  [PASS] 刚加入白名单 -> True
  [PASS] revoke 后 -> False
  [PASS] user_id 不匹配 -> False
  [PASS] jti 不存在 -> False
  ---
  全部测试通过

练完对照项目文件：
  server/app/models/user.py  -> UserToken 表（jti, user_id, is_revoked）
"""

from __future__ import annotations

# 模拟 user_tokens 表：jti -> {"user_id": 1, "is_revoked": False}
whitelist: dict[str, dict] = {}


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


def run_test(name: str, condition: bool) -> None:
    if condition:
        print(f"[PASS] {name}")
    else:
        print(f"[FAIL] {name}")
        raise SystemExit(1)


def main() -> None:
    whitelist.clear()

    add_to_whitelist("abc123", 1)
    add_to_whitelist("def456", 1)

    run_test("刚加入白名单 -> True", is_token_allowed("abc123", 1) is True)

    revoke_token("abc123")
    run_test("revoke 后 -> False", is_token_allowed("abc123", 1) is False)

    run_test("user_id 不匹配 -> False", is_token_allowed("def456", 2) is False)

    run_test("jti 不存在 -> False", is_token_allowed("not-exist", 1) is False)

    print("---")
    print("全部测试通过")


if __name__ == "__main__":
    main()
