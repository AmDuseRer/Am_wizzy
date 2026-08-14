# 小智工具箱

前后端分离的个人工具箱系统，提供备忘录、密码本、待办事项等日常工具，支持多用户与数据隔离。

## 功能概览

| 模块 | 功能 |
|------|------|
| **登录鉴权** | 账号密码登录（无公开注册）；JWT + Token 表；修改密码、退出登录 |
| **用户管理**（admin） | 新增/编辑/删除用户；启用/禁用；重置密码 |
| **备忘录** | 增删改查；分类；关键词搜索；置顶；本地草稿自动保存；单条/全部 TXT 导出 |
| **密码本** | 增删改查；分类管理；列表脱敏展示；查看专用密码二次校验（24 小时会话）；复制明文；加密备份导出 |
| **TodoList 待办** | 增删改查；优先级（低/中/高）；状态流转；截止时间；逾期标记；多条件筛选；批量完成 |
| **通用** | 侧边栏折叠；亮/暗色主题；操作日志（后端记录高危操作） |

## 初始登录账号

执行 `seed_data.py` 后会创建以下预置账号，**首次登录后建议立即修改密码**：

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| **admin** | **Admin@123** | 管理员 | 可访问用户管理，含 3 条备忘录、2 条密码、4 条待办示例数据 |
| **user** | **User@123** | 普通用户 | 仅个人数据，含同等数量的示例数据 |

> 密码本查看明文需单独设置「查看专用密码」（与登录密码独立），在密码本页面点击「查看专用密码」进行配置。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus + Pinia + Axios |
| 后端 | FastAPI + SQLAlchemy（异步）+ MySQL 5.7+ |
| 鉴权 | JWT + user_tokens 表（支持主动下线） |
| 加密 | Bcrypt（用户密码）+ Fernet AES（密码本入库） |

## 目录结构

```
wizzy/
├── web/              # Vue 3 前端
├── server/           # FastAPI 后端
├── deploy/           # Nginx、systemd、一键安装脚本
└── doc/              # 架构、部署、数据库等文档
```

## 快速启动（开发环境）

### 前置条件

- Node.js 18+
- Python 3.10+
- MySQL 5.7+

### 1. 初始化数据库

```bash
mysql -u root -p < server/scripts/init_db.sql
```

### 2. 启动后端

```bash
cd server
python -m venv .venv
.venv\Scripts\activate          # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env          # Linux/macOS: cp .env.example .env
```

编辑 `.env`，至少配置 `DATABASE_URL`、`JWT_SECRET`、`AES_KEY`：

```bash
# 生成 AES 密钥（Fernet 格式）
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

写入种子数据（含 admin/user 账号及示例数据）：

```bash
python scripts/seed_data.py
```

启动 API 服务：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- API 文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/api/health

### 3. 启动前端

```bash
cd web
npm install
npm run dev
```

访问：http://localhost:5173

使用 **admin / Admin@123** 或 **user / User@123** 登录。

> 开发环境下，`web/vite.config.js` 将 `/api` 代理到后端地址，请确保 `proxy.target` 端口与后端一致（默认 `8000`）。

## 生产部署

- 一键部署：[doc/deploy.md](doc/deploy.md)
- 手工部署：[doc/手工部署.md](doc/手工部署.md)

## 文档索引

| 文档 | 说明 |
|------|------|
| [web/readme.md](web/readme.md) | 前端目录、路由、开发与构建 |
| [server/readme.md](server/readme.md) | 后端分层、API 模块、环境变量 |
| [doc/后端技术架构.md](doc/后端技术架构.md) | 整体架构设计 |
| [doc/后端程序流程.md](doc/后端程序流程.md) | 请求处理流程 |
| [doc/数据库说明.md](doc/数据库说明.md) | 表结构与索引 |
| [doc/开发环境测试说明.md](doc/开发环境测试说明.md) | 功能测试用例与故障排查 |
