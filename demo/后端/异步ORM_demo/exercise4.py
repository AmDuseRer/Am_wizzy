"""
练习 4：模拟 get_db —— 提交与回滚

要练会什么：
  - yield session -> 成功 commit -> 失败 rollback
  - 一次业务请求里多条操作要么全成功，要么全撤销

运行方式：
  python exercise4.py

预期输出（大致）：
  [PASS] scenario A committed
  [PASS] scenario B rolled back
  ---
  场景 A: 找到 title=A
  场景 B: 未找到 title=B (回滚生效)
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

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


def make_get_db(session_factory):
    @asynccontextmanager
    async def get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    return get_db


async def find_by_title(session_factory, title: str) -> Note | None:
    async with session_factory() as session:
        result = await session.execute(select(Note).where(Note.title == title))
        return result.scalar_one_or_none()


async def setup() -> tuple:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return engine, session_factory


def run_tests() -> None:
    async def main() -> None:
        engine, session_factory = await setup()
        get_db = make_get_db(session_factory)

        # 场景 A：正常结束 -> commit
        async with get_db() as session:
            session.add(Note(title="A", content="ok"))

        note_a = await find_by_title(session_factory, "A")
        assert note_a is not None and note_a.title == "A"
        print("[PASS] scenario A committed")

        # 场景 B：中途抛错 -> rollback
        try:
            async with get_db() as session:
                session.add(Note(title="B", content="will rollback"))
                raise ValueError("模拟业务失败")
        except ValueError as exc:
            assert str(exc) == "模拟业务失败"

        note_b = await find_by_title(session_factory, "B")
        assert note_b is None
        print("[PASS] scenario B rolled back")

        print("---")
        print(f"场景 A: 找到 title={note_a.title}")
        print("场景 B: 未找到 title=B (回滚生效)")

        await engine.dispose()

    asyncio.run(main())


if __name__ == "__main__":
    run_tests()
    