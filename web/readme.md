# 前端（web）

Vue 3 + Vite + Element Plus 构建的单页应用。

## 目录结构

```
web/src/
├── api/           # API 请求模块（按业务拆分）
├── components/    # 公共组件（PageHeader、CategorySelect 等）
├── layouts/       # 布局组件（MainLayout 侧栏+顶栏）
├── router/        # 路由配置与全局守卫
├── stores/        # Pinia 状态（auth、app）
├── utils/         # 工具（request、date、crypto、pdf、storage）
└── views/         # 页面视图
```

## 核心模块

### 鉴权流程

1. 登录成功后 `authStore` 保存 JWT 与用户信息到 LocalStorage
2. `request.js` 拦截器自动附加 `Authorization: Bearer <token>`
3. 路由守卫拦截未登录访问；admin 路由拦截非管理员
4. 401 响应自动清 token 并跳转登录页

### 页面功能

| 路由 | 页面 | 说明 |
|------|------|------|
| /login | LoginView | 登录 |
| /users | UserManageView | 用户管理（admin） |
| /memos | MemoListView | 备忘录 CRUD、搜索、草稿、PDF |
| /passwords | PasswordListView | 密码本脱敏、二次校验、备份 |
| /todos | TodoListView | 待办管理、逾期、批量操作 |

### 表单校验

使用 Element Plus 表单 `rules`，规则与后端 Pydantic Schema 保持一致（如用户名 2-50 字符、密码 6-100 字符）。

## 开发与构建

```bash
npm install       # 安装依赖
npm run dev       # 开发服务器（端口 5173，代理 /api → 8000）
npm run build     # 生产构建到 dist/
npm run preview   # 预览构建结果
```

## 配置

`vite.config.js` 中开发代理：

```js
proxy: {
  '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true }
}
```
