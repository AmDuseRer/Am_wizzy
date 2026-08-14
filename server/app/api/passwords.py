"""
密码本 API 路由
"""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io

from app.core.database import get_db
from app.core.deps import get_client_ip, get_current_user
from app.core.exceptions import success
from app.models.user import User
from app.schemas.password import (
    PasswordCreateRequest,
    PasswordRevealRequest,
    PasswordRevealResponse,
    PasswordUpdateRequest,
)
from app.services import password_service

router = APIRouter()


@router.get("")
async def list_passwords(
    keyword: str | None = None,
    category_id: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """分页查询密码条目（脱敏）"""
    items, total = await password_service.list_passwords(
        db, current_user, keyword, category_id, page, page_size
    )
    return success({
        "items": [i.model_dump() for i in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.post("")
async def create_password(
    req: PasswordCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建密码条目"""
    entry = await password_service.create_password(db, current_user, req)
    return success(entry.model_dump(), "创建成功")


@router.put("/{entry_id}")
async def update_password(
    entry_id: int,
    req: PasswordUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新密码条目"""
    entry = await password_service.update_password(db, current_user, entry_id, req)
    return success(entry.model_dump(), "更新成功")


@router.delete("/{entry_id}")
async def delete_password(
    entry_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ip: str = Depends(get_client_ip),
):
    """删除密码条目"""
    await password_service.delete_password(db, current_user, entry_id, ip)
    return success(message="删除成功")


@router.post("/{entry_id}/reveal")
async def reveal_password(
    entry_id: int,
    req: PasswordRevealRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ip: str = Depends(get_client_ip),
):
    """二次校验后查看明文密码"""
    plain = await password_service.reveal_password(db, current_user, entry_id, req, ip)
    return success(PasswordRevealResponse(id=entry_id, password=plain).model_dump())


@router.get("/export/backup")
async def export_backup(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ip: str = Depends(get_client_ip),
):
    """导出加密备份 JSON"""
    content = await password_service.export_backup(db, current_user, ip)
    return StreamingResponse(
        io.BytesIO(content.encode("utf-8")),
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="password_backup.json"'},
    )
