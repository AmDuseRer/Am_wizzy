"""
FastAPI 应用入口

运行方式（在项目根目录 wizzy/ 下执行）：

    pip install -r demo/FastAPI_demo/requirements.txt
    uvicorn demo.FastAPI_demo.main:app --reload

然后打开：
    http://127.0.0.1:8000/docs   ← 自动生成的交互式 API 文档
"""

from fastapi import FastAPI

from demo.FastAPI_demo.api.todo_router import router as todo_router

# 创建 FastAPI 应用实例（整个程序的「总机」）
app = FastAPI(
    title="FastAPI 三层架构 Demo",
    description="极简待办 API，演示路由 → 业务 → 数据访问 的分层",
)

# 把路由模块「挂载」到应用上
# 最终 URL = 这里没有 prefix，所以就是 /todos、/todos/{id} 等
app.include_router(todo_router)


@app.get("/")
def root():
    """健康检查 / 欢迎页"""
    return {"message": "欢迎！访问 /docs 查看并测试所有接口"}
