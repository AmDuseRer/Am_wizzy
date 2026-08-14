"""
用户管理 Pydantic Schema
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserCreateRequest(BaseModel):
    """创建用户请求（admin）"""

    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    role: str = Field(default="user", pattern="^(admin|user)$")


class UserUpdateRequest(BaseModel):
    """更新用户请求"""

    role: Optional[str] = Field(None, pattern="^(admin|user)$")
    is_active: Optional[bool] = None


class UserResetPasswordRequest(BaseModel):
    """重置密码请求"""

    new_password: str = Field(..., min_length=6, max_length=100)


class UserResponse(BaseModel):
    """用户列表项响应"""

    id: int
    username: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
