"""
密码本 Pydantic Schema
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PasswordCreateRequest(BaseModel):
    """创建密码条目"""

    site_name: str = Field(..., min_length=1, max_length=200)
    username: str = Field(default="", max_length=200)
    password: str = Field(..., min_length=1, max_length=500)
    url: str = Field(default="", max_length=500)
    remark: str = Field(default="", max_length=2000)
    category_id: Optional[int] = None


class PasswordUpdateRequest(BaseModel):
    """更新密码条目"""

    site_name: Optional[str] = Field(None, min_length=1, max_length=200)
    username: Optional[str] = Field(None, max_length=200)
    password: Optional[str] = Field(None, min_length=1, max_length=500)
    url: Optional[str] = Field(None, max_length=500)
    remark: Optional[str] = Field(None, max_length=2000)
    category_id: Optional[int] = None


class PasswordResponse(BaseModel):
    """密码条目响应（脱敏）"""

    id: int
    user_id: int
    category_id: Optional[int]
    site_name: str
    username: str
    password_masked: str  # 脱敏密码
    url: str
    remark: str
    created_at: datetime
    updated_at: datetime


class PasswordRevealRequest(BaseModel):
    """查看明文密码二次校验"""

    view_password: Optional[str] = Field(None, min_length=6, max_length=100)
    view_session: Optional[str] = None


class PasswordRevealResponse(BaseModel):
    """明文密码响应"""

    id: int
    password: str
