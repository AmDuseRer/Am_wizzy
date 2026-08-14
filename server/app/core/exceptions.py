"""
统一异常处理与标准响应格式
所有 API 返回 { code, message, data } 结构
"""

from typing import Any, Generic, Optional, TypeVar

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """标准 API 响应模型"""

    code: int = 0
    message: str = "success"
    data: Optional[T] = None


class BusinessException(Exception):
    """业务异常，携带错误码与消息"""

    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


def success(data: Any = None, message: str = "success") -> dict:
    """构造成功响应"""
    return {"code": 0, "message": message, "data": data}


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器"""

    @app.exception_handler(BusinessException)
    async def business_exception_handler(request: Request, exc: BusinessException):
        return JSONResponse(
            status_code=200,
            content={"code": exc.code, "message": exc.message, "data": None},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": f"服务器内部错误: {str(exc)}", "data": None},
        )
