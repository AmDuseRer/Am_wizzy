# Pinia 状态管理与持久化学习笔记

> 结合本项目（wizzy 小智工具箱）的通俗讲解，面向零基础。  
> 动手练习脚本（练习 1~3）：`demo/前端/Pinia_demo/`

---

## 目录

1. [一句话理解](#一句话理解)
2. [Pinia 是什么](#pinia-是什么)
3. [持久化是什么](#持久化是什么)
4. [在本项目中的作用](#在本项目中的作用)
5. [不用 vs 用了](#不用-vs-用了)
6. [实质好处（带对比）](#实质好处带对比)
7. [代码写在哪（三层位置）](#代码写在哪三层位置)
8. [defineStore 基础骨架](#definestore-基础骨架)
9. [在本项目里具体怎么用](#在本项目里具体怎么用)
10. [登录完整数据流](#登录完整数据流)
11. [动手练习（5 道题）](#动手练习5-道题)
12. [练完后对照项目文件](#练完后对照项目文件)
13. [总结](#总结)

---

## 一句话理解

**Pinia 是整个前端共用的「记事本」，存登录信息、界面设置等全站都要用的数据；持久化是把记事本自动抄一份到浏览器本地，刷新后还能恢复。页面、路由、发请求都从同一本记事本读，改一处处处同步。**

---

## Pinia 是什么

Vue 页面由很多**组件**组成：登录页、侧边栏、备忘录列表、顶栏……

这些组件经常需要知道**同一件事**，例如：

- 用户登录了吗？
- 当前用户名是什么？
- 是不是管理员？
- 暗色模式开没开？

如果每个组件各自存一份，就会**对不上、漏改、刷新丢失**。

**Pinia** 就是 Vue 官方推荐的全局状态管理库：  
把这类「全站共用数据」集中放在**仓库（Store）**里，谁需要就去读、去改，**全项目共用一本记事本**。

本项目有两个仓库：

| 仓库文件 | 记什么 | localStorage 键名 |
|----------|--------|-------------------|
| `web/src/stores/auth.js` | 登录 token、用户信息 | `wizzy-auth` |
| `web/src/stores/app.js` | 暗色模式、侧边栏折叠 | `wizzy-app` |

---

## 持久化是什么

浏览器里的 JavaScript **变量存在内存里**，按 F5 刷新或关 tab，内存清空，数据就没了。

**持久化（persist）** = 把仓库里指定的字段**自动存进浏览器的 localStorage**，下次打开再**自动读回来**。

可以想成：

- **Pinia 仓库** = 正在用的记事本（内存）
- **localStorage** = 抽屉里备份的复印件（硬盘）
- **persist 插件** = 有人帮你自动「写备份、读备份」

本项目在 `main.js` 里安装了持久化插件：

```javascript
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
app.use(pinia)
```

每个仓库里用 `persist` 指定存哪些字段，例如 `auth.js`：

```javascript
persist: {
  key: 'wizzy-auth',
  paths: ['token', 'userInfo'],
},
```

---

## 在本项目中的作用

小智工具箱是**需要登录**的个人工具（备忘录、密码本、待办等）。Pinia 在这里干三件事：

### 1. 当「登录信息的总仓库」

登录成功后，token 和用户信息写入 `auth` 仓库（`stores/auth.js` 的 `login` action）。

### 2. 让全站不同地方都能读到同一份数据

| 使用者 | 文件 | 读什么 |
|--------|------|--------|
| 发 API 请求 | `web/src/utils/request.js` | `authStore.token`，自动加 `Authorization` |
| 路由守卫 | `web/src/router/index.js` | `authStore.isLoggedIn`、`authStore.isAdmin` |
| 侧边栏 | `web/src/layouts/MainLayout.vue` | `authStore.isAdmin` 决定是否显示用户管理 |
| 登录页 | `web/src/views/LoginView.vue` | 调用 `authStore.login()` |
| 界面设置 | `web/src/layouts/MainLayout.vue` | `appStore.darkMode`、`appStore.toggleSidebar()` |

### 3. 刷新页面后仍然记得你

配置了 `persist` 后，F5 刷新不用重新登录；暗色模式、侧边栏折叠也会保留。

**不可或缺在哪？** 没有 Pinia，登录态要在十几个文件里各自维护或传来传去；没有 persist，每次刷新都要重新登录。

---

## 不用 vs 用了

### 场景 A：从「备忘录」切到「密码本」

| 不用 Pinia | 用了 Pinia |
|------------|------------|
| 每个页面各自存登录信息，或 props 传来传去，容易不一致 | 所有页面读同一个 `authStore`，永远知道当前是谁 |

### 场景 B：用户按 F5 刷新

| 不用（且没自己做持久化） | 用了 Pinia + persist |
|--------------------------|----------------------|
| 内存清空，登录丢失，被踢回登录页 | 从 localStorage 恢复 token，仍保持登录 |

### 场景 C：发 API 请求

| 不用 Pinia | 用了 Pinia |
|------------|------------|
| 每个请求自己找 token，重复、易漏 | `request.js` 统一从 `authStore.token` 取 |

### 场景 D：普通用户访问「用户管理」

| 不用 Pinia | 用了 Pinia |
|------------|------------|
| 每个要鉴权的地方各自判断 | 路由守卫读 `authStore.isAdmin`，一处拦截全站生效 |

### 场景 E：切换暗色模式

| 不用 Pinia + persist | 用了 |
|----------------------|------|
| 刷新后恢复默认亮色 | `appStore` 记住设置，下次打开仍是暗色 |

---

## 实质好处（带对比）

### 好处一：一处改，处处同步

| 不用 | 用了 |
|------|------|
| 登录页存了 token，请求模块不知道；A 页登出 B 页还以为登录着 | `authStore.logout()` 清空一次，路由、请求、界面一起更新 |

### 好处二：刷新不丢登录态

| 不用 | 用了 |
|------|------|
| 每次刷新重新输入账号密码 | `token` 自动存 localStorage，刷新后 `isLoggedIn` 仍为 true |

### 好处三：代码集中、好维护

| 不用 | 用了 |
|------|------|
| 登录、鉴权、带 token 逻辑散落多处 | 集中在 `stores/auth.js`，别处只读、只调 |

### 好处四：界面偏好有记忆

| 不用 | 用了 |
|------|------|
| 每次打开默认亮色、侧边栏展开 | `app` 仓库持久化 `darkMode`、`sidebarCollapsed` |

### 好处五：和 Vue 配合自然

| 不用 | 用了 |
|------|------|
| 全局变量或事件总线，难调试 | 组件里 `useAuthStore()`，改数据界面自动更新 |

---

## 代码写在哪（三层位置）

Pinia **不是**全部写在 `<script setup>` 里，分三层：

| 做什么 | 写在哪 | 例子 |
|--------|--------|------|
| **安装** Pinia | `web/src/main.js` | `createPinia()`、`app.use(pinia)`、持久化插件 |
| **定义**仓库 | `web/src/stores/*.js` | `defineStore('auth', { ... })` |
| **使用**仓库 | 各 `.vue` 的 `<script setup>` 或 `.js` | `const authStore = useAuthStore()` |

`main.js` 里也可以直接用仓库（启动时恢复暗色模式）：

```javascript
const appStore = useAppStore()
if (appStore.darkMode) {
  document.documentElement.classList.add('dark')
}
```

---

## defineStore 基础骨架

### 最小骨架（只有 state 必填）

```javascript
import { defineStore } from 'pinia'

export const useXxxStore = defineStore('仓库id', {
  state: () => ({}),
})
```

### 完整骨架（本项目常见写法）

```javascript
import { defineStore } from 'pinia'

export const useXxxStore = defineStore('仓库id', {
  // ① 数据（必填）
  state: () => ({
    // 字段名: 初始值
  }),

  // ② 计算属性（可选）
  getters: {
    // 名字: (state) => 计算结果
  },

  // ③ 方法（可选）
  actions: {
    // 方法名() { this.xxx = ... }
  },

  // ④ 持久化（可选，需 main.js 已装插件）
  persist: {
    key: 'localStorage里的键名',
    paths: ['要存的字段'],
  },
})
```

### 四块分别干什么

| 部分 | 作用 | 本项目例子 |
|------|------|------------|
| **第一个参数 `'auth'`** | 仓库唯一 id | 不要和 `app` 等重复 |
| **导出名 `useAuthStore`** | 组件里调用的名字 | `use` + 名 + `Store` |
| **state** | 存数据，必须是 `() => ({})` 函数 | `token`、`userInfo` |
| **getters** | 由 state 算出的只读结果 | `isLoggedIn`、`isAdmin` |
| **actions** | 改 state，用 `this.xxx` | `login()`、`logout()` |
| **persist** | 指定存 localStorage 的字段 | `paths: ['token', 'userInfo']` |

### 三个易错点

1. **state 必须是函数**，不能写成 `state: { count: 0 }`
2. **actions 里改数据用 `this`**，不是 `state`
3. **getters 里用 `(state) =>`**，不用 `this`

### 本项目两个真实例子

**完整版** — `web/src/stores/auth.js`（state + getters + actions + persist 四块都有）

**简单版** — `web/src/stores/app.js`（没有 getters，只有 state + actions + persist）

---

## 在本项目里具体怎么用

### 第 1 步：在 main.js 安装（只做一次）

```javascript
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
app.use(pinia)
```

### 第 2 步：在 stores/*.js 定义仓库

见 `stores/auth.js`、`stores/app.js`。

### 第 3 步：在组件或 JS 里使用

**引入并创建实例：**

```javascript
import { useAuthStore } from '@/stores/auth'
const authStore = useAuthStore()
```

**模板里读数据：**

```html
<p>你好，{{ authStore.username }}</p>
<p v-if="authStore.isAdmin">管理员菜单</p>
```

**脚本里调方法（LoginView.vue）：**

```javascript
await authStore.login(form)
router.push('/')
```

**普通 JS 里也能用（request.js）：**

```javascript
const authStore = useAuthStore()
if (authStore.token) {
  config.headers.Authorization = `Bearer ${authStore.token}`
}
```

### 常用写法速查

```javascript
authStore.token              // 读数据
authStore.isLoggedIn         // 读 getter
await authStore.login(form)  // 调 action
await authStore.logout()
```

改数据尽量走 **actions**，不要 scattered 在各处直接 `authStore.token = ...`。

---

## 登录完整数据流

```
用户点登录
    ↓
LoginView.vue 调用 authStore.login(form)
    ↓
auth.js 的 action 调后端 API，写入 token、userInfo
    ↓
persist 插件自动存到 localStorage（key: wizzy-auth）
    ↓
router 守卫看到 isLoggedIn === true，放行
    ↓
request.js 每次请求自动带 Authorization: Bearer xxx
    ↓
用户按 F5 刷新
    ↓
persist 从 localStorage 恢复，仍然登录
```

---

## 动手练习（5 道题）

由浅入深。练习 1~3 已有可执行脚本；练习 4~5 为单文件 HTML（需浏览器）。

---

### 练习 1：理解「全站共用一本记事本」

#### 要练会什么

多个模块读**同一份**数据，改一处处处同步。

#### 可执行代码

```
demo/前端/Pinia_demo/run-tests.js  →  exercise1()
```

#### 运行方式（Windows）

```powershell
cd demo\前端\Pinia_demo
node run-tests.js
```

无需 `npm install`，零依赖。

#### 预期结果

| 断言 | 预期 |
|------|------|
| 1.1 登录后三处都能读到 token | `token=fake-token-abc` |
| 1.2 侧边栏识别为管理员 | `isAdmin=true` |
| 1.3 清空 token 后 | 请求模块读到空字符串 |

终端应出现 `[OK] 1.1` … `[OK] 1.3`。

#### 核心逻辑（摘要）

```javascript
const authBox = { token: '', userInfo: null }

function loginPageLogin() {
  authBox.token = 'fake-token-abc'
  authBox.userInfo = { username: 'admin', role: 'admin' }
}

function requestModuleGetToken() {
  return authBox.token
}

function sidebarCheckAdmin() {
  return authBox.userInfo?.role === 'admin'
}
```

---

### 练习 2：理解「持久化 = 刷新后还能恢复」

#### 要练会什么

内存会丢，localStorage 里的可以恢复；删掉 localStorage 等于无法恢复登录。

#### 可执行代码

```
demo/前端/Pinia_demo/run-tests.js  →  exercise2()
```

运行方式同练习 1。

#### 预期结果

| 断言 | 预期 |
|------|------|
| 2.1 恢复后 token | `persist-token-123` |
| 2.2 恢复后用户名 | `user` |
| 2.3 删除 localStorage 后 | `getItem` 返回 `null` |

#### 核心逻辑（摘要）

```javascript
localStorage.setItem('wizzy-auth-practice', JSON.stringify(data))
let memory = null                    // 模拟刷新清空内存
memory = JSON.parse(localStorage.getItem('wizzy-auth-practice'))
localStorage.removeItem('wizzy-auth-practice')  // 模拟登出/清缓存
```

---

### 练习 3：手写迷你 defineStore

#### 要练会什么

对应 `stores/auth.js` 的 **state / getters / actions** 三块结构。

#### 可执行代码

```
demo/前端/Pinia_demo/run-tests.js  →  exercise3() + createMiniStore()
```

运行方式同练习 1。全部练完应显示：**12 通过，0 失败**。

#### 预期结果

| 步骤 | 预期 |
|------|------|
| 初始 | `isLoggedIn=false` |
| admin 登录 | `isLoggedIn=true`，`isAdmin=true` |
| 登出 | `isLoggedIn=false` |
| user 登录 | `isLoggedIn=true`，`isAdmin=false` |

#### 核心逻辑（摘要）

```javascript
function createMiniStore(initialState, getters, actions) {
  const state = { ...initialState }
  return {
    ...Object.fromEntries(
      Object.entries(getters).map(([name, fn]) => [name, () => fn(state)])
    ),
    ...Object.fromEntries(
      Object.entries(actions).map(([name, fn]) => [name, (...args) => fn(state, ...args)])
    ),
  }
}
```

---

### 练习 4：单文件 HTML + 真 Pinia + 持久化

#### 要练会什么

在真实 Pinia 里写 state / getters / actions / persist，页面按钮操作，**F5 后仍保持登录**。

#### 怎么做

1. 新建 `pinia-practice.html`（内容见下方或自行按骨架扩展）
2. 浏览器打开，点「admin 登录 / user 登录 / 登出」
3. 登录后 F5，应仍保持登录
4. DevTools → Application → Local Storage 查看 `pinia-practice-auth`

#### 测试清单

| 操作 | 预期 |
|------|------|
| 点「以 admin 登录」 | 已登录，是管理员 |
| 点「以 user 登录」 | 已登录，**不是**管理员 |
| 点「登出」 | 回到未登录 |
| 登录后 F5 | 仍保持登录（persist 生效） |
| 登出后 F5 | 仍是未登录 |

#### HTML 骨架要点

```javascript
const useAuthStore = defineStore('auth-practice', {
  state: () => ({ token: '', userInfo: null }),
  getters: { isLoggedIn: (s) => !!s.token, isAdmin: (s) => s.userInfo?.role === 'admin' },
  actions: { login(user) { ... }, logout() { ... } },
  persist: { key: 'pinia-practice-auth', paths: ['token', 'userInfo'] },
})

const pinia = createPinia()
pinia.use(PiniaPersistedstate)
```

CDN：`vue@3`、`pinia@2`、`pinia-plugin-persistedstate@3`（unpkg）。

---

### 练习 5：迷你综合题（最接近真实项目）

#### 要练会什么

一个 auth 仓库同时服务 **页面、路由判断、发请求** 三处。

#### 场景

单文件 HTML：`navigate()` 模拟路由守卫，`fetchData()` 模拟 request 拦截器带 token。

#### 测试清单

| 步骤 | 操作 | 预期 |
|------|------|------|
| 1 | user 登录 | 进入 memos |
| 2 | user 点「去用户管理」 | **被拦截**，日志含「非管理员」，留在 memos |
| 3 | admin 登录再点「去用户管理」 | **成功**进入 users |
| 4 | 点「模拟发请求」 | 日志含 `Authorization: Bearer jwt-admin` |
| 5 | admin 登录后 F5 | 仍 logged in，能再去 users |
| 6 | 登出后 F5 | 回 login |

#### 与主项目对应

| 迷你题 | 主项目 |
|--------|--------|
| `navigate()` | `web/src/router/index.js` 的 `beforeEach` |
| `fetchData()` | `web/src/utils/request.js` 请求拦截器 |
| `useAuthStore` | `web/src/stores/auth.js` |

---

## 练完后对照项目文件

### 练习与文件对照

| 练完题号 | 打开的文件 | 对照什么 |
|----------|------------|----------|
| 练习 1 | `web/src/stores/auth.js` | `state` 就是共用数据 |
| 练习 2 | `web/src/stores/auth.js` 底部 `persist` | `key: 'wizzy-auth'` |
| 练习 2 | `web/src/main.js` 第 19 行 | `pinia.use(piniaPluginPersistedstate)` |
| 练习 3 | `web/src/stores/auth.js` 全文 | getters、actions |
| 练习 4 | `web/src/views/LoginView.vue` | `<script setup>` 里 `useAuthStore()` |
| 练习 4 | `web/src/stores/app.js` | 第二个仓库 + persist |
| 练习 5 | `web/src/router/index.js` | `beforeEach` + `isLoggedIn` / `isAdmin` |
| 练习 5 | `web/src/utils/request.js` | 读 `authStore.token` |
| 练习 5 | `web/src/layouts/MainLayout.vue` | 模板里 `authStore`、`appStore` |

### demo 与主项目对照

| demo（Pinia_demo） | 主项目 |
|--------------------|--------|
| `authBox` 共用对象 | `stores/auth.js` 的 Pinia 仓库 |
| `localStorage.setItem('wizzy-auth-practice')` | `persist: { key: 'wizzy-auth' }` |
| `createMiniStore` | `defineStore('auth', { state, getters, actions })` |
| `requestModuleGetToken()` | `utils/request.js` |
| `sidebarCheckAdmin()` | `layouts/MainLayout.vue` 的 `authStore.isAdmin` |

### 建议阅读顺序

`main.js` → `stores/auth.js` → `LoginView.vue` → `router/index.js` → `utils/request.js` → `MainLayout.vue` → `stores/app.js`

### 自检清单

- [ ] 能说出 Pinia = 全站共用一本记事本
- [ ] 能说出 persist = 自动抄一份到 localStorage，刷新再抄回来
- [ ] 能说出 state 存数据、getters 算结果、actions 改数据
- [ ] 能区分：安装在 main.js、定义在 stores/*.js、使用在 script setup
- [ ] 跑通 `demo/前端/Pinia_demo`，终端显示 12 通过 0 失败

---

## 总结

**Pinia** 是 Vue 全站共用的状态仓库，本项目用 `auth` 存登录信息、用 `app` 存界面设置。**持久化**通过 `pinia-plugin-persistedstate` 把指定字段自动写入 localStorage，刷新不丢登录、不丢暗色模式。用法三步：`main.js` 安装 → `defineStore` 定义仓库 → 组件或 JS 里 `useXxxStore()` 读写。不用 Pinia，登录态要在多处重复维护且刷新易丢；用了之后路由、请求、页面读同一份数据，逻辑集中在 `stores/`，好维护。动手练完 `demo/前端/Pinia_demo` 后，按 `stores/auth.js` → `main.js` → `LoginView.vue` → `router/index.js` → `request.js` 顺序对照主项目即可。
