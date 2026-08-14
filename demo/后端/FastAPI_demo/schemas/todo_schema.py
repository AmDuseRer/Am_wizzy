"""
数据映射层（Schema）—— 连接「HTTP 世界」和「程序内部世界」

前端 / 客户端发的是 JSON，程序内部用的是 Todo 对象。
Pydantic Schema 负责：
  1. 校验入参（类型、长度、必填）
  2. 定义出参格式（返回给前端的 JSON 长什么样）

类比：海关表格——入境要填表（Request），出境给你盖章的凭证（Response）。
"""

from pydantic import BaseModel, Field


class TodoCreateRequest(BaseModel):
    """创建待办时，客户端 POST 的 JSON 体"""

    title: str = Field(..., min_length=1, max_length=100, description="待办标题")


class TodoUpdateRequest(BaseModel):
    """更新待办时，客户端 PUT 的 JSON 体（字段均可选）"""

    title: str | None = Field(None, min_length=1, max_length=100)
    done: bool | None = None


class TodoResponse(BaseModel):
    """返回给客户端的待办 JSON 结构"""

    id: int
    title: str
    done: bool

    # 允许从 dataclass / ORM 对象自动转换
    model_config = {"from_attributes": True}
