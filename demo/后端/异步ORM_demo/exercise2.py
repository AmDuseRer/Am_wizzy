"""
练习 2：用 ORM 类代表一张表

要练会什么：
  - DeclarativeBase、Mapped、mapped_column
  - create_all 建表
  - 用 Python 对象插入并查询数据

运行方式：
  python exercise2.py

预期输出（大致）：
  [PASS] insert and select
  [PASS] commit required
  ---
  1 买菜 鸡蛋、牛奶
"""

from __future__ import annotations

import asyncio

from sqlalchemy import Integer, String, Text, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, default="", nullable=False)


async def setup_session() -> tuple:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return engine, session_factory


async def insert_and_select(session_factory) -> Note:
    async with session_factory() as session:
        note = Note(title="买菜", content="鸡蛋、牛奶")
        session.add(note)
        await session.commit()

        result = await session.execute(select(Note).where(Note.title == "买菜"))
        return result.scalar_one()


async def insert_without_commit(session_factory) -> bool:
    """不 commit 时，新 session 查不到刚插入的数据"""
    async with session_factory() as session:
        session.add(Note(title="未提交", content="test"))
        # 故意不 await session.commit()

    async with session_factory() as session:
        result = await session.execute(select(Note).where(Note.title == "未提交"))
        found = result.scalar_one_or_none()
        return found is None


def run_tests() -> None:
    async def main() -> None:
        engine, session_factory = await setup_session()

        note = await insert_and_select(session_factory)
        print(f"{note.id} {note.title} {note.content}")
        assert note.id == 1
        assert note.title == "买菜"
        assert note.content == "鸡蛋、牛奶"
        print("[PASS] insert and select")

        no_commit_ok = await insert_without_commit(session_factory)
        assert no_commit_ok is True
        print("[PASS] commit required")

        await engine.dispose()
        print("---")

    asyncio.run(main())


if __name__ == "__main__":
    run_tests()
