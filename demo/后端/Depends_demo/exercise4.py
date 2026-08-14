"""
练习 4：yield 依赖 -- 借东西 + 自动归还

要练会什么：
  yield 前是「借出」，yield 后是「收尾」。
  对应本项目 get_db 的借连接 / 还连接模式。

运行方式：
  pip install -r requirements.txt
  python exercise4.py

  （可选）启动服务：
  uvicorn exercise4:app --reload
  连续访问几次 http://127.0.0.1:8000/use-db 观察控制台日志

预期输出（大致）：
  [PASS] first request returns conn-1, pool_size=1
  [PASS] second request returns conn-2, pool_size=1
  [PASS] pool restored after two requests
  ---
  (控制台会打印借出/归还日志)
  first:  status=200 body={'used': 'conn-1', 'pool_size': 1}
  second: status=200 body={'used': 'conn-2', 'pool_size': 1}
  pool after tests: ['conn-1', 'conn-2']
"""

from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

app = FastAPI(title="Exercise 4 - Yield Depends")

# 模拟连接池，只有 2 条连接
POOL: list[str] = ["conn-1", "conn-2"]


def get_conn() -> Generator[str, None, None]:
    """yield 依赖：借出连接，用完后在 finally 里归还"""
    conn = POOL.pop(0)
    print(f"[get_conn] borrow {conn}, pool left={len(POOL)}")
    try:
        yield conn
        print(f"[get_conn] normal finish, return {conn}")
    finally:
        POOL.append(conn)
        print(f"[get_conn] returned {conn}, pool size={len(POOL)}")


@app.get("/use-db")
def use_db(conn: str = Depends(get_conn)):
    return {"used": conn, "pool_size": len(POOL)}


def run_tests() -> None:
    global POOL
    POOL = ["conn-1", "conn-2"]

    client = TestClient(app)

    print("--- request 1 ---")
    first = client.get("/use-db")
    print("--- request 2 ---")
    second = client.get("/use-db")

    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text

    first_body = first.json()
    second_body = second.json()

    assert first_body["used"] == "conn-1", first_body
    assert second_body["used"] == "conn-2", second_body
    assert first_body["pool_size"] == 1, first_body
    assert second_body["pool_size"] == 1, second_body
    assert POOL == ["conn-1", "conn-2"], POOL

    print("[PASS] first request returns conn-1, pool_size=1")
    print("[PASS] second request returns conn-2, pool_size=1")
    print("[PASS] pool restored after two requests")
    print("---")
    print(f"first:  status={first.status_code} body={first_body}")
    print(f"second: status={second.status_code} body={second_body}")
    print(f"pool after tests: {POOL}")


def demo_leak() -> None:
    """
    加分实验：注释掉 finally 里的归还逻辑后，第三次请求会失败。
    本函数仅演示原理，默认不自动运行。
    """
    print("demo_leak() is optional. See README for manual experiment steps.")


if __name__ == "__main__":
    run_tests()
