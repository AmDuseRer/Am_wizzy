"""
认证相关 Pydantic Schema
"""

from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    """登录请求"""

    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""

    old_password: str = Field(..., min_length=6, max_length=100)
    new_password: str = Field(..., min_length=6, max_length=100)


class UserInfoResponse(BaseModel):
    """当前用户信息响应"""

    id: int
    username: str
    role: str
    is_active: bool
    has_view_password: bool = False

    model_config = {"from_attributes": True}


class SetViewPasswordRequest(BaseModel):
    """设置/修改查看专用密码"""

    login_password: str = Field(..., min_length=6, max_length=100)
    view_password: str = Field(..., min_length=6, max_length=100)
    old_view_password: Optional[str] = Field(None, min_length=6, max_length=100)


class VerifyViewPasswordRequest(BaseModel):
    """验证查看专用密码"""

    view_password: str = Field(..., min_length=6, max_length=100)


class ViewPasswordStatusResponse(BaseModel):
    """查看专用密码状态"""

    has_view_password: bool


class ViewSessionResponse(BaseModel):
    """查看会话响应"""

    view_session: str
    expires_in_hours: int = 24


class LoginResponse(BaseModel):
    """登录成功响应"""

    access_token: str
    token_type: str = "bearer"
    user: UserInfoResponse
