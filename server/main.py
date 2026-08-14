"""
小智工具箱 - FastAPI 应用入口
负责创建 FastAPI 实例、注册路由、中间件与 CORS 配置
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, categories, logs, memos, passwords, todos, users
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化日志"""
    setup_logging()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="小智工具箱后端 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册全局异常处理器
register_exception_handlers(app)

# 注册 API 路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户管理"])
app.include_router(categories.router, prefix="/api/categories", tags=["分类"])
app.include_router(memos.router, prefix="/api/memos", tags=["备忘录"])
app.include_router(passwords.router, prefix="/api/passwords", tags=["密码本"])
app.include_router(todos.router, prefix="/api/todos", tags=["待办"])
app.include_router(logs.router, prefix="/api/logs", tags=["操作日志"])


@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {"code": 0, "message": "ok", "data": {"status": "healthy"}}
