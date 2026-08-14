"""
练习 2：练「能验证」——对的上、对不上

要练会什么：
  用 verify 判断密码是否正确，不需要把哈希变回明文。

运行方式（Windows PowerShell）：
  cd demo/Bcrypt_demo
  pip install -r requirements.txt
  python exercise2.py

预期输出（大致）：
  已生成哈希: $2b$12$...
  正确密码   'abc123'   -> [PASS] 通过
  错一位     'abc124'   -> [PASS] 失败
  大小写不同 'ABC123'   -> [PASS] 失败
  空密码     ''         -> [PASS] 失败
  ---
  全部测试通过
"""

from __future__ import annotations

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 模拟注册：把 abc123 变成哈希存起来
stored_hash = pwd_context.hash("abc123")
print(f"已生成哈希: {stored_hash[:30]}...")

# 测试用例：(输入密码, 描述, 期望是否通过)
tests: list[tuple[str, str, bool]] = [
    ("abc123", "正确密码", True),
    ("abc124", "错一位", False),
    ("ABC123", "大小写不同", False),
    ("", "空密码", False),
]

all_passed = True

for password, label, expected_ok in tests:
    ok = pwd_context.verify(password, stored_hash)
    status = "通过" if ok else "失败"
    expected_status = "通过" if expected_ok else "失败"
    passed = ok == expected_ok
    mark = "[PASS]" if passed else "[FAIL]"
    if not passed:
        all_passed = False
    print(f"{label:10} {password!r:10} -> {mark} {status} (期望: {expected_status})")

print("---")
if all_passed:
    print("全部测试通过")
else:
    raise SystemExit(1)
