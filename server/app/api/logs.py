"""
操作日志 API 路由
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.exceptions import success
from app.models.user import User
from app.schemas.operation_log import OperationLogResponse
from app.services import operation_log_service

router = APIRouter()


@router.get("")
async def list_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    module: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """分页查询操作日志"""
    logs, total = await operation_log_service.get_logs(db, current_user, page, page_size, module)
    return success({
        "items": [OperationLogResponse.model_validate(l).model_dump() for l in logs],
        "total": total,
        "page": page,
        "page_size": page_size,
    })
