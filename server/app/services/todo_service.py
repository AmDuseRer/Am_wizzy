"""
待办任务服务
支持逾期判定、多条件筛选、批量更新
"""

from datetime import datetime

from sqlalchemy import case, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessException
from app.models.todo import Todo
from app.models.user import User
from app.schemas.todo import TodoCreateRequest, TodoResponse, TodoUpdateRequest


def to_todo_response(todo: Todo) -> TodoResponse:
    """ORM 转响应，计算逾期状态"""
    now = datetime.now()
    is_overdue = (
        todo.due_at is not None
        and todo.due_at < now
        and todo.status not in ("completed", "cancelled")
    )
    return TodoResponse(
        id=todo.id,
        user_id=todo.user_id,
        category_id=todo.category_id,
        title=todo.title,
        description=todo.description,
        priority=todo.priority,
        status=todo.status,
        due_at=todo.due_at,
        completed_at=todo.completed_at,
        is_overdue=is_overdue,
        created_at=todo.created_at,
        updated_at=todo.updated_at,
    )


async def list_todos(
    db: AsyncSession,
    user: User,
    keyword: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    category_id: int | None = None,
    overdue_only: bool = False,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[TodoResponse], int]:
    """分页查询待办，支持多条件筛选"""
    query = select(Todo).where(Todo.user_id == user.id)
    count_query = select(func.count(Todo.id)).where(Todo.user_id == user.id)

    if keyword:
        kw_filter = or_(Todo.title.contains(keyword), Todo.description.contains(keyword))
        query = query.where(kw_filter)
        count_query = count_query.where(kw_filter)

    if status:
        query = query.where(Todo.status == status)
        count_query = count_query.where(Todo.status == status)

    if priority:
        query = query.where(Todo.priority == priority)
        count_query = count_query.where(Todo.priority == priority)

    if category_id is not None:
        query = query.where(Todo.category_id == category_id)
        count_query = count_query.where(Todo.category_id == category_id)

    if overdue_only:
        now = datetime.now()
        overdue_filter = (
            Todo.due_at.isnot(None)
            & (Todo.due_at < now)
            & (Todo.status.notin_(["completed", "cancelled"]))
        )
        query = query.where(overdue_filter)
        count_query = count_query.where(overdue_filter)

    total = (await db.execute(count_query)).scalar() or 0
    # 已完成排最下，其余按截止时间倒序（无截止日期的排在该组最后）
    query = query.order_by(
        case((Todo.status == "completed", 1), else_=0),
        Todo.due_at.is_(None),
        Todo.due_at.desc(),
    ).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    todos = list(result.scalars().all())
    return [to_todo_response(t) for t in todos], total


async def get_todo(db: AsyncSession, user: User, todo_id: int) -> Todo:
    """获取单条待办"""
    result = await db.execute(select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id))
    todo = result.scalar_one_or_none()
    if not todo:
        raise BusinessException("待办不存在", code=404)
    return todo


async def create_todo(db: AsyncSession, user: User, req: TodoCreateRequest) -> TodoResponse:
    """创建待办"""
    todo = Todo(
        user_id=user.id,
        title=req.title,
        description=req.description,
        priority=req.priority,
        status=req.status,
        category_id=req.category_id,
        due_at=req.due_at,
    )
    db.add(todo)
    await db.flush()
    return to_todo_response(todo)


async def update_todo(db: AsyncSession, user: User, todo_id: int, req: TodoUpdateRequest) -> TodoResponse:
    """更新待办，状态变为 completed 时记录完成时间"""
    todo = await get_todo(db, user, todo_id)
    if req.title is not None:
        todo.title = req.title
    if req.description is not None:
        todo.description = req.description
    if req.priority is not None:
        todo.priority = req.priority
    if req.status is not None:
        todo.status = req.status
        if req.status == "completed" and todo.completed_at is None:
            todo.completed_at = datetime.now()
        elif req.status != "completed":
            todo.completed_at = None
    if req.category_id is not None:
        todo.category_id = req.category_id
    if req.due_at is not None:
        todo.due_at = req.due_at
    return to_todo_response(todo)


async def delete_todo(db: AsyncSession, user: User, todo_id: int) -> None:
    """删除待办"""
    todo = await get_todo(db, user, todo_id)
    await db.delete(todo)


async def batch_update_status(
    db: AsyncSession, user: User, ids: list[int], status: str
) -> int:
    """批量更新待办状态"""
    now = datetime.now()
    values = {"status": status}
    if status == "completed":
        values["completed_at"] = now
    else:
        values["completed_at"] = None

    result = await db.execute(
        update(Todo)
        .where(Todo.id.in_(ids), Todo.user_id == user.id)
        .values(**values)
    )
    return result.rowcount
