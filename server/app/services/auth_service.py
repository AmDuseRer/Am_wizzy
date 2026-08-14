"""
认证服务
处理登录、登出、修改密码、Token 管理
"""

import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessException
from app.core.security import create_access_token, create_view_session_token, hash_password, verify_password
from app.models.user import User, UserToken
from app.schemas.auth import ChangePasswordRequest, LoginRequest, SetViewPasswordRequest, UserInfoResponse, VerifyViewPasswordRequest
from app.services.operation_log_service import log_operation

logger = logging.getLogger(__name__)


def to_user_info(user: User) -> UserInfoResponse:
    """ORM 转用户信息响应"""
    return UserInfoResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        is_active=user.is_active,
        has_view_password=bool(user.view_password_hash),
    )


async def login(db: AsyncSession, req: LoginRequest, ip: str = "127.0.0.1") -> tuple[str, User]:
    """用户登录，返回 token 与用户对象"""
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.password_hash):
        raise BusinessException("用户名或密码错误", code=401)

    if not user.is_active:
        raise BusinessException("账号已被禁用", code=403)

    token, jti, expire = create_access_token(user.id, user.username, user.role)

    # 写入 Token 表
    token_record = UserToken(user_id=user.id, jti=jti, expires_at=expire.replace(tzinfo=None))
    db.add(token_record)
    await db.flush()

    await log_operation(db, user, "login", "auth", f"用户 {user.username} 登录", ip)
    logger.info("用户 %s 登录成功", user.username)

    return token, user


async def logout(db: AsyncSession, user: User, jti: str, ip: str = "127.0.0.1") -> None:
    """登出，revoke 当前 Token"""
    await db.execute(update(UserToken).where(UserToken.jti == jti).values(is_revoked=True))
    await log_operation(db, user, "logout", "auth", f"用户 {user.username} 登出", ip)


async def change_password(
    db: AsyncSession, user: User, req: ChangePasswordRequest, ip: str = "127.0.0.1"
) -> None:
    """修改密码，并 revoke 该用户全部 Token"""
    if not verify_password(req.old_password, user.password_hash):
        raise BusinessException("原密码错误", code=400)

    user.password_hash = hash_password(req.new_password)
    await db.execute(
        update(UserToken).where(UserToken.user_id == user.id).values(is_revoked=True)
    )
    await log_operation(db, user, "change_password", "auth", f"用户 {user.username} 修改密码", ip)


async def revoke_all_tokens(db: AsyncSession, user_id: int) -> None:
    """批量 revoke 用户所有 Token（强制下线）"""
    await db.execute(update(UserToken).where(UserToken.user_id == user_id).values(is_revoked=True))


async def get_view_password_status(user: User) -> bool:
    """是否已设置查看专用密码"""
    return bool(user.view_password_hash)


async def set_view_password(db: AsyncSession, user: User, req: SetViewPasswordRequest, ip: str = "127.0.0.1") -> None:
    """设置或修改查看专用密码"""
    if not verify_password(req.login_password, user.password_hash):
        raise BusinessException("登录密码验证失败", code=403)

    if user.view_password_hash:
        if not req.old_view_password:
            raise BusinessException("请输入原查看专用密码", code=400)
        if not verify_password(req.old_view_password, user.view_password_hash):
            raise BusinessException("原查看专用密码错误", code=400)

    user.view_password_hash = hash_password(req.view_password)
    await log_operation(db, user, "set_view_password", "auth", f"用户 {user.username} 设置查看专用密码", ip)


async def verify_view_password(db: AsyncSession, user: User, req: VerifyViewPasswordRequest, ip: str = "127.0.0.1") -> str:
    """验证查看专用密码，返回 24 小时有效的查看会话令牌"""
    if not user.view_password_hash:
        raise BusinessException("尚未设置查看专用密码", code=400)
    if not verify_password(req.view_password, user.view_password_hash):
        raise BusinessException("查看专用密码错误", code=403)

    await log_operation(db, user, "verify_view_password", "auth", f"用户 {user.username} 验证查看专用密码", ip)
    return create_view_session_token(user.id)
