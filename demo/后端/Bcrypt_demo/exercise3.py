"""
练习 3：模拟「数据库只存哈希」

要练会什么：
  注册时存哈希、登录时验哈希——理解「库里没有明文密码」。

运行方式（Windows PowerShell）：
  cd demo/Bcrypt_demo
  pip install -r requirements.txt
  python exercise3.py

预期输出（大致）：
  注册成功: 张三
    库里存的是: $2b$12$...
  [PASS] 正确密码登录 -> (True, '登录成功')
  [PASS] 错误密码登录 -> (False, '密码错误')
  [PASS] 不存在用户登录 -> (False, '用户不存在')
  [PASS] 数据库中没有明文密码
  ---
  数据库内容: {'张三': '$2b$12$...'}
  全部测试通过
"""

from __future__ import annotations

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 假装这是数据库里的 users 表
users_db: dict[str, str] = {}


def register(username: str, password: str) -> None:
    users_db[username] = pwd_context.hash(password)
    print(f"注册成功: {username}")
    print(f"  库里存的是: {users_db[username][:30]}...")


def login(username: str, password: str) -> tuple[bool, str]:
    if username not in users_db:
        return False, "用户不存在"
    if pwd_context.verify(password, users_db[username]):
        return True, "登录成功"
    return False, "密码错误"


def check(label: str, actual: tuple[bool, str], expected: tuple[bool, str]) -> None:
    if actual == expected:
        print(f"[PASS] {label} -> {actual}")
    else:
        print(f"[FAIL] {label} -> 得到 {actual}，期望 {expected}")
        raise SystemExit(1)


# --- 测试 ---
register("张三", "hello888")

check("正确密码登录", login("张三", "hello888"), (True, "登录成功"))
check("错误密码登录", login("张三", "wrong"), (False, "密码错误"))
check("不存在用户登录", login("李四", "hello888"), (False, "用户不存在"))

# 确认数据库里没有明文密码
plain_in_db = "hello888" in users_db.values()
if not plain_in_db:
    print("[PASS] 数据库中没有明文密码")
else:
    print("[FAIL] 数据库中发现了明文密码")
    raise SystemExit(1)

print("---")
print("数据库内容:", {k: v[:30] + "..." for k, v in users_db.items()})
print("全部测试通过")
