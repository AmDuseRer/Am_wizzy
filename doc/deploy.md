# 一键化部署说明

## 概述

`deploy/install.sh` 脚本实现 Ubuntu 22.04 上一键部署小智工具箱，自动完成依赖安装、数据库初始化、后端服务配置、前端构建与 Nginx 反向代理。

## 部署架构

```
用户浏览器 → Nginx(:80)
                ├── /        → /var/www/wizzy (Vue 静态文件)
                └── /api     → Uvicorn(:8000) FastAPI
                                    └── MySQL(:3306) wizzy_db
```

## 脚本执行流程

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1/7 | apt 安装依赖 | Python3、Node.js、Nginx、MySQL |
| 2/7 | 配置 MySQL | 创建 wizzy_db 库和 wizzy 用户 |
| 3/7 | 部署后端 | 复制代码、创建 venv、pip install、生成 .env |
| 4/7 | systemd 服务 | 注册 wizzy-api.service，开机自启 |
| 5/7 | 构建前端 | npm ci && npm run build，复制到 /var/www/wizzy |
| 6/7 | 配置 Nginx | 静态资源 + API 反向代理 |
| 7/7 | 完成 | 输出访问地址和预置账号 |

## 使用方法

```bash
# 在 deploy 目录下执行
cd deploy
sudo bash install.sh
```

## 关键文件

| 文件 | 作用 |
|------|------|
| deploy/install.sh | 一键部署主脚本 |
| deploy/nginx.conf | Nginx 站点配置 |
| deploy/systemd/wizzy-api.service | 后端 systemd 单元 |

## 自动生成配置

脚本自动执行：

1. **AES_KEY**：`Fernet.generate_key()` 生成并写入 .env
2. **JWT_SECRET**：`secrets.token_hex(32)` 生成
3. **数据库初始化**：执行 init_db.sql + seed_data.py

## 服务管理

```bash
# 查看后端状态
sudo systemctl status wizzy-api

# 重启后端
sudo systemctl restart wizzy-api

# 查看日志
sudo journalctl -u wizzy-api -f

# 重载 Nginx
sudo nginx -t && sudo systemctl reload nginx
```

## 注意事项

- 需要 root 权限（sudo）
- 默认数据库密码为 wizzy123，生产环境请修改
- 脚本假设项目代码在 deploy 的上级目录（即 wizzy/ 根目录）
- 首次部署后访问 http://服务器IP，使用 admin / Admin@123 登录
