# Vue Router 与路由守卫学习笔记

> 结合本项目（wizzy 小智工具箱）的通俗讲解，面向零基础。  
> 动手练习脚本（练习 1 / 3 / 4）：`demo/前端/路由守卫_demo/`

---

## 目录

1. [一句话理解](#一句话理解)
2. [Vue Router 是什么](#vue-router-是什么)
3. [路由守卫是什么](#路由守卫是什么)
4. [在本项目中的作用](#在本项目中的作用)
5. [不用 vs 用了](#不用-vs-用了)
6. [实质好处（带对比）](#实质好处带对比)
7. [代码写在哪（三层位置）](#代码写在哪三层位置)
8. [路由表与 beforeEach 基础骨架](#路由表与-beforeeach-基础骨架)
9. [在本项目里具体怎么用](#在本项目里具体怎么用)
10. [一次完整导航流程](#一次完整导航流程)
11. [动手练习（5 道题）](#动手练习5-道题)
12. [练完后对照项目文件](#练完后对照项目文件)
13. [总结](#总结)

---

## 一句话理解

**Vue Router 负责「地址栏换地址 → 页面自动切换」；路由守卫是在切换前站岗的保安，统一检查「登录了吗？是管理员吗？」，不行就改道，不用每个页面各自写一遍。**

---

## Vue Router 是什么

小智工具箱不只有一个页面，有登录页、备忘录、密码本、待办、用户管理等。浏览器地址栏里的 `/login`、`/memos`、`/users` 就是不同的「门牌号」。

**Vue Router** 就是 Vue 官方的路由库，干两件事：

1. **维护一张「门牌表」**：哪个地址对应哪个页面组件
2. **监听地址变化**：地址变了，就在 `<router-view />` 里自动换成对应页面

可以想成：

- **路由表（routes）** = 楼里的门牌目录
- **`<router-view />`** = 墙上的一块「显示区」，Router 决定这里放哪一页
- **`<router-link>` 或 `router.push()`** = 按电梯 / 走楼梯去某个门牌

本项目路由表在 `web/src/router/index.js`：

| 地址 | 页面 | 谁可以看 |
|------|------|----------|
| `/login` | 登录页 | 谁都能看（公开） |
| `/memos` | 备忘录 | 登录后 |
| `/passwords` | 密码本 | 登录后 |
| `/todos` | 待办 | 登录后 |
| `/users` | 用户管理 | 只有管理员 |

---

## 路由守卫是什么

**路由守卫（Route Guard）** = 在「真正换页之前」执行的检查函数。

本项目用的是**全局前置守卫** `router.beforeEach`：每次跳转前都会跑一遍，像门口保安：

- 没登录？ → 赶去 `/login`
- 普通用户要去 `/users`？ → 赶回 `/memos`
- 已登录还去 `/login`？ → 送回首页

守卫里读的是 Pinia 的 `authStore.isLoggedIn` 和 `authStore.isAdmin`（定义在 `web/src/stores/auth.js`），和侧边栏「是否显示用户管理」用的是同一套规则。

---

## 在本项目中的作用

### 1. 当「全站页面调度员」

点侧边栏「备忘录」「密码本」，或登录成功后 `router.push('/')`，都是 Router 在换地址、换页面。没有它，`.vue` 文件只是文件，浏览器不知道现在该显示哪一个。

### 2. 当「统一鉴权入口」

登录检查、管理员权限检查集中在 `router/index.js` 的 `beforeEach` 里，**写一次，全站生效**。不用在每个业务页面开头重复写「没 token 就跳走」。

### 3. 支撑「像正常网站一样」的行为

- 刷新浏览器仍停在当前页（如 `/memos`）
- 可以收藏、分享某个功能的链接
- 浏览器前进 / 后退能正确换页

**不可或缺在哪？** 本项目必须登录才能用；没有 Router，多页面无法切换；没有守卫，用户改地址栏就能绕过登录或进管理页。

---

## 不用 vs 用了

### 场景 A：打开网站、切换功能

| 不用 Router | 用了 Router |
|-------------|-------------|
| 永远只显示一个页面，或自己写大量 `v-if` 切换 | 地址栏变 `/memos`、`/passwords`，`<router-view />` 自动换页 |

### 场景 B：没登录就访问 `/passwords`

| 不用守卫 | 用了守卫 |
|----------|----------|
| 可能先看到密码页，再在页面里弹窗 / 跳转，体验乱 | 守卫直接拦到 `/login`，页面根本打不开 |

### 场景 C：普通用户访问 `/users`

| 不用守卫 | 用了守卫 |
|----------|----------|
| 可能短暂看到管理页，或每个页面各自判断、容易漏 | 统一拦到 `/memos`，一处规则全站生效 |

### 场景 D：已登录还打开 `/login`

| 不用守卫 | 用了守卫 |
|----------|----------|
| 又看到登录页，用户困惑 | 自动送回首页 `/` |

### 场景 E：刷新浏览器

| 不用 Router | 用了 Router |
|-------------|-------------|
| 很难记住「刚才在哪一页」 | 刷新后仍停在 `/memos` 等当前地址 |

---

## 实质好处（带对比）

### 好处一：一个入口管全站页面切换

| 不用 | 用了 |
|------|------|
| 在 `App.vue` 里写 `v-if="当前是备忘录"`、`v-if="当前是密码本"`，每加一个功能改一大块 | `App.vue` 只有一个 `<router-view />`，新功能在 `router/index.js` 加一条路由即可 |

### 好处二：登录检查写一次，全站生效

| 不用 | 用了 |
|------|------|
| 备忘录、密码本、待办、用户管理每个页面开头都要写「没 token 就跳登录」 | 守卫里一行 `if (!authStore.isLoggedIn) next('/login')`，所有非公开页都受保护 |

### 好处三：管理员权限集中控制

| 不用 | 用了 |
|------|------|
| 用户管理页可能漏判，普通用户改地址栏就能进 | `/users` 带 `meta: { admin: true }`，守卫里 `isAdmin` 为 false 就送回 `/memos` |

### 好处四：地址栏和菜单保持一致

| 不用 | 用了 |
|------|------|
| 点了「密码本」，地址仍是 `/`，刷新又回到默认页 | 菜单 `index="/passwords"` + `router`，地址变成 `/passwords`，可收藏、可分享 |

### 好处五：和登录、登出、接口报错配合顺畅

| 不用 | 用了 |
|------|------|
| 登录成功不知道跳哪；401 时各页面各自处理 | 登录后 `router.push('/')`；登出、`request.js` 里 401 时 `router.push('/login')`，行为统一 |

---

## 代码写在哪（三层位置）

Router **不是**全部写在某个 `.vue` 里，分三层：

| 做什么 | 写在哪 | 例子 |
|--------|--------|------|
| **安装** Router | `web/src/main.js` | `import router from './router'`、`app.use(router)` |
| **定义**路由表 + 守卫 | `web/src/router/index.js` | `routes`、`createRouter`、`beforeEach` |
| **使用** Router | 各 `.vue` 或 `.js` | `<router-view />`、`<router-link>`、`useRouter()`、`router.push()` |

### 相关文件一览

| 文件 | 作用 |
|------|------|
| `web/src/main.js` | 挂载 Router |
| `web/src/App.vue` | 根级 `<router-view />` |
| `web/src/router/index.js` | 路由表 + 全局守卫（核心） |
| `web/src/layouts/MainLayout.vue` | 嵌套路由布局 + 侧边栏菜单 + 内层 `<router-view />` |
| `web/src/views/LoginView.vue` | 登录成功后 `router.push('/')` |
| `web/src/utils/request.js` | 401 时 `router.push('/login')` |
| `web/src/stores/auth.js` | 守卫读的 `isLoggedIn`、`isAdmin` |

---

## 路由表与 beforeEach 基础骨架

### 最小路由表

```javascript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', component: () => import('@/views/LoginView.vue') },
  { path: '/memos', component: () => import('@/views/MemoListView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
```

### 嵌套路由（本项目主布局）

主界面共用左侧边栏，只有中间内容区换页，所以 `/` 用 `MainLayout`，子页面写在 `children` 里：

```javascript
{
  path: '/',
  component: () => import('@/layouts/MainLayout.vue'),
  redirect: '/memos',
  children: [
    { path: 'memos', component: () => import('@/views/MemoListView.vue') },
    { path: 'users', component: () => import('@/views/UserManageView.vue'), meta: { admin: true } },
  ],
}
```

### meta 字段

路由上可以挂**自定义说明**，守卫里用 `to.meta.xxx` 读取：

| meta 字段 | 含义（本项目约定） |
|-----------|-------------------|
| `{ public: true }` | 公开页，未登录也能访问（如 `/login`） |
| `{ admin: true }` | 仅管理员可访问（如 `/users`） |
| `{ title: '备忘录' }` | 页面标题（可给顶栏用） |

### beforeEach 三个参数

```javascript
router.beforeEach((to, from, next) => {
  // to   = 要去哪（目标路由）
  // from = 从哪来（当前路由）
  // next = 放行函数：next() 放行；next('/login') 改道
})
```

### 本项目完整守卫逻辑

```javascript
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // 1. 公开页（登录页）
  if (to.meta.public) {
    if (authStore.isLoggedIn && to.path === '/login') {
      next('/')           // 已登录别再看登录页
    } else {
      next()              // 放行
    }
    return
  }

  // 2. 非公开页：必须先登录
  if (!authStore.isLoggedIn) {
    next('/login')
    return
  }

  // 3. 管理员页：必须是 admin
  if (to.meta.admin && !authStore.isAdmin) {
    next('/memos')
    return
  }

  next()                  // 全部通过，放行
})
```

### 三个易错点

1. **`next()` 必须调用**，否则页面会卡住不跳转
2. **某个分支 `return` 前已经 `next(...)` 了**，不要后面再 `next()` 一次
3. **守卫里用 Pinia** 要在 `beforeEach` 回调里调 `useAuthStore()`，不能写在文件顶层（那时 Pinia 可能还没装好）

---

## 在本项目里具体怎么用

### 第 1 步：在 main.js 安装（只做一次）

```javascript
import router from './router'

app.use(router)
app.mount('#app')
```

### 第 2 步：根组件放 router-view

`web/src/App.vue` 只有一行核心模板：

```vue
<template>
  <router-view />
</template>
```

Router 根据地址在这里渲染「登录页」或「带侧边栏的主布局」。

### 第 3 步：主布局里再嵌一层 router-view

`MainLayout.vue` 负责侧边栏 + 顶栏，中间内容区再有一个 `<router-view />`，子路由（备忘录、密码本等）显示在这里。

侧边栏菜单加了 `router` 属性，点击会自动改地址：

```vue
<el-menu router ...>
  <el-menu-item index="/memos">备忘录列表</el-menu-item>
  <el-menu-item index="/users" v-if="authStore.isAdmin">用户列表</el-menu-item>
</el-menu>
```

### 第 4 步：登录 / 登出时编程式跳转

```javascript
import { useRouter } from 'vue-router'

const router = useRouter()

// 登录成功
router.push('/')

// 登出
router.push('/login')
```

---

## 一次完整导航流程

以「未登录用户手动在地址栏输入 `/memos`」为例：

```
1. 浏览器地址变为 /memos
2. Vue Router 准备加载 MemoListView
3. beforeEach 触发：
   - to.path = '/memos'
   - to.meta.public 不存在 → 不是公开页
   - authStore.isLoggedIn = false
   - 执行 next('/login')，改道
4. 最终显示 LoginView，地址变为 /login
5. 用户登录成功 → authStore.login() → router.push('/')
6. 再次触发 beforeEach：
   - isLoggedIn = true，无 admin 要求 → next() 放行
7. 显示 MainLayout + MemoListView
```

---

## 动手练习（5 道题）

由浅入深，尽量自包含。练习 1 / 3 / 4 已有可执行脚本，见 `demo/前端/路由守卫_demo/`。

---

### 练习 1：地址和页面的对应关系

#### 要练会什么

理解 Router 的核心：**地址（path）决定显示哪一页**。

#### 可执行代码

```
demo/前端/路由守卫_demo/lesson1-route-map.js
```

#### 运行方式（Windows PowerShell / CMD）

在仓库根目录 `wizzy` 下：

```powershell
cd demo\前端\路由守卫_demo
node lesson1-route-map.js
```

或：

```powershell
npm test
```

- **无需** `npm install`（零依赖）
- **无需** 浏览器、后端或 wizzy 主项目
- 需要 **Node.js 18+**

#### 预期输出

```
=== 练习 1：地址 -> 页面映射 ===

[OK] 访问 /memos 应显示备忘录
[OK] 访问 /users 应显示用户管理
[OK] 访问 /abc 应返回 404
[OK] 访问 /login 应显示登录页
[OK] 访问 /todos 应显示待办列表

结果：5 通过，0 失败
```

#### 核心逻辑（摘要）

```javascript
const routes = {
  '/login': '登录页',
  '/memos': '备忘录',
  '/users': '用户管理',
}

function go(path) {
  const page = routes[path]
  if (!page) return { ok: false, msg: '404 找不到页面' }
  return { ok: true, page, path }
}
```

---

### 练习 2：手写路由守卫逻辑（纯 JS）

#### 要练会什么

理解 `beforeEach` 在干什么：**跳转前先检查登录和管理员身份**，再决定放行或改道。

#### 怎么做

在浏览器控制台（F12 → Console）粘贴运行，或新建 `guard-practice.js` 用 `node` 执行。

#### 核心代码

```javascript
const auth = { token: '', role: 'user' }

const routes = {
  '/login': { public: true },
  '/memos': {},
  '/users': { admin: true },
}

function navigate(path) {
  const route = routes[path]
  if (!route) return { result: 'fail', reason: '404' }

  if (route.public) {
    if (auth.token && path === '/login') return { result: 'redirect', to: '/memos' }
    return { result: 'ok', path }
  }
  if (!auth.token) return { result: 'redirect', to: '/login' }
  if (route.admin && auth.role !== 'admin') return { result: 'redirect', to: '/memos' }
  return { result: 'ok', path }
}
```

#### 测试组与预期

| 场景 | 设置 | 调用 | 预期 |
|------|------|------|------|
| A1 未登录访问业务页 | `token=''` | `navigate('/memos')` | `redirect` → `/login` |
| A2 未登录访问登录页 | `token=''` | `navigate('/login')` | `ok` |
| B1 普通用户访问备忘录 | `token='x'`, `role='user'` | `navigate('/memos')` | `ok` |
| B2 普通用户访问管理页 | 同上 | `navigate('/users')` | `redirect` → `/memos` |
| B3 已登录还去登录页 | 同上 | `navigate('/login')` | `redirect` → `/memos` |
| C1 管理员访问管理页 | `role='admin'` | `navigate('/users')` | `ok` |

对照项目：`web/src/router/index.js` 的 `beforeEach` 与上述逻辑结构一致。

---

### 练习 3：真正用 Vue Router 换页（浏览器）

#### 要练会什么

体验 Router 真实用法：**点链接改地址，`<router-view>` 自动换组件**。

#### 可执行代码

```
demo/前端/路由守卫_demo/lesson3-router-basic.html
```

#### 运行方式

```powershell
start demo\前端\路由守卫_demo\lesson3-router-basic.html
```

或直接双击 HTML 文件。

- 需要能访问 CDN（`unpkg.com`）
- 使用 hash 路由（`#/memos`），**无需** 本地服务器

#### 手动测试清单

| 操作 | 预期 |
|------|------|
| 打开文件 | 地址栏含 `#/memos`，显示 `[备忘录] 这是备忘录页` |
| 点击「密码本」 | 地址变为 `#/passwords`，显示密码本页 |
| 浏览器后退 | 回到备忘录页 |
| 手动改地址为 `#/passwords` | 直接显示密码本页 |

对照项目：`web/src/App.vue` 的 `<router-view />`。

---

### 练习 4：给路由加 meta 和 beforeEach 守卫

#### 要练会什么

把练习 2 的 JS 逻辑放进**真正的 Vue Router 守卫**；理解 `meta.public`、`meta.admin`。

#### 可执行代码

```
demo/前端/路由守卫_demo/lesson4-router-guard.html
```

#### 运行方式

```powershell
start demo\前端\路由守卫_demo\lesson4-router-guard.html
```

#### 手动测试清单

| 步骤 | 操作 | 预期 |
|------|------|------|
| 1 | 未登录，点「备忘录」 | 被赶到 `#/login` |
| 2 | 点「切换登录」，再点「备忘录」 | 显示备忘录页 |
| 3 | 角色 user，点「用户管理」 | 被赶回 `#/memos` |
| 4 | 切换为 admin，点「用户管理」 | 显示用户管理页 |
| 5 | 已登录时打开 `#/login` | 自动跳到 `#/memos` |

页面底部「守卫日志」示例：

```
从 / 到 /memos -> 未登录，重定向到 /login
```

对照项目：`web/src/router/index.js` 全文。

---

### 练习 5：迷你综合题（最接近真实项目）

#### 要练会什么

串联完整流程：**登录 → 存 token → 守卫放行 → 侧边栏导航 → 管理员才能进用户管理 → 登出回登录**。

#### 怎么做

参考下方骨架，新建 `mini-wizzy.html` 在浏览器打开（或自行扩展 `lesson4` 加入登录表单和 localStorage）。

#### 测试账号（可自行定义）

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | 123 | admin |
| user | 123 | user |

#### 测试清单

| 步骤 | 操作 | 预期 |
|------|------|------|
| 1 | 打开页面 | 未登录 → `#/login` |
| 2 | user / 123 登录 | 进入 `#/memos`，侧边栏**无**用户管理 |
| 3 | 手动改地址 `#/users` | 被拦回 `#/memos` |
| 4 | 退出，admin / 123 登录 | 侧边栏**有**用户管理，能进 `#/users` |
| 5 | 刷新页面 | 仍保持登录（localStorage） |
| 6 | 已登录访问 `#/login` | 自动回首页 |
| 7 | 退出 | 回登录页，再访问 `#/memos` 被拦 |

#### 与主项目对应

| 迷你题 | 主项目 |
|--------|--------|
| 登录页 + `router.push` | `web/src/views/LoginView.vue` |
| `beforeEach` 守卫 | `web/src/router/index.js` |
| `isLoggedIn` / `isAdmin` | `web/src/stores/auth.js` |
| MainLayout + 嵌套 children | `web/src/layouts/MainLayout.vue` |
| 侧边栏 `v-if="isAdmin"` | `MainLayout.vue` 用户管理菜单 |

#### 骨架要点

```javascript
// 嵌套路由结构（与主项目一致）
{
  path: '/login', component: LoginView, meta: { public: true },
},
{
  path: '/',
  component: MainLayout,
  redirect: '/memos',
  children: [
    { path: 'memos', component: Memos },
    { path: 'users', component: Users, meta: { admin: true } },
  ],
}
```

---

## 练完后对照项目文件

### 练习与文件对照

| 练完题号 | 打开的文件 | 对照什么 |
|----------|------------|----------|
| 练习 1 | `web/src/router/index.js` | `routes` 数组就是「门牌表」 |
| 练习 2 | `web/src/router/index.js` 第 54~77 行 | `beforeEach` 三段 if 逻辑 |
| 练习 3 | `web/src/App.vue` | 根级 `<router-view />` |
| 练习 3 | `web/src/main.js` | `app.use(router)` |
| 练习 4 | `web/src/router/index.js` | `meta.public`、`meta.admin` |
| 练习 4 | `web/src/stores/auth.js` | `isLoggedIn`、`isAdmin` getters |
| 练习 5 | `web/src/views/LoginView.vue` | 登录后 `router.push('/')` |
| 练习 5 | `web/src/layouts/MainLayout.vue` | 嵌套路由 + 侧边栏 `router` 菜单 |
| 练习 5 | `web/src/utils/request.js` | 401 时 `router.push('/login')` |

### demo 与主项目对照

| demo（路由守卫_demo） | 主项目 |
|-----------------------|--------|
| `lesson1-route-map.js` 的 `routes` 对象 | `router/index.js` 的 `routes` 数组 |
| `lesson4` 的 `beforeEach` | `router/index.js` 的 `beforeEach` |
| `loggedIn` / `role` ref | `stores/auth.js` 的 `token` / `userInfo.role` |
| `lesson3` 的 `<router-view>` | `App.vue`、`MainLayout.vue` |
| hash 模式 `#/memos` | 主项目用 `createWebHistory()`（地址无 `#`） |

### 建议阅读顺序

`main.js` → `App.vue` → `router/index.js` → `stores/auth.js` → `LoginView.vue` → `MainLayout.vue` → `utils/request.js`

### 自检清单

- [ ] 能说出 Vue Router = 地址决定显示哪一页
- [ ] 能说出路由守卫 = 换页前的统一检查（登录、权限）
- [ ] 能说出 `routes`、`router-view`、`beforeEach`、`meta` 各干什么
- [ ] 能说出守卫为什么读 `authStore`，而不是每个页面各自判断
- [ ] 跑通 `demo/前端/路由守卫_demo/lesson1-route-map.js`，终端显示 5 通过 0 失败
- [ ] 在浏览器跑通 `lesson3`、`lesson4`，手动测试清单全部符合预期

---

## 总结

**Vue Router** 在本项目里是「地址 ↔ 页面」的调度员：点侧边栏或改地址栏，就显示登录、备忘录、密码本等对应页面。**路由守卫**是跳转前的保安：没登录不能进业务页，非管理员不能进用户管理，已登录不用再看到登录页。不用它们，要用大量 `v-if` 管页面切换和权限，容易漏、难维护；用了之后规则集中在 `router/index.js` 一处，全站行为一致、更安全，也支持刷新、收藏链接。动手练完 `demo/前端/路由守卫_demo` 后，按 `router/index.js` → `stores/auth.js` → `LoginView.vue` → `MainLayout.vue` 顺序对照主项目即可。
