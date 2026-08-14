"""
练习 1：AES/Fernet 加解密往返

要练会什么：
  明文可以变成乱码存起来；用同一把钥匙能变回原文；
  换钥匙、乱改密文、密钥缺失时应该解不开。

运行方式（Windows PowerShell）：
  cd demo/AES_Fernet_demo
  pip install -r requirements.txt
  python exercise1.py

预期输出（大致）：
  密文开头: gAAAAA...
  解密结果: 'GitHubPass123'
  [PASS] 用错误密钥解密 — 正确失败
  [PASS] 篡改密文后解密 — 正确失败
  [PASS] 空密钥 — 正确失败
  ---
  全部测试通过
"""

from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken

KEY_A = "lOV5cj7GBhFokEpgMfBqc3f0xcMnLceZ2h4VgsszMjg="
KEY_B = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
PLAIN = "GitHubPass123"


def make_fernet(key: str) -> Fernet:
    return Fernet(key.encode())


def encrypt_text(key: str, plain: str) -> str:
    f = make_fernet(key)
    return f.encrypt(plain.encode("utf-8")).decode("utf-8")


def decrypt_text(key: str, cipher: str) -> str:
    f = make_fernet(key)
    return f.decrypt(cipher.encode("utf-8")).decode("utf-8")


def expect_fail(label: str, fn) -> bool:
    try:
        fn()
        print(f"[FAIL] {label} — 应该失败却成功了")
        return False
    except (InvalidToken, ValueError, Exception):
        print(f"[PASS] {label} — 正确失败")
        return True


def main() -> None:
    ok = True

    cipher = encrypt_text(KEY_A, PLAIN)
    print(f"密文开头: {cipher[:12]}...")
    ok &= cipher.startswith("gAAAAA")

    back = decrypt_text(KEY_A, cipher)
    print(f"解密结果: {back!r}")
    ok &= back == PLAIN

    ok &= expect_fail(
        "用错误密钥解密",
        lambda: decrypt_text(KEY_B, cipher),
    )

    bad_cipher = cipher[:-1] + ("A" if cipher[-1] != "A" else "B")
    ok &= expect_fail(
        "篡改密文后解密",
        lambda: decrypt_text(KEY_A, bad_cipher),
    )

    ok &= expect_fail(
        "空密钥",
        lambda: encrypt_text("", PLAIN),
    )

    print("---")
    if ok:
        print("全部测试通过")
    else:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
