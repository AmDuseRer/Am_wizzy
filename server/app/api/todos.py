"""
待办任务 API 路由
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.exceptions import success
from app.models.user import User
from app.schemas.todo import TodoBatchUpdateRequest, TodoCreateRequest, TodoUpdateRequest
from app.services import todo_service

router = APIRouter()


@router.get("")
async def list_todos(
    keyword: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    category_id: int | None = None,
    overdue_only: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """分页查询待办"""
    items, total = await todo_service.list_todos(
        db, current_user, keyword, status, priority, category_id, overdue_only, page, page_size
    )
    return success({
        "items": [i.model_dump() for i in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.post("")
async def create_todo(
    req: TodoCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建待办"""
    todo = await todo_service.create_todo(db, current_user, req)
    return success(todo.model_dump(), "创建成功")


@router.put("/{todo_id}")
async def update_todo(
    todo_id: int,
    req: TodoUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新待办"""
    todo = await todo_service.update_todo(db, current_user, todo_id, req)
    return success(todo.model_dump(), "更新成功")


@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除待办"""
    await todo_service.delete_todo(db, current_user, todo_id)
    return success(message="删除成功")


@router.post("/batch-update")
async def batch_update(
    req: TodoBatchUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """批量更新待办状态"""
    count = await todo_service.batch_update_status(db, current_user, req.ids, req.status)
    return success({"updated": count}, f"已更新 {count} 条")
