"""
认证 API 路由
登录、登出、修改密码、获取当前用户信息
"""

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_client_ip, get_current_user
from app.core.exceptions import success
from app.core.security import decode_access_token
from app.models.user import User
from app.schemas.auth import ChangePasswordRequest, LoginRequest, LoginResponse, SetViewPasswordRequest, UserInfoResponse, VerifyViewPasswordRequest, ViewPasswordStatusResponse, ViewSessionResponse
from app.services import auth_service

router = APIRouter()


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db), ip: str = Depends(get_client_ip)):
    """用户登录"""
    token, user = await auth_service.login(db, req, ip)
    data = LoginResponse(
        access_token=token,
        user=auth_service.to_user_info(user),
    )
    return success(data.model_dump())


@router.post("/logout")
async def logout(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ip: str = Depends(get_client_ip),
):
    """用户登出"""
    token = authorization[7:] if authorization.startswith("Bearer ") else authorization
    payload = decode_access_token(token)
    jti = payload.get("jti", "")
    await auth_service.logout(db, current_user, jti, ip)
    return success(message="登出成功")


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return success(auth_service.to_user_info(current_user).model_dump())


@router.get("/view-password/status")
async def get_view_password_status(current_user: User = Depends(get_current_user)):
    """获取查看专用密码是否已设置"""
    has = await auth_service.get_view_password_status(current_user)
    return success(ViewPasswordStatusResponse(has_view_password=has).model_dump())


@router.post("/view-password")
async def set_view_password(
    req: SetViewPasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ip: str = Depends(get_client_ip),
):
    """设置或修改查看专用密码"""
    await auth_service.set_view_password(db, current_user, req, ip)
    return success(message="查看专用密码设置成功")


@router.post("/view-password/verify")
async def verify_view_password(
    req: VerifyViewPasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ip: str = Depends(get_client_ip),
):
    """验证查看专用密码，返回 24 小时有效的查看会话"""
    view_session = await auth_service.verify_view_password(db, current_user, req, ip)
    return success(ViewSessionResponse(view_session=view_session).model_dump())


@router.post("/change-password")
async def change_password(
    req: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ip: str = Depends(get_client_ip),
):
    """修改当前用户密码"""
    await auth_service.change_password(db, current_user, req, ip)
    return success(message="密码修改成功，请重新登录")
