# Vue Router 与路由守卫 · 练习 1 / 3 / 4

> 对应学习题：地址映射、Vue Router 换页、beforeEach 路由守卫  
> 练会：path 对应页面、router-view 换组件、登录与 admin 权限拦截

---

## 目录结构

```
demo/前端/路由守卫_demo/
├── README.md                  # 本文件
├── package.json               # 提供 npm test 快捷命令（仅练习1）
├── lesson1-route-map.js       # 练习1：纯 JS 地址映射 + 自动测试
├── lesson3-router-basic.html  # 练习3：Vue Router 基础换页（浏览器）
└── lesson4-router-guard.html  # 练习4：beforeEach 路由守卫（浏览器）
```

---

## 练习 1：地址 -> 页面映射（Node.js）

### 运行方式（Windows PowerShell / CMD）

在仓库根目录 `wizzy` 下：

```powershell
cd demo\前端\路由守卫_demo
node lesson1-route-map.js
```

或：

```powershell
npm test
```

**说明：**

- **无需** `npm install`（零依赖）
- **无需** 浏览器、后端或 wizzy 主项目
- 需要已安装 **Node.js 18+**（终端执行 `node -v` 检查）

### 预期输出（大致样子）

```
=== 练习 1：地址 -> 页面映射 ===

[OK] 访问 /memos 应显示备忘录
[OK] 访问 /users 应显示用户管理
[OK] 访问 /abc 应返回 404
[OK] 访问 /login 应显示登录页
[OK] 访问 /todos 应显示待办列表

结果：5 通过，0 失败
全部通过。你可以修改 routes 对象，再运行 node lesson1-route-map.js 观察变化。
```

若有失败会显示 `[FAIL]` 和期望值/实际值对比。

---

## 练习 3：Vue Router 基础换页（浏览器）

### 运行方式

1. 用资源管理器打开 `demo\前端\路由守卫_demo\lesson3-router-basic.html`
2. 或 PowerShell 中执行：

```powershell
start demo\前端\路由守卫_demo\lesson3-router-basic.html
```

**说明：**

- 需要能访问 CDN（`unpkg.com`）加载 Vue 和 Vue Router
- 使用 hash 路由（`#/memos`），**无需** 启动本地服务器
- 首次打开若空白，检查网络或稍等 CDN 加载

### 手动测试步骤与预期

| 操作 | 预期 |
|------|------|
| 打开文件 | 地址栏含 `#/memos`，页面显示 `[备忘录] 这是备忘录页` |
| 点击「密码本」 | 地址变为 `#/passwords`，显示 `[密码本] 这是密码本页` |
| 浏览器后退 | 回到备忘录页 |
| 手动改地址为 `#/passwords` 回车 | 直接显示密码本页 |

---

## 练习 4：beforeEach 路由守卫（浏览器）

### 运行方式

```powershell
start demo\前端\路由守卫_demo\lesson4-router-guard.html
```

### 手动测试步骤与预期

| 步骤 | 操作 | 预期 |
|------|------|------|
| 1 | 打开页面，默认未登录，点「备忘录」 | 被赶到 `#/login`，显示登录页 |
| 2 | 点「切换登录/登出」，再点「备忘录」 | 显示 `[备忘录] 需要登录才能访问` |
| 3 | 角色为 user，点「用户管理」 | 被赶回 `#/memos` |
| 4 | 点「切换 admin / user」，再点「用户管理」 | 显示 `[用户管理] 需要 admin 角色` |
| 5 | 已登录时手动打开 `#/login` | 自动跳到 `#/memos` |

页面底部「守卫日志」会显示类似：

```
从 / 到 /memos -> 未登录，重定向到 /login
```

---

## 练完后对照项目文件

| 顺序 | 文件 | 对照内容 |
|------|------|----------|
| 1 | `web/src/main.js` | `app.use(router)` 挂载路由 |
| 2 | `web/src/App.vue` | 根组件 `<router-view />` |
| 3 | `web/src/router/index.js` | 路由表 + `beforeEach` 守卫（核心） |
| 4 | `web/src/stores/auth.js` | `isLoggedIn`、`isAdmin` 来源 |
| 5 | `web/src/layouts/MainLayout.vue` | 嵌套路由 + 侧边栏菜单 |
