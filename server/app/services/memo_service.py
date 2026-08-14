"""
备忘录服务
"""

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessException
from app.models.memo import Memo
from app.models.user import User
from app.schemas.memo import MemoCreateRequest, MemoUpdateRequest


async def list_memos(
    db: AsyncSession,
    user: User,
    keyword: str | None = None,
    category_id: int | None = None,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[Memo], int]:
    """分页查询备忘录，支持关键词与分类筛选"""
    query = select(Memo).where(Memo.user_id == user.id)
    count_query = select(func.count(Memo.id)).where(Memo.user_id == user.id)

    if keyword:
        kw_filter = or_(Memo.title.contains(keyword), Memo.content.contains(keyword))
        query = query.where(kw_filter)
        count_query = count_query.where(kw_filter)

    if category_id is not None:
        query = query.where(Memo.category_id == category_id)
        count_query = count_query.where(Memo.category_id == category_id)

    total = (await db.execute(count_query)).scalar() or 0
    query = query.order_by(Memo.is_pinned.desc(), Memo.updated_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_memo(db: AsyncSession, user: User, memo_id: int) -> Memo:
    """获取单条备忘录"""
    result = await db.execute(select(Memo).where(Memo.id == memo_id, Memo.user_id == user.id))
    memo = result.scalar_one_or_none()
    if not memo:
        raise BusinessException("备忘录不存在", code=404)
    return memo


async def create_memo(db: AsyncSession, user: User, req: MemoCreateRequest) -> Memo:
    """创建备忘录"""
    memo = Memo(
        user_id=user.id,
        title=req.title,
        content=req.content,
        category_id=req.category_id,
        is_pinned=req.is_pinned,
    )
    db.add(memo)
    await db.flush()
    return memo


async def update_memo(db: AsyncSession, user: User, memo_id: int, req: MemoUpdateRequest) -> Memo:
    """更新备忘录"""
    memo = await get_memo(db, user, memo_id)
    if req.title is not None:
        memo.title = req.title
    if req.content is not None:
        memo.content = req.content
    if req.category_id is not None:
        memo.category_id = req.category_id
    if req.is_pinned is not None:
        memo.is_pinned = req.is_pinned
    return memo


async def delete_memo(db: AsyncSession, user: User, memo_id: int) -> None:
    """删除备忘录"""
    memo = await get_memo(db, user, memo_id)
    await db.delete(memo)
