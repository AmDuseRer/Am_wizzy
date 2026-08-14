"""
练习 1：模拟「前端校验」（对应 LoginView.vue 的 rules）

要练会什么：
  用户点提交之前，网页先检查一遍；不合格就不发请求。

运行方式：
  cd demo\\表单校验_demo
  pip install -r requirements.txt
  python exercise1.py

对照项目文件：
  web/src/views/LoginView.vue  （rules + formRef.validate()）
"""

from __future__ import annotations


def validate_login(form: dict) -> list[str]:
    """模拟 Element Plus 表单 rules：与 LoginView.vue 一致"""
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


def run_tests() -> None:
    cases = [
        ({"username": "admin", "password": "Admin@123"}, True, "测1-正常登录"),
        ({"username": "", "password": "Admin@123"}, False, "测2-用户名为空"),
        ({"username": "a", "password": "Admin@123"}, False, "测3-用户名太短"),
        ({"username": "admin", "password": "123"}, False, "测4-密码太短"),
    ]

    passed = 0
    for form, expect_ok, name in cases:
        errors = validate_login(form)
        ok = len(errors) == 0
        assert ok == expect_ok, f"{name}: expected ok={expect_ok}, got errors={errors}"
        if ok:
            print(f"[PASS] {name}: OK -> 前端放行，可以发请求")
        else:
            print(f"[PASS] {name}: BLOCK -> {'; '.join(errors)}")
        passed += 1

    print("---")
    print(f"{passed}/{len(cases)} tests passed")


if __name__ == "__main__":
    run_tests()
