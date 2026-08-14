"""
操作日志 Pydantic Schema
"""

from datetime import datetime

from pydantic import BaseModel


class OperationLogResponse(BaseModel):
    """操作日志响应"""

    id: int
    user_id: int
    action: str
    module: str
    detail: str
    ip: str
    created_at: datetime

    model_config = {"from_attributes": True}
