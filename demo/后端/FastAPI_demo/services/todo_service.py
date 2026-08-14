"""
第 2 层 · 业务逻辑（Service）

职责：处理「能不能做、怎么做」的业务规则。
路由层不直接碰数据库，而是调用 Service。

类比：餐厅后厨——前台（路由）只接单，后厨（Service）决定怎么做菜、能不能做。
"""

from demo.FastAPI_demo.models.todo import Todo
from demo.FastAPI_demo.repositories import todo_repository
from demo.FastAPI_demo.schemas.todo_schema import TodoCreateRequest, TodoUpdateRequest


class TodoNotFoundError(Exception):
    """待办不存在时抛出，由路由层转成 HTTP 404"""


def list_todos() -> list[Todo]:
    return todo_repository.list_all()


def get_todo(todo_id: int) -> Todo:
    todo = todo_repository.get_by_id(todo_id)
    if todo is None:
        raise TodoNotFoundError(f"待办 {todo_id} 不存在")
    return todo


def create_todo(req: TodoCreateRequest) -> Todo:
    # 业务规则示例：标题去首尾空格
    title = req.title.strip()
    return todo_repository.create(title)


def update_todo(todo_id: int, req: TodoUpdateRequest) -> Todo:
    todo = todo_repository.update(
        todo_id,
        title=req.title.strip() if req.title is not None else None,
        done=req.done,
    )
    if todo is None:
        raise TodoNotFoundError(f"待办 {todo_id} 不存在")
    return todo


def delete_todo(todo_id: int) -> None:
    if not todo_repository.delete(todo_id):
        raise TodoNotFoundError(f"待办 {todo_id} 不存在")
