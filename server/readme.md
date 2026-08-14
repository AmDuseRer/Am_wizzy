# 后端（server）

FastAPI 异步后端，提供 RESTful API。

## 目录结构

```
server/
├── main.py              # 应用入口
├── app/
│   ├── core/            # 配置、安全、数据库、异常、依赖注入
│   ├── models/          # SQLAlchemy ORM 模型
│   ├── schemas/         # Pydantic 请求/响应模型
│   ├── api/             # API 路由层
│   ├── services/        # 业务逻辑层
│   └── utils/           # 工具（PDF 生成等）
└── scripts/
    ├── init_db.sql      # 建表 SQL
    └── seed_data.py     # 种子数据
```

## 分层架构

```
API 路由 (api/) → 业务服务 (services/) → ORM 模型 (models/)
                      ↓
              安全/加密 (core/security.py)
              操作日志 (operation_log_service)
```

## API 模块

| 前缀 | 模块 | 权限 |
|------|------|------|
| /api/auth | 登录/登出/改密 | 登录用户 |
| /api/users | 用户 CRUD | admin |
| /api/categories | 分类管理 | 登录用户 |
| /api/memos | 备忘录 | 登录用户（行级隔离） |
| /api/passwords | 密码本 | 登录用户（AES 加密） |
| /api/todos | 待办 | 登录用户 |
| /api/logs | 操作日志 | 登录用户/admin |

## 安全机制

- **用户密码**：Bcrypt 加盐哈希
- **密码本**：Fernet AES 对称加密入库，列表接口脱敏
- **JWT**：签发含 jti，配合 user_tokens 表实现主动下线
- **改密/禁用**：批量 revoke 该用户全部 Token

## 启动

```bash
cd server
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # 编辑配置
python scripts/seed_data.py # 初始化数据
uvicorn main:app --reload --port 8000
```

Swagger 文档：http://127.0.0.1:8000/docs

## 环境变量

| 变量 | 说明 |
|------|------|
| DATABASE_URL | MySQL 连接串 |
| JWT_SECRET | JWT 签名密钥 |
| AES_KEY | Fernet AES 密钥 |
| CORS_ORIGINS | 允许的前端来源 |
