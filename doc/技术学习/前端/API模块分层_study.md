# API 模块分层学习笔记

> 结合本项目（wizzy 小智工具箱）的通俗讲解，面向零基础。  
> 与 Axios 封装配合阅读：[Axios_study.md](./Axios_study.md)（讲 `request.js` 怎么工作）  
> 本文重点讲：`web/src/api/` 这一层「按功能拆文件、用函数名封装接口」。

---

## 目录

1. [一句话理解](#一句话理解)
2. [API 模块分层是什么](#api-模块分层是什么)
3. [打个比方](#打个比方)
4. [在前端长什么样（目录结构）](#在前端长什么样目录结构)
5. [三层各自干什么](#三层各自干什么)
6. [在本项目中的作用](#在本项目中的作用)
7. [不用 vs 用了](#不用-vs-用了)
8. [实质好处（带对比）](#实质好处带对比)
9. [整条调用链（前端视角）](#整条调用链前端视角)
10. [前后端文件一一对应](#前后端文件一一对应)
11. [谁在调用 api 文件](#谁在调用-api-文件)
12. [写 api 文件的规律](#写-api-文件的规律)
13. [标准写法与反例](#标准写法与反例)
14. [动手练习（3 道题）](#动手练习3-道题)
15. [练完后对照项目文件](#练完后对照项目文件)
16. [总结](#总结)

---

## 一句话理解

**API 模块分层 = 把「怎么跟后端说话」从页面里抽出来，按功能放进 `web/src/api/` 每个文件里，用 `listMemos()` 这种好懂的名字代替裸网址。页面只管界面和业务逻辑，接口细节集中管理。**

---

## API 模块分层是什么

页面要显示数据，必须向服务器发 HTTP 请求。如果每个 `.vue` 页面都自己写：

- 访问哪个网址（`/api/memos?page=1`）
- 用什么方法（GET / POST / PUT / DELETE）
- 传什么参数

代码会又乱又难改。

**API 模块分层**的做法是：专门建一个 `api/` 文件夹，**一个业务功能对应一个文件**，文件里导出若干函数，函数名表达「我要干什么」，函数内部才去调 `request.get/post/...`。

| 概念 | 在本项目里 |
|------|-----------|
| 分层 | 页面 → `api/*.js` → `request.js` → 后端，各干各的 |
| 模块 | 备忘录、待办、登录等，每个功能一个文件 |
| 封装 | 把 `/memos`、`/auth/login` 等路径藏进 `listMemos()`、`login()` 里 |

---

## 打个比方

想象你在点外卖：

| 角色 | 对应什么 | 项目里的文件 |
|------|----------|-------------|
| 你（食客） | 只关心「我要看备忘录」 | `MemoListView.vue` 等页面 |
| 菜单 | 写着 `listMemos()`（查列表）、`createMemo()`（新建） | `api/memos.js` |
| 配送员 | 统一带登录凭证、处理报错、拼地址前缀 | `utils/request.js` |
| 厨房 | 真正存数据、查数据 | `server/app/api/memos.py` 等 |

**API 模块分层**做的，就是中间这层「菜单」：每个功能一个文件，用中文能看懂的名字封装接口。

---

## 在前端长什么样（目录结构）

```
web/src/
├── utils/
│   └── request.js          ← 第 1 层：公共「配送员」（详见 Axios_study.md）
├── api/                    ← 第 2 层：API 模块分层（本文重点）
│   ├── auth.js             ← 登录 / 登出 / 改密码
│   ├── memos.js            ← 备忘录
│   ├── todos.js            ← 待办
│   ├── passwords.js        ← 密码本
│   ├── categories.js       ← 分类
│   ├── users.js            ← 用户管理（管理员）
│   └── logs.js             ← 操作日志
├── views/                  ← 第 3 层：页面（只管界面 + 调 api 函数）
│   ├── MemoListView.vue
│   ├── TodoListView.vue
│   └── ...
├── components/             ← 组件也会直接调 api
│   ├── CategorySelect.vue
│   └── ViewPasswordDialog.vue
└── stores/
    └── auth.js             ← Store 也会调 api（如 login）
```

**在前端最直观的表现**：打开任意页面，看顶部的 `import ... from '@/api/xxx'`，那就是分层。

---

## 三层各自干什么

### 第 1 层：`request.js`（一般只写一次）

全站共用的发请求工具，负责：

- `baseURL: '/api'` → 只写 `/memos`，自动变成 `/api/memos`
- 请求拦截器 → 自动带登录 token
- 响应拦截器 → 统一判 `code === 0`、弹错误、401 跳登录页

详见 [Axios_study.md](./Axios_study.md)，本文不展开。

### 第 2 层：`api/*.js`（按功能写接口）—— 分层核心

每个文件只做一件事：**把这个功能要调的后端接口，包装成语义化的函数名。**

以备忘录为例（`web/src/api/memos.js`）：

```javascript
import request from '@/utils/request'

export function listMemos(params) {
  return request.get('/memos', { params })
}

export function getMemo(id) {
  return request.get(`/memos/${id}`)
}

export function createMemo(data) {
  return request.post('/memos', data)
}

export function updateMemo(id, data) {
  return request.put(`/memos/${id}`, data)
}

export function deleteMemo(id) {
  return request.delete(`/memos/${id}`)
}

export function exportMemoTxt(id) {
  return request.get(`/memos/${id}/export-txt`, { responseType: 'blob' })
}
```

**规律：**

- 文件名 = 功能名（`memos.js`、`auth.js`）
- 函数名 = 动作 + 对象（`listMemos`、`createTodo`、`login`）
- 函数内部 = 一行 `request.get/post/put/delete(...)`

Axios 在本项目 api 层最常用的 4 种写法：

| 方法 | 干什么 | 项目例子 |
|------|--------|----------|
| `request.get(路径, { params })` | **查**数据 | `listMemos({ page, page_size })` |
| `request.post(路径, 数据)` | **新增** / 提交 | `login(data)`、`createMemo(data)` |
| `request.put(路径, 数据)` | **修改** | `updateMemo(id, data)` |
| `request.delete(路径)` | **删除** | `deleteMemo(id)` |

补充：

- `{ params }` → 变成 URL 后面的 `?page=1&page_size=10`
- 第二个参数 `data` → POST/PUT 的请求体（JSON）
- `responseType: 'blob'` → 下载文件，不按 JSON 解析

### 第 3 层：页面 / 组件 / Store — 只「点菜」，不「进厨房」

页面从 `api/` 里 import 函数，像调普通 JS 函数一样用：

```javascript
// web/src/views/MemoListView.vue
import { listMemos, createMemo, updateMemo, deleteMemo } from '@/api/memos'
import { listCategories } from '@/api/categories'

async function loadData() {
  loading.value = true
  try {
    const res = await listMemos({
      page: page.value,
      page_size: pageSize.value,
      keyword: keyword.value || undefined,
    })
    memos.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}
```

页面里**看不到** `/api/memos`、`axios`、`Authorization` 这些细节。

Store 里也一样（`web/src/stores/auth.js`）：

```javascript
import { login as loginApi, logout as logoutApi, getMe } from '@/api/auth'

async login(credentials) {
  const res = await loginApi(credentials)
  this.token = res.data.access_token
  this.userInfo = res.data.user
}
```

---

## 在本项目中的作用

项目有备忘录、待办、密码本、登录等很多功能，对应 7 个 `api/*.js` 文件、几十个页面和组件。如果每个页面都自己写「访问哪个网址、用什么方法」，很快就会乱掉。

分层之后，规则很简单：

| 谁 | 干什么 | 项目里的文件 |
|----|--------|-------------|
| 页面 / 组件 / Store | 只调用 `listMemos()` 这类函数 | `MemoListView.vue`、`CategorySelect.vue`、`stores/auth.js` |
| API 模块 | 只写「这个功能要调哪些接口」 | `api/memos.js`、`api/auth.js` 等 7 个 |
| 请求封装 | 只写一次公共规矩（地址前缀、登录、报错） | `utils/request.js` |

**不可或缺在哪？** 所有功能都靠同一套规则和后端说话。没有这层「菜单」，每个页面都要自己记网址、自己拼参数，改一处就要改很多地方，极易漏改、行为不一致。

---

## 不用 vs 用了

### 整体感受

| | 不用 API 模块分层 | 用了（本项目） |
|---|---|---|
| 页面里写什么 | 到处散落 `axios.get('/api/memos', ...)` | 只写 `await listMemos({ page: 1 })` |
| 找接口在哪 | 要在很多 `.vue` 文件里搜 | 直接去 `api/memos.js` |
| 和后端对应关系 | 靠人脑记「这个页面对应哪个接口」 | 前端 `api/memos.js` ↔ 后端 `app/api/memos.py` |
| 改接口地址 | 可能改 10 个页面 | 只改 `api/memos.js` 一处 |

### 具体场景：备忘录列表页加载数据

**不用：**

```javascript
// 写在 MemoListView.vue 里，页面又要管界面，又要管网址
const res = await axios.get('/api/memos', {
  params: { page: 1, page_size: 10 },
  headers: { Authorization: 'Bearer ' + token }  // 还要自己带登录凭证
})
if (res.data.code !== 0) { /* 自己处理错误 */ }
memos.value = res.data.data.items
```

**用了（本项目）：**

```javascript
// 页面里
const res = await listMemos({ page: 1, page_size: 10 })
memos.value = res.data.items   // token、报错已在 request.js 里统一处理好
```

```javascript
// api/memos.js 里
export function listMemos(params) {
  return request.get('/memos', { params })
}
```

**本质区别：**

- **不用** = 每个页面都是「自己跑厨房」的食客，重复记路线、重复处理意外
- **用了** = 页面只点菜（调函数），「菜单 + 配送」交给专门的人做

---

## 实质好处（带对比）

### 好处一：页面代码更好读，只管「做什么」

| 不用 | 用了 |
|------|------|
| 页面里混着 `get('/api/memos')`、`post('/api/auth/login')`，界面逻辑和网络请求缠在一起 | 页面写 `listMemos()`、`login()`，一眼知道在干什么 |
| 新人看页面要先搞懂 HTTP、URL 拼法 | 看函数名就懂：`createMemo` = 新建备忘录 |

### 好处二：改后端地址时，只动一个文件

| 不用 | 用了 |
|------|------|
| 后端把 `/memos` 改成 `/notes`，要在每个用过的页面里搜 `/memos` 逐个改 | 只改 `api/memos.js` 里那几行，所有页面自动跟着变 |
| 容易漏改某个页面，上线后某个功能突然 404 | 接口定义集中在一处，不容易漏 |

### 好处三：前后端结构对齐，找东西不迷路

| 不用 | 用了 |
|------|------|
| 前端接口散落在各页面，后端在 `server/app/api/`，两边对不上号 | 前端 `api/memos.js` 对应后端 `memos.py`，功能名一致 |
| 「这个接口到底谁在调？」要全局搜索 | 看文件名就知道：备忘录相关 → 打开 `api/memos.js` |

### 好处四：和 `request.js` 配合，公共逻辑只写一次

API 模块本身不管「带 token、弹错误、登录过期跳页」，这些都由 `request.js` 统一做。API 文件只负责「调哪个路径」：

```javascript
// api/auth.js
export function login(data) {
  return request.post('/auth/login', data)
}
```

| 不用 | 用了 |
|------|------|
| 7 个功能 × 多个页面，每个请求都要重复写 token、错误处理 | `request.js` 写一次；7 个 `api/*.js` 只管业务路径；页面只管调函数 |
| 有的页面忘了带 token → 401；有的忘了处理 401 → 卡在空白页 | 全站行为一致：失败弹窗，登录过期自动跳 `/login` |

---

## 整条调用链（前端视角）

以打开备忘录列表为例：

```
MemoListView.vue
    ↓  import { listMemos } from '@/api/memos'
    ↓  await listMemos({ page: 1, page_size: 10 })
api/memos.js
    ↓  request.get('/memos', { params })
utils/request.js
    ↓  【请求拦截器】自动加 Authorization: Bearer token
    ↓  拼上 baseURL '/api'
    ↓  实际请求：GET /api/memos?page=1&page_size=10
Vite 开发代理
    ↓  转发到后端
server/app/api/memos.py
    ↓  查数据库，返回 { code: 0, data: { items: [...], total: N } }
utils/request.js
    ↓  【响应拦截器】判断 code === 0，失败就弹窗
MemoListView.vue
    ↓  res.data.items 填进表格
```

---

## 前后端文件一一对应

| 前端 `web/src/api/` | 后端 `server/app/api/` | 功能 |
|---------------------|------------------------|------|
| `auth.js` | `auth.py` | 登录、登出、改密码、查看专用密码 |
| `memos.js` | `memos.py` | 备忘录增删改查、TXT 导出 |
| `todos.js` | `todos.py` | 待办增删改查、批量更新 |
| `passwords.js` | `passwords.py` | 密码本、查看明文、备份导出 |
| `categories.js` | `categories.py` | 分类增删改查 |
| `users.js` | `users.py` | 用户管理（管理员） |
| `logs.js` | `logs.py` | 操作日志查询 |

命名一致不是巧合，而是刻意设计：**前端找接口、后端找路由，看同一个名字就行。**

---

## 谁在调用 api 文件

分层不只给页面用，组件和 Store 也会直接调：

| 调用方 | 文件 | 调用的 api |
|--------|------|-----------|
| 页面 | `views/MemoListView.vue` | `@/api/memos`、`@/api/categories` |
| 页面 | `views/TodoListView.vue` | `@/api/todos` |
| 页面 | `views/PasswordListView.vue` | `@/api/passwords`、`@/api/auth`、`@/api/categories` |
| 页面 | `views/UserManageView.vue` | `@/api/users` |
| 组件 | `components/CategorySelect.vue` | `@/api/categories` |
| 组件 | `components/ViewPasswordDialog.vue` | `@/api/auth` |
| Store | `stores/auth.js` | `@/api/auth` |

**规律：**

- 一个页面可能 import **多个** api 文件（密码页同时用 `passwords` 和 `auth`）
- 组件也可以直接用 api，不必经过页面中转
- 页面里几乎不出现裸 URL（不应写 `axios.get('/api/...')`）

---

## 写 api 文件的规律

### 认证 API 示例（`api/auth.js`）

```javascript
import request from '@/utils/request'

export function login(data) {
  return request.post('/auth/login', data)
}

export function logout() {
  return request.post('/auth/logout')
}

export function getMe() {
  return request.get('/auth/me')
}

export function verifyViewPassword(viewPassword) {
  return request.post('/auth/view-password/verify', { view_password: viewPassword })
}
```

### 分类 API 示例（`api/categories.js`）

带查询参数时，用 `{ params: { ... } }`：

```javascript
export function listCategories(moduleType) {
  return request.get('/categories', { params: { module_type: moduleType } })
}
```

### 密码本 API 示例（`api/passwords.js`）

特殊接口（查看明文、下载备份）也是同一文件里加函数：

```javascript
export function revealPassword(id, data) {
  return request.post(`/passwords/${id}/reveal`, data)
}

export function exportBackup() {
  return request.get('/passwords/export/backup', { responseType: 'blob' })
}
```

### 返回数据怎么用

后端成功时格式（响应拦截器已检查 `code === 0`）：

```json
{
  "code": 0,
  "message": "ok",
  "data": { ... 真正要用的数据 ... }
}
```

页面拿到的 `res` 就是上面这一整包，**业务数据在 `res.data` 里**：

| 场景 | 取什么 |
|------|--------|
| 备忘录列表 | `res.data.items`、`res.data.total` |
| 登录 | `res.data.access_token`、`res.data.user` |

---

## 标准写法与反例

### 推荐

```javascript
// api 层：只写路径和方法
import request from '@/utils/request'

export function listSomething(params) {
  return request.get('/something', { params })
}

// 页面：只 import 函数名
import { listSomething } from '@/api/something'

const res = await listSomething({ page: 1 })
items.value = res.data.items
```

### 不推荐

| 反例 | 问题 |
|------|------|
| 页面里 `import axios from 'axios'` | 绕过封装，公共配置和拦截器失效 |
| 页面里直接 `axios.get('/api/memos')` | 应放在 `api/memos.js`，页面调 `listMemos()` |
| 页面里直接 `request.get('/memos')` | 应经过 api 层，保持分层清晰 |
| 一个 api 文件混写多个不相关功能 | 违背「一功能一文件」，难找难改 |
| 函数名写成 `getData1`、`fetchApi` | 看不出业务含义，应写 `listMemos`、`createTodo` |

---

## 动手练习（3 道题）

由浅入深，尽量自包含。

---

### 练习 1：认目录、认对应关系（约 5 分钟）

#### 要练会什么

- 能在项目里找到 `web/src/api/` 下 7 个文件
- 能说出每个文件对应后端哪个 `.py`
- 能说出「页面 → api → request → 后端」四层关系

#### 怎么做

1. 打开 `web/src/api/`，数一数有几个文件，分别叫什么
2. 打开 `server/app/api/`，对比文件名是否一一对应
3. 打开 `MemoListView.vue`，找到 `import ... from '@/api/memos'`，再打开 `api/memos.js` 看 `listMemos` 里写了什么路径

#### 自检

- [ ] 能说出 `api/memos.js` 对应后端 `memos.py`
- [ ] 能说出页面不直接写 URL，而是调 `listMemos()`

---

### 练习 2：读真实 api 文件，总结命名规律（约 10 分钟）

#### 要练会什么

- 识别 GET / POST / PUT / DELETE 在 api 文件里长什么样
- 理解函数名和 HTTP 方法的对应关系

#### 怎么做

依次打开并阅读：

1. `web/src/api/memos.js` — 标准 CRUD
2. `web/src/api/auth.js` — 登录类 POST 居多
3. `web/src/api/todos.js` — 注意 `batchUpdateTodos` 这种非 CRUD 接口

填表（自己写答案）：

| 函数名 | HTTP 方法 | 路径 |
|--------|-----------|------|
| `listMemos` | ? | ? |
| `createMemo` | ? | ? |
| `deleteTodo` | ? | ? |
| `login` | ? | ? |

**参考答案：**

| 函数名 | HTTP 方法 | 路径 |
|--------|-----------|------|
| `listMemos` | GET | `/memos` |
| `createMemo` | POST | `/memos` |
| `deleteTodo` | DELETE | `/todos/${id}` |
| `login` | POST | `/auth/login` |

---

### 练习 3：对照页面，走一遍完整调用（约 15 分钟）

#### 要练会什么

- 从页面点击「搜索」到表格出现数据，代码是怎么串起来的
- 知道 `res.data.items` 从哪来

#### 怎么做

1. 打开 `web/src/views/MemoListView.vue`
2. 找到 `loadData` 函数，看它怎么调 `listMemos`
3. 打开 `web/src/api/memos.js`，看 `listMemos` 怎么调 `request.get`
4. 打开 `web/src/utils/request.js`，看请求发出前、收到后各做什么
5. （可选）打开 `server/app/api/memos.py`，看后端 `list_memos` 返回什么

#### 预期理解

- 页面只关心 `page`、`page_size` 等业务参数
- api 层只关心路径 `/memos` 和方法 GET
- request 层只关心 token、code、报错
- 后端只关心查数据库、拼 `{ code: 0, data: {...} }`

---

## 练完后对照项目文件

建议按此顺序阅读：

| 顺序 | 文件 | 对照什么 |
|------|------|----------|
| 1 | `web/src/api/memos.js` | 标准 api 文件：import request + export 若干函数 |
| 2 | `web/src/api/auth.js` | 登录相关接口；Store 也会用 |
| 3 | `web/src/views/MemoListView.vue` | 页面怎么 import、怎么 `await listMemos()` |
| 4 | `web/src/stores/auth.js` | Store 层也走 api，不是直接 request |
| 5 | `web/src/components/CategorySelect.vue` | 组件也可以直接调 `@/api/categories` |
| 6 | `server/app/api/memos.py` | 前后端文件名、路径如何对应 |

### 自检清单

- [ ] 能说出 API 模块分层 = `web/src/api/` 按功能拆文件
- [ ] 能区分三层：页面调函数、api 写路径、request 管公共规矩
- [ ] 能说出不用分层时，改一个 URL 可能要改很多页面
- [ ] 能说出用了分层后，改 URL 只改一个 api 文件
- [ ] 知道 `@/api/memos` 里的 `@` 是路径别名，指向 `web/src/`
- [ ] 知道业务数据在 `res.data` 里（拦截器已处理 `code !== 0` 的情况）

---

## 总结

**API 模块分层**就是把「怎么跟后端说话」从页面里抽出来，按功能放进 `web/src/api/` 每个文件里，用 `listMemos()` 这种好懂的名字代替裸网址。不用它，每个页面都要自己记 URL、自己处理登录和报错，项目一大就难维护；用了它，页面只负责「我要什么数据」，接口细节集中管理，改一处全站生效。对你这种刚学前后端来说，记住一条就够：**页面管界面，`api/` 管要数据，`request.js` 管公共规矩**——各干各的，代码才不容易乱。建议先读 [Axios_study.md](./Axios_study.md) 理解 `request.js`，再对照本文和 `web/src/api/*.js`，把概念和真实项目对上号。
