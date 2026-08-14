"""
第 1 层 · 路由（Router / Controller）

职责：接收 HTTP 请求，调用 Service，把结果转成 JSON 返回。
这一层尽量「薄」——不写业务逻辑，不直接访问数据库。

类比：餐厅前台——客人点菜（HTTP），前台转给后厨（Service），再把菜端出来（JSON）。
"""

from fastapi import APIRouter, HTTPException

from demo.FastAPI_demo.schemas.todo_schema import TodoCreateRequest, TodoResponse, TodoUpdateRequest
from demo.FastAPI_demo.services import todo_service
from demo.FastAPI_demo.services.todo_service import TodoNotFoundError

# APIRouter：把一组相关接口打包，方便在 main.py 里挂载
router = APIRouter(prefix="/todos", tags=["待办"])


@router.get("", response_model=list[TodoResponse])
def list_todos():
    """
    GET /todos — 查询全部待办

    FastAPI 会自动把 list[TodoResponse] 序列化成 JSON 数组。
    """
    todos = todo_service.list_todos()
    return todos


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int):
    """GET /todos/{todo_id} — 查询单条"""
    try:
        return todo_service.get_todo(todo_id)
    except TodoNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", response_model=TodoResponse, status_code=201)
def create_todo(req: TodoCreateRequest):
    """
    POST /todos — 创建待办

    req 的类型是 TodoCreateRequest，FastAPI 会：
      1. 读取请求体 JSON
      2. 用 Pydantic 校验字段
      3. 校验失败直接返回 422，不会进入函数体
    """
    return todo_service.create_todo(req)


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, req: TodoUpdateRequest):
    """PUT /todos/{todo_id} — 更新待办"""
    try:
        return todo_service.update_todo(todo_id, req)
    except TodoNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    """DELETE /todos/{todo_id} — 删除待办（成功无响应体）"""
    try:
        todo_service.delete_todo(todo_id)
    except TodoNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
