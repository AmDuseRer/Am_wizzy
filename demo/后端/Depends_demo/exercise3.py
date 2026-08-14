"""
练习 3：依赖套依赖（链式 Depends）

要练会什么：
  一个依赖函数的参数里也可以写 Depends，形成链条：
  admin_only -> require_admin -> get_user -> get_token

运行方式：
  pip install -r requirements.txt
  python exercise3.py

  （可选）启动服务：
  uvicorn exercise3:app --reload
  在 /docs 里给请求头 X-Token 填不同值测试

预期输出：
  [PASS] admin-token -> 200
  [PASS] user-token -> 403
  [PASS] wrong-token -> 401
  [PASS] no token -> 422
  ---
  admin: status=200 body={'ok': True, 'user': {...}}
  user:  status=403 body={'detail': '权限不足'}
  wrong: status=401 body={'detail': '无效 token'}
  none:  status=422
"""

from __future__ import annotations

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient

app = FastAPI(title="Exercise 3 - Depends Chain")


def get_token(x_token: str = Header(..., alias="X-Token")) -> str:
    """第 1 层：从请求头读取 token"""
    return x_token


def get_user(token: str = Depends(get_token)) -> dict:
    """第 2 层：根据 token 查用户"""
    if token == "user-token":
        return {"name": "张三", "role": "user"}
    if token == "admin-token":
        return {"name": "管理员", "role": "admin"}
    raise HTTPException(status_code=401, detail="无效 token")


def require_admin(user: dict = Depends(get_user)) -> dict:
    """第 3 层：必须是 admin"""
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    return user


@app.get("/admin-only")
def admin_only(user: dict = Depends(require_admin)):
    """接口只声明 require_admin，背后自动完成 token + 角色校验"""
    return {"ok": True, "user": user}


def run_tests() -> None:
    client = TestClient(app)

    cases = [
        ("admin-token", 200, {"ok": True, "user": {"name": "管理员", "role": "admin"}}),
        ("user-token", 403, {"detail": "权限不足"}),
        ("wrong-token", 401, {"detail": "无效 token"}),
    ]

    for token, expected_status, expected_body in cases:
        response = client.get("/admin-only", headers={"X-Token": token})
        assert response.status_code == expected_status, (
            f"token={token!r} expected {expected_status}, got {response.status_code}, body={response.text}"
        )
        assert response.json() == expected_body, response.json()
        print(f"[PASS] {token} -> {expected_status}")

    response_no_token = client.get("/admin-only")
    assert response_no_token.status_code == 422, response_no_token.text
    print("[PASS] no token -> 422")

    print("---")
    for token in ["admin-token", "user-token", "wrong-token"]:
        resp = client.get("/admin-only", headers={"X-Token": token})
        label = "admin" if token == "admin-token" else ("user" if token == "user-token" else "wrong")
        print(f"{label}: status={resp.status_code} body={resp.json()}")
    print(f"none:  status={response_no_token.status_code}")


if __name__ == "__main__":
    run_tests()
