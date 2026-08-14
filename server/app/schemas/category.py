"""
分类 Pydantic Schema
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CategoryCreateRequest(BaseModel):
    """创建分类"""

    module_type: str = Field(..., pattern="^(memo|password|todo)$")
    name: str = Field(..., min_length=1, max_length=100)


class CategoryUpdateRequest(BaseModel):
    """更新分类"""

    name: str = Field(..., min_length=1, max_length=100)


class CategoryResponse(BaseModel):
    """分类响应"""

    id: int
    user_id: int
    module_type: str
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}
