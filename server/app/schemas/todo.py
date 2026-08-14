"""
待办任务 Pydantic Schema
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TodoCreateRequest(BaseModel):
    """创建待办"""

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=5000)
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    status: str = Field(default="pending", pattern="^(pending|in_progress|completed|cancelled)$")
    category_id: Optional[int] = None
    due_at: Optional[datetime] = None


class TodoUpdateRequest(BaseModel):
    """更新待办"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed|cancelled)$")
    category_id: Optional[int] = None
    due_at: Optional[datetime] = None


class TodoBatchUpdateRequest(BaseModel):
    """批量更新待办状态"""

    ids: list[int] = Field(..., min_length=1)
    status: str = Field(..., pattern="^(pending|in_progress|completed|cancelled)$")


class TodoResponse(BaseModel):
    """待办响应"""

    id: int
    user_id: int
    category_id: Optional[int]
    title: str
    description: str
    priority: str
    status: str
    due_at: Optional[datetime]
    completed_at: Optional[datetime]
    is_overdue: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
