"""
练习 1：感受「异步等数据库」

要练会什么：
  - create_async_engine 是什么
  - 为什么数据库操作必须写 await
  - asyncio.run() 如何跑一段异步代码

运行方式：
  cd demo/异步ORM_demo
  pip install -r requirements.txt
  python exercise1.py

预期输出（大致）：
  [PASS] query returns 1
  [PASS] missing await detected
  ---
  查询结果: 1
  (若 echo=True，还会看到 SQL 日志)
"""

from __future__ import annotations

import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


async def query_one(conn) -> int:
    result = await conn.execute(text("SELECT 1 AS n"))
    row = result.one()
    return row.n


async def demo_missing_await(conn) -> object:
    """故意不写 await，用于对比演示"""
    return conn.execute(text("SELECT 1 AS n"))


async def main_async() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)

    async with engine.connect() as conn:
        value = await query_one(conn)
        print(f"查询结果: {value}")

        inner = await demo_missing_await(conn)
        if asyncio.iscoroutine(inner):
            print("漏写 await 时得到 coroutine 对象，而不是查询结果")
            inner.close()

    await engine.dispose()


def run_tests() -> None:
    asyncio.run(main_async())

    # 独立验证：有 await 返回 int，无 await 返回 coroutine
    async def _check() -> None:
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        async with engine.connect() as conn:
            with_await = await query_one(conn)
            assert with_await == 1
            without_await = demo_missing_await(conn)
            assert asyncio.iscoroutine(without_await)
            without_await.close()
        await engine.dispose()

    asyncio.run(_check())
    print("[PASS] query returns 1")
    print("[PASS] missing await detected")
    print("---")


if __name__ == "__main__":
    run_tests()
