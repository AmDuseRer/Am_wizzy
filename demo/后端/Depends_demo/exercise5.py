"""
练习 5：迷你综合题（最接近本项目）

要练会什么：
  组合 get_db(yield) + get_current_user(Header + Depends) + 业务接口。
  对应 server/app/core/database.py、deps.py、api/memos.py 的简化版。

运行方式：
  pip install -r requirements.txt
  python exercise5.py

  （可选）启动服务：
  uvicorn exercise5:app --reload
  在 /docs 里给 Authorization 填 Bearer token-alice 或 Bearer token-bob

预期输出：
  [PASS] Bearer token-alice -> 200, 1 memo
  [PASS] Bearer token-bob -> 200, 1 memo
  [PASS] Bearer wrong -> 401
  [PASS] no Authorization -> 401
  ---
  alice: status=200 body={'items': [{'id': 1, ...}]}
  bob:   status=200 body={'items': [{'id': 2, ...}]}
  wrong: status=401 body={'detail': '无效 token'}
  none:  status=401 body={'detail': '未登录'}
"""

from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient

app = FastAPI(title="Exercise 5 - Mini Project")

USERS = {
    "token-alice": {"id": 1, "name": "Alice"},
    "token-bob": {"id": 2, "name": "Bob"},
}

MEMOS = [
    {"id": 1, "user_id": 1, "title": "Alice 的备忘"},
    {"id": 2, "user_id": 2, "title": "Bob 的备忘"},
]


def get_db() -> Generator[dict, None, None]:
    """模拟 database.py 里的 get_db"""
    db = {"memos": MEMOS}
    try:
        yield db
        # 真实项目里这里会 await session.commit()
    finally:
        # 真实项目里这里会关闭 session
        pass


def get_current_user(
    authorization: str | None = Header(None),
    db: dict = Depends(get_db),
) -> dict:
    """模拟 deps.py 里的 get_current_user"""
    _ = db  # 真实项目里会用 db 查 token 表和用户表
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")

    token = authorization.removeprefix("Bearer ")
    user = USERS.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="无效 token")
    return user


@app.get("/memos")
def list_memos(
    db: dict = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """模拟 memos.py：业务函数只关心 db 和 current_user"""
    items = [memo for memo in db["memos"] if memo["user_id"] == user["id"]]
    return {"items": items}


def run_tests() -> None:
    client = TestClient(app)

    cases = [
        (
            {"Authorization": "Bearer token-alice"},
            200,
            {"items": [{"id": 1, "user_id": 1, "title": "Alice 的备忘"}]},
        ),
        (
            {"Authorization": "Bearer token-bob"},
            200,
            {"items": [{"id": 2, "user_id": 2, "title": "Bob 的备忘"}]},
        ),
        (
            {"Authorization": "Bearer wrong"},
            401,
            {"detail": "无效 token"},
        ),
        (
            {},
            401,
            {"detail": "未登录"},
        ),
    ]

    labels = ["alice", "bob", "wrong", "none"]
    results = []

    for label, (headers, expected_status, expected_body) in zip(labels, cases):
        response = client.get("/memos", headers=headers)
        assert response.status_code == expected_status, (
            f"{label}: expected {expected_status}, got {response.status_code}, body={response.text}"
        )
        assert response.json() == expected_body, response.json()
        results.append((label, response))

        if label == "alice":
            print("[PASS] Bearer token-alice -> 200, 1 memo")
        elif label == "bob":
            print("[PASS] Bearer token-bob -> 200, 1 memo")
        elif label == "wrong":
            print("[PASS] Bearer wrong -> 401")
        else:
            print("[PASS] no Authorization -> 401")

    print("---")
    for label, response in results:
        print(f"{label}: status={response.status_code} body={response.json()}")


if __name__ == "__main__":
    run_tests()
