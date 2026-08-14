"""
第 3 层 · 数据访问（Repository / DAO）

职责：只管「存、取、改、删」，不管业务规则。
类比：仓库管理员——你告诉他编号，他帮你找货、上架、下架。

本 demo 用内存列表模拟数据库，重启后数据会消失。
真实项目里这里会写 SQL / ORM（如 SQLAlchemy）。
"""

from demo.FastAPI_demo.models.todo import Todo

# 模拟数据库表：进程内全局列表
_fake_db: list[Todo] = []
_next_id: int = 1


def list_all() -> list[Todo]:
    """查询全部待办"""
    return list(_fake_db)


def get_by_id(todo_id: int) -> Todo | None:
    """按 id 查询，找不到返回 None"""
    for todo in _fake_db:
        if todo.id == todo_id:
            return todo
    return None


def create(title: str) -> Todo:
    """插入一条新待办"""
    global _next_id
    todo = Todo(id=_next_id, title=title, done=False)
    _fake_db.append(todo)
    _next_id += 1
    return todo


def update(todo_id: int, title: str | None, done: bool | None) -> Todo | None:
    """更新字段，只改传入的非 None 值"""
    todo = get_by_id(todo_id)
    if todo is None:
        return None
    if title is not None:
        todo.title = title
    if done is not None:
        todo.done = done
    return todo


def delete(todo_id: int) -> bool:
    """删除，成功返回 True"""
    todo = get_by_id(todo_id)
    if todo is None:
        return False
    _fake_db.remove(todo)
    return True
