# Axios 请求封装与拦截器学习笔记

> 结合本项目（wizzy 小智工具箱）的通俗讲解，面向零基础。  
> 动手练习脚本（练习 2）：`demo/前端/Axios_demo/`

---

## 目录

1. [一句话理解](#一句话理解)
2. [Axios 是什么](#axios-是什么)
3. [封装是什么、起什么作用](#封装是什么起什么作用)
4. [拦截器是什么、起什么作用](#拦截器是什么起什么作用)
5. [封装 + 拦截器：整条链路](#封装--拦截器整条链路)
6. [在本项目中的作用](#在本项目中的作用)
7. [不用 vs 用了](#不用-vs-用了)
8. [实质好处（带对比）](#实质好处带对比)
9. [补充：memos 是什么](#补充memos-是什么)
10. [在本项目里具体怎么用（三层结构）](#在本项目里具体怎么用三层结构)
11. [返回数据长什么样](#返回数据长什么样)
12. [标准写法与反例](#标准写法与反例)
13. [动手练习（3 道题）](#动手练习3-道题)
14. [练完后对照项目文件](#练完后对照项目文件)
15. [总结](#总结)

---

## 一句话理解

**Axios 是前端向后端要数据的工具；「封装」是做出全项目共用的 `request`；「拦截器」是在每次请求发出前、收到回复后自动加登录凭证、统一判成功失败。页面只管「我要办什么事」，身份和报错交给 `request.js` 这一层。**

---

## Axios 是什么

浏览器里的页面**不能直接访问数据库**，必须通过 **HTTP 请求**向服务器要数据或提交数据，例如：

- 「给我备忘录列表」
- 「我要登录」
- 「删除 id 为 5 的待办」

**Axios** 就是一个 JavaScript 库，专门帮你发这些请求、拿回结果。  
在本项目中，页面和 API 文件**不直接使用**原始的 `axios`，而是使用 `web/src/utils/request.js` 里定制出来的 **`request`**。

---

## 封装是什么、起什么作用

**封装 = 不用原始 Axios 到处乱用，而是先「定制一个专用版本」，全项目只用它。**

原始用法（每个文件自己写）：

```javascript
axios.get('http://xxx/api/memos', {
  headers: { Authorization: 'Bearer ...' },
  timeout: 30000,
})
```

本项目做法（`web/src/utils/request.js`）：

```javascript
const request = axios.create({
  baseURL: '/api',    // 公共前缀
  timeout: 30000,     // 30 秒超时
})
```

| 配置项 | 含义 |
|--------|------|
| `axios.create(...)` | 从 Axios「复印一台专用机」，名字叫 `request` |
| `baseURL: '/api'` | 以后只写 `/memos`，自动变成访问 `/api/memos` |
| `timeout: 30000` | 等 30 秒还没回应就当作失败 |

**作用**：全站请求的默认规则写在一处；`memos.js`、`auth.js` 里只写 `request.get('/memos')`，不用每次重复前缀、超时等配置。

---

## 拦截器是什么、起什么作用

**拦截器 = 在「真正发出去之前」和「收到回复之后」自动插入的一段代码。**

可以想成快递：

| 时机 | 类比 | 本项目在干什么 |
|------|------|----------------|
| **请求拦截器** | 打包前检查：要不要贴「会员标签」 | 若用户已登录，自动在请求头加上 `Authorization: Bearer token` |
| **响应拦截器** | 拆包后统一处理：坏了就通知、过期就办退会 | 看后端 `code` 是不是 0；失败就弹窗；401 就退出登录并跳转登录页 |

### 请求拦截（发出前自动带 token）

```javascript
request.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`
  }
  return config
})
```

### 响应拦截（收到后统一判成功/失败）

```javascript
request.interceptors.response.use((response) => {
  if (response.config.responseType === 'blob') {
    return response   // 下载文件时不按 JSON 处理
  }
  const res = response.data
  if (res.code !== 0) {
    ElMessage.error(res.message || '请求失败')
    if (res.code === 401) {
      authStore.logout()
      router.push('/login')
    }
    return Promise.reject(new Error(res.message))
  }
  return res
})
```

**作用**：业务代码不用在每个 `get/post` 里写「取 token、塞 header、看 code、弹错误、401 跳登录」；拦截器对**每一次**走 `request` 的请求自动执行。

---

## 封装 + 拦截器：整条链路

```
页面 / 组件
    ↓ 调用 api/memos.js 里的 listMemos()
    ↓ 内部：request.get('/memos')
    ↓
【请求拦截器】有 token 吗？有 → 加到请求头 Authorization
    ↓
真正发到后端 /api/memos
    ↓
【响应拦截器】是下载文件吗？是 → 原样返回
              否则 code === 0 吗？是 → 把 res 交给页面用
              否 → 弹错误；若是 401 → 清登录、去 /login
```

---

## 在本项目中的作用

可以把前后端想成：**浏览器里的页面** ↔ **服务器上的接口**（统一走 `/api/...`）。

封装 + 拦截器相当于全站共用的**三条规矩**，写在一个地方，所有接口自动遵守：

| 规矩 | 项目里具体在干什么 |
|------|-------------------|
| 地址前缀 | 只写 `/memos`、`/auth/login`，`baseURL: '/api'` 自动拼好 |
| 登录凭证 | 登录后的 token，**每次请求**自动带上 `Authorization: Bearer ...` |
| 结果怎么处理 | 后端用 `code === 0` 表示成功；失败弹提示、401 清登录并跳登录页 |

### 哪些文件在用

| 层级 | 文件 | 作用 |
|------|------|------|
| 第 1 层 | `web/src/utils/request.js` | 封装 + 拦截器 |
| 第 2 层 | `web/src/api/*.js`（7 个） | 各功能的接口函数 |
| 第 3 层 | 页面、`stores/auth.js` 等 | 调用 api，用 `res.data` 更新界面 |

**不可或缺在哪？** 登录、备忘录、待办、密码库等所有功能，都靠同一套规则和后端说话。否则每个功能都要自己复制粘贴 token、错误提示、跳登录，极易漏改、行为不一致。

---

## 不用 vs 用了

| 场景 | 不用（每个 API 裸用 axios） | 用了（本项目） |
|------|----------------------------|----------------|
| 写接口 | 每个文件自己拼 `/api`、超时、token | 只有一个 `request`，默认配好 |
| 登录凭证 | 每个 `get/post` 前手动从 store 取 token | 请求拦截器自动加 |
| 错误提示 | 有的页面弹窗、有的只 console.log | 响应拦截器统一 `ElMessage.error` |
| 401 过期 | 有的跳登录、有的不跳 | 统一 `logout` + `router.push('/login')` |
| 改规则 | 改 token 格式要动很多文件 | 只改 `request.js` 一处 |

**本质区别：**

- **不用** = 每个功能各自为政，重复逻辑堆 everywhere
- **用了** = 前端和后端之间的「总机 + 前台」，业务只写「我要办什么事」

---

## 实质好处（带对比）

### 好处一：不用在每个请求里手写「我是谁」（JWT）

| 不用 | 用了 |
|------|------|
| 每个 `get/post` 前都要写「从 store 取 token，塞进 headers」；漏一处就 401 | 请求拦截器写一次；`listMemos`、`getMe`、`createTodo` 全部自动带 token |

### 好处二：错误提示和「登录过期」行为全站一致

| 不用 | 用了 |
|------|------|
| 有的 catch 了只 `console.log`，401 有的跳、有的不跳 | `code !== 0` 或网络错误统一弹窗；401 统一清登录并去 `/login` |

### 好处三：业务代码更短、改规则更安全

| 不用 | 用了 |
|------|------|
| 7 个 `api/*.js` 加几十个页面，重复逻辑难维护 | API 文件只描述「调哪个接口」；改 timeout 或 baseURL 只动 `request.js` |

### 好处四：和后端约定对齐（`code === 0`、文件下载）

| 不用 | 用了 |
|------|------|
| 每个调用都要自己判断 `response.data.code`；导出 blob 可能被当 JSON 解析报错 | 成功时直接拿处理好的 `res`；`responseType: 'blob'` 时原样返回 |

---

## 补充：memos 是什么

学习过程中常看到 `/memos`，它是本项目**「备忘录」功能**对应的后端接口路径，不是抽象概念。

| 概念 | 说明 |
|------|------|
| **memos 功能** | 记文字笔记：标题、内容、分类、置顶、搜索、导出 TXT 等 |
| **`/memos` 路径** | 访问该功能的 API 地址；加上 `baseURL` 后实际请求 `/api/memos` |
| **和其他模块** | `todos` = 待办；`passwords` = 密码本；`logs` = 操作日志 |

举例：`request.get('/memos')` 就是在说「向后端要备忘录列表的数据」。

---

## 在本项目里具体怎么用（三层结构）

### 第 1 层：`request.js`（一般只写一次）

见 `web/src/utils/request.js`：`axios.create` + 两个 `interceptors`。

### 第 2 层：`api/*.js`（按功能写接口）

Axios 最常用的 4 种写法：

| 方法 | 干什么 | 项目例子 |
|------|--------|----------|
| `request.get(路径, { params })` | **查**数据 | `listMemos({ page, page_size })` |
| `request.post(路径, 数据)` | **新增** / 提交 | `login(data)`、`createMemo(data)` |
| `request.put(路径, 数据)` | **修改** | `updateMemo(id, data)` |
| `request.delete(路径)` | **删除** | `deleteMemo(id)` |

示例（`web/src/api/memos.js`）：

```javascript
import request from '@/utils/request'

export function listMemos(params) {
  return request.get('/memos', { params })
}

export function createMemo(data) {
  return request.post('/memos', data)
}

export function exportMemoTxt(id) {
  return request.get(`/memos/${id}/export-txt`, { responseType: 'blob' })
}
```

- `{ params }` → 变成 URL 后面的 `?page=1&page_size=10`
- 第二个参数 `data` → POST/PUT 的请求体（表单 JSON）
- `responseType: 'blob'` → 下载文件，不按 JSON 解析

### 第 3 层：页面或 Store 里调用

页面**不直接**写 `request.get(...)`，而是：

```javascript
import { listMemos, createMemo } from '@/api/memos'

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

登录在 Store 里（`web/src/stores/auth.js`）：

```javascript
async login(credentials) {
  const res = await loginApi(credentials)
  this.token = res.data.access_token
  this.userInfo = res.data.user
}
```

---

## 返回数据长什么样

后端成功时大致格式（与 `demo/后端` 里「统一响应」一致）：

```json
{
  "code": 0,
  "message": "ok",
  "data": { ... 真正要用的数据 ... }
}
```

响应拦截器已检查 `code === 0`，页面拿到的 `res` 就是上面这一整包，**业务数据在 `res.data` 里**。

| 场景 | 取什么 |
|------|--------|
| 备忘录列表 | `res.data.items`、`res.data.total` |
| 登录 | `res.data.access_token`、`res.data.user` |

---

## 标准写法与反例

### 推荐

```javascript
// api 层
import request from '@/utils/request'
export function getSomething(id) {
  return request.get(`/something/${id}`)
}

// 页面
import { getSomething } from '@/api/xxx'
const res = await getSomething(1)
console.log(res.data)
```

### 不推荐

| 反例 | 问题 |
|------|------|
| 页面里 `import axios from 'axios'` | 绕过封装，公共配置和拦截器失效 |
| 页面里直接 `axios.get('/api/memos')` | 应放在 `api/memos.js`，页面调 `listMemos()` |
| 每个请求手动加 token | 应交给请求拦截器 |
| 每个请求自己判断 `code`、弹错误 | 应交给响应拦截器 |

---

## 动手练习（3 道题）

由浅入深，尽量自包含，**不依赖完整 wizzy 项目环境**。

---

### 练习 1：先会「发请求、拿结果」（浏览器控制台）

#### 要练会什么

- 理解：前端发请求 → 等一会儿 → 拿到数据
- 会用 GET 查、POST 交
- 会用 `.then()` 读返回结果

#### 怎么做（约 5 分钟）

1. 打开任意网页，按 `F12` → **Console（控制台）**
2. 依次粘贴运行：

**GET —— 查一条帖子**

```javascript
fetch('https://jsonplaceholder.typicode.com/posts/1')
  .then(r => r.json())
  .then(data => console.log('标题:', data.title))
```

**预期成功**：打印类似 `标题: sunt aut facere...`

**POST —— 提交假数据**

```javascript
fetch('https://jsonplaceholder.typicode.com/posts', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ title: '我的第一条', body: '测试内容' })
})
  .then(r => r.json())
  .then(data => console.log('返回 id:', data.id, '标题:', data.title))
```

**预期成功**：打印 `返回 id: 101 标题: 我的第一条`（id 可能为 101，假接口会编一个）

**故意写错地址**

```javascript
fetch('https://jsonplaceholder.typicode.com/xxx/wrong')
  .then(r => r.json())
  .then(data => console.log(data))
  .catch(e => console.log('失败了:', e.message))
```

**预期**：体会「请求可能失败」

#### 和本项目的关系

`request.get('/memos')` 本质上就是在做上面这些事，只是地址换成 `/api/memos`，且封装后不用每次写完整 URL。

---

### 练习 2：亲手写「迷你封装 + 拦截器」（推荐跑 demo）

#### 要练会什么

- **封装**：公共配置写一处
- **请求拦截器**：发出前自动加「身份牌」
- **响应拦截器**：收到后统一看 `code`，失败就 reject

#### 可执行代码位置

完整脚本已放在：

```
demo/前端/Axios_demo/
├── run-tests.js      # Node 自动测试（推荐 Windows）
├── index.html        # 浏览器按钮 + 自动测试
├── package.json
└── README.md
```

#### 运行方式（Windows）

```powershell
cd demo\前端\Axios_demo
npm install
node run-tests.js
```

或：`npm test`

**无需启动后端、无需打开 wizzy 主项目。**

#### 预期输出（大致样子）

```
========================================
  Axios 练习2：封装 + 拦截器 自动测试
========================================

--- 用例：1. GET /memos（无需登录，应成功） ---
  [请求拦截] GET /api/memos，未带 token
  [响应拦截] 成功，data={"items":[...],"total":2}
[OK] 1. GET /memos（无需登录，应成功）

--- 用例：2. GET /secret（未登录，应失败） ---
  [响应拦截] 失败 code=401，message=未登录
[OK] 2. GET /secret（未登录，应失败）（按预期失败）
     捕获错误：未登录

--- 用例：3. GET /secret（已登录，应成功） ---
[OK] 3. GET /secret（已登录，应成功）

--- 用例：4. GET /bad（业务 code=500，应失败） ---
[OK] 4. GET /bad（业务 code=500，应失败）（按预期失败）

========================================
  测试结果：4 通过，0 失败
========================================
```

#### 测试用例说明

| 用例 | 操作 | 预期 |
|------|------|------|
| 1 | GET `/memos`，无 token | 成功，`total=2`，第一条标题「买牛奶」 |
| 2 | GET `/secret`，无 token | 失败，`message=未登录` |
| 3 | 设置 token 后 GET `/secret` | 成功，`data=机密数据` |
| 4 | GET `/bad` | 失败，`message=服务器开小差了` |

浏览器版：双击 `index.html`，点「运行全部测试」或手动点各按钮，效果同上。

#### demo 与主项目对应

| demo | 主项目 |
|------|--------|
| `run-tests.js` 里的 `request` + 拦截器 | `web/src/utils/request.js` |
| `listMemos` / `getSecret` | `web/src/api/memos.js` 等 |
| `fakeToken` | `web/src/stores/auth.js` 里的 `token` |
| `fakeServer` 返回 `{ code, data, message }` | 后端 FastAPI 的 `success()` |

---

### 练习 3：迷你综合题（最接近真实项目）

#### 要练会什么

- 完整走通：**封装 → api 层 → 页面/Store 调用**
- 区分 **GET 带 params**、**POST 带 body**
- 成功读 `res.data`，失败进 `catch`

#### 场景

做一个「迷你备忘录」：**登录 → 拉列表 → 新建一条 → 再拉列表**。

#### 核心逻辑（可在练习 2 的 `run-tests.js` 基础上扩展）

**假后端（内存数据库）要点：**

- `POST /auth/login`：`admin` + `123456` 成功，错密码返回 `code=400`
- 未登录访问 `/memos` 返回 `code=401`
- `GET /memos` 返回列表
- `POST /memos`：无 `title` 失败；有 `title` 则新增

**api 层：**

```javascript
function login(data) { return request.post('/auth/login', data) }
function listMemos(params) { return request.get('/memos', { params }) }
function createMemo(data) { return request.post('/memos', data) }
```

**综合流程 `fullFlow()` 预期顺序：**

| 步骤 | 操作 | 预期 |
|------|------|------|
| 1 | 错误密码登录 | 失败：`用户名或密码错误` |
| 2 | 正确登录 | 成功，拿到 `access_token` |
| 3 | 拉列表 | 1 条：「初始备忘录」 |
| 4 | 新建（不传 title） | 失败：`标题不能为空` |
| 5 | 新建（有 title） | 成功 |
| 6 | 再拉列表 | 2 条：「初始备忘录 \| 我新建的」 |

练习 3 可自行在 `Axios_demo` 里按上述步骤扩展；对照主项目 `auth.js` + `MemoListView.vue` 的 `loadData`、`handleSubmit` 即可。

---

## 练完后对照项目文件

建议按此顺序阅读，与练习 2、3 一一对应：

| 顺序 | 文件 | 对照什么 |
|------|------|----------|
| 1 | `web/src/utils/request.js` | 练习 2 的 `axios.create`、两个 `interceptors` |
| 2 | `web/src/api/memos.js`、`web/src/api/auth.js` | 练习 3 的 `listMemos`、`createMemo`、`login` |
| 3 | `web/src/stores/auth.js` | 先 login，token 存起来，后面请求自动带 token |
| 4 | `web/src/views/MemoListView.vue` | `loadData`、`handleSubmit`：`await listMemos(...)`、`res.data.items` |

### 自检清单

- [ ] 能说出「封装」：`axios.create` 把 `baseURL`、超时写在一处
- [ ] 能说出「请求拦截器」：发出前自动加 `Authorization`
- [ ] 能说出「响应拦截器」：`code !== 0` 时 reject，页面走 catch
- [ ] 能区分：api 层只写路径，页面只 `await listMemos()` 拿 `res.data`
- [ ] 知道 `/memos` 是备忘录功能的 API 路径，不是 Axios 专用术语

---

## 总结

**Axios** 是前端向后端要数据的工具。**封装**是用 `axios.create` 做出全项目统一的 `request`，把 `/api` 前缀、超时等公共配置集中在一处。**拦截器**是在每次请求发出前、响应回来后自动执行：前者自动带登录 token，后者统一判断后端是否成功、弹错误、登录过期跳登录页。不用它，每个功能都要重复写 token 和报错逻辑；用了它，API 文件只写「访问哪个路径」，身份和错误处理交给 `request.js`，好维护、行为也一致。动手练完 `demo/前端/Axios_demo` 后，对照 `web/src/utils/request.js` 和 `web/src/api/*.js`，即可把概念和真实项目对上号。
