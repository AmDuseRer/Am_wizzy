"""
分类服务
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessException
from app.models.category import Category
from app.models.user import User
from app.schemas.category import CategoryCreateRequest, CategoryUpdateRequest


async def list_categories(db: AsyncSession, user: User, module_type: str) -> list[Category]:
    """获取用户指定模块的分类列表"""
    result = await db.execute(
        select(Category).where(Category.user_id == user.id, Category.module_type == module_type)
    )
    return list(result.scalars().all())


async def create_category(db: AsyncSession, user: User, req: CategoryCreateRequest) -> Category:
    """创建分类"""
    cat = Category(user_id=user.id, module_type=req.module_type, name=req.name)
    db.add(cat)
    await db.flush()
    return cat


async def update_category(db: AsyncSession, user: User, cat_id: int, req: CategoryUpdateRequest) -> Category:
    """更新分类"""
    result = await db.execute(select(Category).where(Category.id == cat_id, Category.user_id == user.id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise BusinessException("分类不存在", code=404)
    cat.name = req.name
    return cat


async def delete_category(db: AsyncSession, user: User, cat_id: int) -> None:
    """删除分类"""
    result = await db.execute(select(Category).where(Category.id == cat_id, Category.user_id == user.id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise BusinessException("分类不存在", code=404)
    await db.delete(cat)
