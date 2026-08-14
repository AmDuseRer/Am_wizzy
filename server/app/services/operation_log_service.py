"""
操作日志服务
记录与查询高危操作
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.operation_log import OperationLog
from app.models.user import User


async def log_operation(
    db: AsyncSession,
    user: User,
    action: str,
    module: str,
    detail: str,
    ip: str = "127.0.0.1",
) -> None:
    """写入一条操作日志"""
    log = OperationLog(
        user_id=user.id,
        action=action,
        module=module,
        detail=detail,
        ip=ip,
    )
    db.add(log)
    await db.flush()


async def get_logs(
    db: AsyncSession,
    user: User,
    page: int = 1,
    page_size: int = 20,
    module: str | None = None,
) -> tuple[list[OperationLog], int]:
    """分页查询操作日志，admin 可查全部，普通用户仅查自身"""
    query = select(OperationLog)
    count_query = select(func.count(OperationLog.id))

    if user.role != "admin":
        query = query.where(OperationLog.user_id == user.id)
        count_query = count_query.where(OperationLog.user_id == user.id)

    if module:
        query = query.where(OperationLog.module == module)
        count_query = count_query.where(OperationLog.module == module)

    total = (await db.execute(count_query)).scalar() or 0
    query = query.order_by(OperationLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total
