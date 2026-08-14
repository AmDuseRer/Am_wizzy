"""
用户管理服务（admin）
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessException
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreateRequest, UserResetPasswordRequest, UserUpdateRequest
from app.services.auth_service import revoke_all_tokens
from app.services.operation_log_service import log_operation


async def list_users(db: AsyncSession, page: int = 1, page_size: int = 20) -> tuple[list[User], int]:
    """分页获取用户列表"""
    total = (await db.execute(select(func.count(User.id)))).scalar() or 0
    result = await db.execute(
        select(User).order_by(User.id).offset((page - 1) * page_size).limit(page_size)
    )
    return list(result.scalars().all()), total


async def create_user(db: AsyncSession, admin: User, req: UserCreateRequest, ip: str) -> User:
    """创建新用户"""
    existing = await db.execute(select(User).where(User.username == req.username))
    if existing.scalar_one_or_none():
        raise BusinessException("用户名已存在", code=400)

    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        role=req.role,
    )
    db.add(user)
    await db.flush()
    await log_operation(db, admin, "create", "user", f"创建用户 {req.username}", ip)
    return user


async def update_user(db: AsyncSession, admin: User, user_id: int, req: UserUpdateRequest, ip: str) -> User:
    """更新用户信息"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise BusinessException("用户不存在", code=404)

    if req.role is not None:
        user.role = req.role
    if req.is_active is not None:
        user.is_active = req.is_active
        if not req.is_active:
            await revoke_all_tokens(db, user.id)

    await log_operation(db, admin, "update", "user", f"更新用户 {user.username}", ip)
    return user


async def delete_user(db: AsyncSession, admin: User, user_id: int, ip: str) -> None:
    """删除用户"""
    if user_id == admin.id:
        raise BusinessException("不能删除当前登录用户", code=400)

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise BusinessException("用户不存在", code=404)

    await log_operation(db, admin, "delete", "user", f"删除用户 {user.username}", ip)
    await db.delete(user)


async def reset_password(
    db: AsyncSession, admin: User, user_id: int, req: UserResetPasswordRequest, ip: str
) -> None:
    """重置用户密码并强制下线"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise BusinessException("用户不存在", code=404)

    user.password_hash = hash_password(req.new_password)
    await revoke_all_tokens(db, user.id)
    await log_operation(db, admin, "reset_password", "user", f"重置用户 {user.username} 密码", ip)
