"""
依赖注入模块
提供当前用户获取、admin 权限校验等 FastAPI 依赖
"""

from typing import Optional

from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import BusinessException
from app.core.security import decode_access_token
from app.models.user import User, UserToken


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    从 Authorization Bearer 头解析 JWT，校验 Token 表有效性，返回当前用户
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise BusinessException("未提供有效的认证令牌", code=401)

    token = authorization[7:]
    payload = decode_access_token(token)
    user_id = int(payload.get("sub", 0))
    jti = payload.get("jti")

    # 校验 Token 是否在白名单且未 revoke
    result = await db.execute(
        select(UserToken).where(
            UserToken.jti == jti,
            UserToken.user_id == user_id,
            UserToken.is_revoked == False,  # noqa: E712
        )
    )
    token_record = result.scalar_one_or_none()
    if not token_record:
        raise BusinessException("令牌已失效，请重新登录", code=401)

    # 获取用户
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise BusinessException("用户不存在或已被禁用", code=401)

    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """要求当前用户为 admin 角色"""
    if current_user.role != "admin":
        raise BusinessException("权限不足，需要管理员角色", code=403)
    return current_user


def get_client_ip(x_forwarded_for: Optional[str] = Header(None)) -> str:
    """从请求头获取客户端 IP"""
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return "127.0.0.1"
