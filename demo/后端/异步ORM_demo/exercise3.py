"""
练习 3：查询 + 筛选 + 分页（贴近 list_memos）

要练会什么：
  - select(Model).where(...).order_by(...).offset().limit()
  - func.count() 算总数
  - or_() 做关键词搜索

运行方式：
  python exercise3.py

预期输出（大致）：
  [PASS] page 1 titles
  [PASS] page 2 titles
  [PASS] keyword filter
  [PASS] empty keyword
  ---
  page1: ['临时备忘', '学习笔记'] total=4
  page2: ['购物清单', '周末计划'] total=4
  keyword: ['购物清单'] total=1
  empty: [] total=0
"""

from __future__ import annotations

import asyncio

from sqlalchemy import Integer, String, Text, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, default="", nullable=False)


SEED_DATA = [
    ("周末计划", "去爬山"),
    ("购物清单", "买水果"),
    ("学习笔记", "复习 SQLAlchemy"),
    ("临时备忘", "打电话"),
]


async def list_notes(
    session: AsyncSession,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 2,
) -> tuple[list[Note], int]:
    query = select(Note)
    count_query = select(func.count(Note.id))

    if keyword:
        kw_filter = or_(Note.title.contains(keyword), Note.content.contains(keyword))
        query = query.where(kw_filter)
        count_query = count_query.where(kw_filter)

    total = (await session.execute(count_query)).scalar() or 0
    query = query.order_by(Note.id.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(query)
    return list(result.scalars().all()), total


async def setup_with_seed() -> tuple:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        for title, content in SEED_DATA:
            session.add(Note(title=title, content=content))
        await session.commit()

    return engine, session_factory


def run_tests() -> None:
    async def main() -> None:
        engine, session_factory = await setup_with_seed()

        async with session_factory() as session:
            page1_items, page1_total = await list_notes(session)
            page2_items, page2_total = await list_notes(session, page=2, page_size=2)
            kw_items, kw_total = await list_notes(session, keyword="购物")
            empty_items, empty_total = await list_notes(session, keyword="xyz")

        page1_titles = [n.title for n in page1_items]
        page2_titles = [n.title for n in page2_items]
        kw_titles = [n.title for n in kw_items]

        assert page1_titles == ["临时备忘", "学习笔记"], page1_titles
        assert page1_total == 4
        print("[PASS] page 1 titles")

        assert page2_titles == ["购物清单", "周末计划"], page2_titles
        assert page2_total == 4
        print("[PASS] page 2 titles")

        assert kw_titles == ["购物清单"] and kw_total == 1
        print("[PASS] keyword filter")

        assert empty_items == [] and empty_total == 0
        print("[PASS] empty keyword")

        print("---")
        print(f"page1: {page1_titles} total={page1_total}")
        print(f"page2: {page2_titles} total={page2_total}")
        print(f"keyword: {kw_titles} total={kw_total}")
        print(f"empty: {empty_items} total={empty_total}")

        await engine.dispose()

    asyncio.run(main())


if __name__ == "__main__":
    run_tests()
