"""
练习 2：迷你密码本 — 存 / 列表脱敏 / 验证后查看

要练会什么：
  模拟 wizzy 密码本完整流程——保存时加密、列表只脱敏、
  查看前先 Bcrypt 验证查看密码，通过后才 AES 解密。

运行方式（Windows PowerShell）：
  cd demo/AES_Fernet_demo
  pip install -r requirements.txt
  python exercise2.py

预期输出（大致）：
  [PASS] 库里不是明文
  [PASS] 列表只显示脱敏
  [PASS] 验证通过后看到明文: 'GitHubPass123'
  [PASS] 错误查看密码被拦住
  [PASS] 换密钥后解密失败
  ---
  全部测试通过 — 你已经摸到了项目里密码本的完整流程
"""

from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken
from passlib.context import CryptContext

# ===== 配置（模拟 .env）=====
AES_KEY = "lOV5cj7GBhFokEpgMfBqc3f0xcMnLceZ2h4VgsszMjg="
VIEW_PASSWORD_PLAIN = "view666"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
view_password_hash = pwd_context.hash(VIEW_PASSWORD_PLAIN)

# ===== 模拟数据库 =====
fake_db: dict[str, str] = {}


def aes_encrypt(plain: str, key: str = AES_KEY) -> str:
    f = Fernet(key.encode())
    return f.encrypt(plain.encode("utf-8")).decode("utf-8")


def aes_decrypt(cipher: str, key: str = AES_KEY) -> str:
    f = Fernet(key.encode())
    return f.decrypt(cipher.encode("utf-8")).decode("utf-8")


def mask_password(password: str) -> str:
    """脱敏：GitHubPass123 -> G****3"""
    if len(password) <= 2:
        return "****"
    return password[0] + "****" + password[-1]


def save_entry(site_name: str, plain_password: str) -> None:
    fake_db[site_name] = aes_encrypt(plain_password)


def list_entries() -> list[dict]:
    """列表：只返回脱敏占位，不解密"""
    result = []
    for site in fake_db:
        result.append({"site": site, "password_masked": "****"})
    return result


def reveal_entry(site_name: str, view_password_input: str, key: str = AES_KEY) -> str:
    if site_name not in fake_db:
        raise ValueError("条目不存在")

    if not pwd_context.verify(view_password_input, view_password_hash):
        raise PermissionError("查看专用密码错误")

    return aes_decrypt(fake_db[site_name], key=key)


def main() -> None:
    ok = True

    save_entry("GitHub", "GitHubPass123")

    stored = fake_db["GitHub"]
    ok &= stored != "GitHubPass123"
    ok &= stored.startswith("gAAAAA")
    print(f"[{'PASS' if stored != 'GitHubPass123' else 'FAIL'}] 库里不是明文")

    listed = list_entries()
    ok &= listed[0]["password_masked"] == "****"
    print(f"[{'PASS' if listed[0]['password_masked'] == '****' else 'FAIL'}] 列表只显示脱敏")

    plain = reveal_entry("GitHub", "view666")
    ok &= plain == "GitHubPass123"
    print(f"[{'PASS' if plain == 'GitHubPass123' else 'FAIL'}] 验证通过后看到明文: {plain!r}")

    try:
        reveal_entry("GitHub", "wrong")
        print("[FAIL] 错误查看密码应该失败")
        ok = False
    except PermissionError:
        print("[PASS] 错误查看密码被拦住")

    wrong_key = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    try:
        reveal_entry("GitHub", "view666", key=wrong_key)
        print("[FAIL] 换密钥后应该解密失败")
        ok = False
    except InvalidToken:
        print("[PASS] 换密钥后解密失败")

    print("---")
    if ok:
        print("全部测试通过 — 你已经摸到了项目里密码本的完整流程")
    else:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
