# Pinia 练习 1~3：共用仓库 / 持久化 / defineStore 骨架

> 对应学习题：Pinia 状态管理入门前三题  
> 练会：共用数据、localStorage 持久化、state/getters/actions 结构

---

## 目录结构

```
demo/前端/Pinia_demo/
├── package.json      # 零依赖，仅提供 npm test 快捷命令
├── run-tests.js      # 练习 1~3 合一的 Node 自动测试
└── README.md         # 本文件
```

---

## 运行方式（Windows PowerShell / CMD）

在仓库根目录 `wizzy` 下：

```powershell
cd demo\前端\Pinia_demo
node run-tests.js
```

或：

```powershell
npm test
```

**说明：**

- **无需** `npm install`（脚本零依赖，只用 Node.js 自带能力）
- **无需** 打开浏览器、启动后端或 wizzy 主项目
- 需要已安装 **Node.js 18+**（在终端执行 `node -v` 检查）

---

## 预期输出（大致样子）

全部通过时，终端应类似：

```
========================================
  Pinia 练习 1~3 自动测试（Node 版）
========================================

========================================
  练习1：共用仓库（多个模块读同一份数据）
========================================
  [登录页] 登录成功 {"token":"fake-token-abc","userInfo":{"username":"admin","role":"admin"}}
  [请求模块] 拿到的 token: fake-token-abc
  [侧边栏] 是否管理员: true
[OK] 1.1 登录后三处都能读到 token
     token=fake-token-abc
[OK] 1.2 登录后侧边栏识别为管理员
     isAdmin=true
  [请求模块] 拿到的 token: (空)
[OK] 1.3 清空 token 后请求模块读到空（未登录）
     token 为空字符串

========================================
  练习2：持久化（模拟刷新后恢复登录态）
========================================
  [写入] 已保存到 localStorage
  [刷新] 模拟页面刷新，内存清空 -> null
  [恢复] 从 localStorage 读回 -> {"token":"persist-token-123","userInfo":{"username":"user"}}
[OK] 2.1 恢复后 token 正确
     token=persist-token-123
[OK] 2.2 恢复后用户名正确
     username=user
  [删除] 清除 localStorage 后 -> null
[OK] 2.3 删除后无法恢复（相当于登出/清缓存）
     getItem 返回 null

========================================
  练习3：迷你 defineStore（state / getters / actions）
========================================
  [初始] isLoggedIn: false
[OK] 3.1 初始未登录
     isLoggedIn=false
  [admin 登录] isLoggedIn: true isAdmin: true
[OK] 3.2 admin 登录后 isLoggedIn 为 true
     isLoggedIn=true
[OK] 3.3 admin 登录后 isAdmin 为 true
     isAdmin=true
  [登出] isLoggedIn: false
[OK] 3.4 登出后 isLoggedIn 为 false
     isLoggedIn=false
  [user 登录] isLoggedIn: true isAdmin: false
[OK] 3.5 user 登录后 isLoggedIn 为 true
     isLoggedIn=true
[OK] 3.6 user 登录后 isAdmin 为 false
     isAdmin=false

========================================
  测试结果：12 通过，0 失败
========================================

练完请对照主项目：
  web/src/stores/auth.js   <- 练习3 的 defineStore 真身
  web/src/main.js          <- persist 插件注册
  web/src/utils/request.js <- 练习1 请求模块读 token
```

若有 `[FAIL]` 或最后一行显示 `N 失败`，说明对应练习逻辑有误，打开 `run-tests.js` 对照检查。

---

## 三题分别练什么

| 题号 | 要练会什么 | 脚本里对应函数 |
|------|------------|----------------|
| 1 | 登录页、请求模块、侧边栏读**同一份** token | `exercise1()` |
| 2 | 刷新后内存清空，从 localStorage **恢复**登录态 | `exercise2()` |
| 3 | `state` / `getters` / `actions` 三块骨架 | `exercise3()` 里的 `createMiniStore` |

---

## 练完对照主项目

| 本 demo | wizzy 主项目 |
|---------|----------------|
| `authBox` 共用对象 | `web/src/stores/auth.js` 的 Pinia 仓库 |
| `localStorage.setItem('wizzy-auth-practice')` | `persist: { key: 'wizzy-auth' }` |
| `createMiniStore` | `defineStore('auth', { state, getters, actions })` |
| `requestModuleGetToken()` | `web/src/utils/request.js` 读 `authStore.token` |
| `sidebarCheckAdmin()` | `web/src/layouts/MainLayout.vue` 读 `authStore.isAdmin` |

建议阅读顺序：`stores/auth.js` -> `main.js` -> `LoginView.vue` -> `router/index.js` -> `utils/request.js`

---

## 自检清单

- [ ] 能说出练习1：Pinia 就是「全站共用一本记事本」
- [ ] 能说出练习2：`persist` 把记事本抄一份到 localStorage，刷新再抄回来
- [ ] 能说出练习3：`state` 存数据，`getters` 算结果，`actions` 改数据
