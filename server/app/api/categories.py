"""
分类 API 路由
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.exceptions import success
from app.models.user import User
from app.schemas.category import CategoryCreateRequest, CategoryResponse, CategoryUpdateRequest
from app.services import category_service

router = APIRouter()


@router.get("")
async def list_categories(
    module_type: str = Query(..., pattern="^(memo|password|todo)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取分类列表"""
    cats = await category_service.list_categories(db, current_user, module_type)
    return success([CategoryResponse.model_validate(c).model_dump() for c in cats])


@router.post("")
async def create_category(
    req: CategoryCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建分类"""
    cat = await category_service.create_category(db, current_user, req)
    return success(CategoryResponse.model_validate(cat).model_dump(), "创建成功")


@router.put("/{cat_id}")
async def update_category(
    cat_id: int,
    req: CategoryUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新分类"""
    cat = await category_service.update_category(db, current_user, cat_id, req)
    return success(CategoryResponse.model_validate(cat).model_dump(), "更新成功")


@router.delete("/{cat_id}")
async def delete_category(
    cat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除分类"""
    await category_service.delete_category(db, current_user, cat_id)
    return success(message="删除成功")
