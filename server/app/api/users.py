"""
用户管理 API 路由（admin）
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_client_ip, require_admin
from app.core.exceptions import success
from app.models.user import User
from app.schemas.user import UserCreateRequest, UserResetPasswordRequest, UserResponse, UserUpdateRequest
from app.services import user_service

router = APIRouter()


@router.get("")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """分页获取用户列表"""
    users, total = await user_service.list_users(db, page, page_size)
    return success({
        "items": [UserResponse.model_validate(u).model_dump() for u in users],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.post("")
async def create_user(
    req: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
    ip: str = Depends(get_client_ip),
):
    """创建用户"""
    user = await user_service.create_user(db, admin, req, ip)
    return success(UserResponse.model_validate(user).model_dump(), "创建成功")


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    req: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
    ip: str = Depends(get_client_ip),
):
    """更新用户"""
    user = await user_service.update_user(db, admin, user_id, req, ip)
    return success(UserResponse.model_validate(user).model_dump(), "更新成功")


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
    ip: str = Depends(get_client_ip),
):
    """删除用户"""
    await user_service.delete_user(db, admin, user_id, ip)
    return success(message="删除成功")


@router.post("/{user_id}/reset-password")
async def reset_password(
    user_id: int,
    req: UserResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
    ip: str = Depends(get_client_ip),
):
    """重置用户密码"""
    await user_service.reset_password(db, admin, user_id, req, ip)
    return success(message="密码重置成功")
