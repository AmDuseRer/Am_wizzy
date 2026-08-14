"""
通用分页响应 Schema
"""

from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页列表响应"""

    items: List[T]
    total: int
    page: int
    page_size: int
