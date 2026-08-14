"""
备忘录 Pydantic Schema
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MemoCreateRequest(BaseModel):
    """创建备忘录"""

    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(default="", max_length=10000)
    category_id: Optional[int] = None
    is_pinned: bool = False


class MemoUpdateRequest(BaseModel):
    """更新备忘录"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, max_length=10000)
    category_id: Optional[int] = None
    is_pinned: Optional[bool] = None


class MemoResponse(BaseModel):
    """备忘录响应"""

    id: int
    user_id: int
    category_id: Optional[int]
    title: str
    content: str
    is_pinned: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MemoListQuery(BaseModel):
    """备忘录列表查询参数"""

    keyword: Optional[str] = None
    category_id: Optional[int] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
