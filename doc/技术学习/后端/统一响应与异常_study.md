# 统一响应格式与业务异常 学习笔记

> 结合本项目（wizzy 备忘录系统）的通俗讲解，面向零基础。  
> 动手练习脚本：`demo/统一响应与异常_demo/`

---

## 目录

1. [一句话理解](#一句话理解)
2. [「回话」是什么](#回话是什么)
3. [打个比方](#打个比方)
4. [格式是什么样的](#格式是什么样的)
5. [在本项目中的作用](#在本项目中的作用)
6. [不用 vs 用了](#不用-vs-用了)
7. [实质好处](#实质好处)
8. [常见误解：500 和 404 不是一回事](#常见误解500-和-404-不是一回事)
9. [为什么不同报错可以同样格式输出](#为什么不同报错可以同样格式输出)
10. [报错种类梳理](#报错种类梳理)
11. [前后端对照表](#前后端对照表)
12. [动手练习（5 道题）](#动手练习5-道题)
13. [可执行 Demo 脚本](#可执行-demo-脚本)
14. [练完后对照项目文件](#练完后对照项目文件)
15. [总结](#总结)

---

## 一句话理解

**统一响应格式** = 后端每次「回话」都用同一个 JSON 结构 `{ code, message, data }`。  
**业务异常** = 预期内的失败（找不到、没权限、密码错）用 `BusinessException` 主动告诉前端，而不是让程序崩溃。

---

## 「回话」是什么

在这里，**「回话」= 后端收到请求之后，返回给前端的那段内容**。

可以想成打电话：

1. **你（前端）** 说：「帮我查 id=5 的备忘录」→ 这是**请求**
2. **对方（后端）** 说：「找到了，内容是 xxx」或「没找到」→ 这就是**回话**（也叫**响应 / 返回结果**）

在 Web 项目里，这段「回话」通常是一段 **JSON 文本**，例如：

```json
{ "code": 0, "message": "success", "data": { "title": "买菜清单" } }
```

或失败时：

```json
{ "code": 404, "message": "备忘录不存在", "data": null }
```

---

## 打个比方

前后端就像**餐厅前台和后厨**：

- **前台（前端）** 只负责点菜、上菜、告诉客人「成了 / 没成」。
- **后厨（后端）** 负责做菜，可能成功，也可能说「这道菜卖完了」。

**统一响应格式** = 规定：不管哪个窗口，回话都用同一张单子，上面固定三行：`code`、`message`、`data`。

**业务异常** = 后厨遇到「正常业务上的失败」（比如备忘录不存在、密码错了），不用乱喊、不用程序崩溃，而是**按固定格式**告诉前台原因。

---

## 格式是什么样的

### 后端：三种回话

所有接口回话本质上都是同一个「信封」：**`code` + `message` + `data`**。

#### 1. 成功

```json
{
  "code": 0,
  "message": "success",
  "data": { "title": "买菜清单", "content": "..." }
}
```

后端写法：`return success(数据)` 或 `return success(数据, "创建成功")`

项目代码（`server/app/core/exceptions.py`）：

```python
def success(data: Any = None, message: str = "success") -> dict:
    return {"code": 0, "message": message, "data": data}
```

#### 2. 业务失败（预期内的错误）

例如备忘录不存在、密码错了、没权限：

```json
{
  "code": 404,
  "message": "备忘录不存在",
  "data": null
}
```

后端写法：`raise BusinessException("备忘录不存在", code=404)`

全局处理器自动转成上面的 JSON（注意：HTTP 状态码是 **200**，真正的错误类型看 body 里的 **`code`**）：

```python
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    return JSONResponse(
        status_code=200,
        content={"code": exc.code, "message": exc.message, "data": None},
    )
```

#### 3. 系统崩溃（预期外的 bug）

例如代码写错、数据库连不上，没被 `BusinessException` 捕获：

```json
{
  "code": 500,
  "message": "服务器内部错误: xxxxx",
  "data": null
}
```

HTTP 状态码也是 **500**。

### 前端：统一判断

前端在 `web/src/utils/request.js` 里只写**一套**逻辑：

```javascript
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
```

---

## 在本项目中的作用

**作用一句话：让前后端说同一种「语言」。**

没有它，每个接口可能回完全不同的 JSON，前端每个页面都要单独猜「这次成功了吗？数据在哪？错了该显示啥？」。

有了它：

| 角色 | 做什么 |
|------|--------|
| **后端** | 成功就 `return success(...)`，业务失败就 `raise BusinessException(...)` |
| **前端** | 只写**一套**判断逻辑：看 `code` 是不是 0 |

**不可或缺**体现在：登录、备忘录、密码本、待办……几十个接口，前端不用每个都写一遍「怎么判断成功、怎么弹错、401 要不要跳登录页」。

---

## 不用 vs 用了

### 场景 A：查一条不存在的备忘录

| | **不用统一格式** | **用了（本项目）** |
|---|---|---|
| 后端可能返回 | 有的返回 `404` + HTML 错误页；有的返回 `{"detail":"Not Found"}`；有的直接抛异常变成 500 | 固定返回 `{ "code": 404, "message": "备忘录不存在", "data": null }` |
| 前端要做的事 | 每个接口写不同判断：`status === 404`？`detail` 字段？还是别的？ | 统一：`if (res.code !== 0)` → 弹 `res.message` |

> **注意**：左列三种情况是「不用统一格式时，同一种失败可能长成不同样子」；右列是「用了之后固定长成这一种」。**500 不会变成 404**。

### 场景 B：登录密码错了

| | **不用** | **用了** |
|---|---|---|
| 后端 | 可能 HTTP 401，也可能 HTTP 200 但 body 里有个 `error` 字段 | `raise BusinessException("用户名或密码错误", code=401)` → 自动变成标准 JSON |
| 前端 | 有的接口看 HTTP 状态码，有的看 body，逻辑分散 | 一处处理：`code === 401` → 登出并跳转登录页 |

### 场景 C：程序真出 bug（比如数据库连不上）

| | **不用** | **用了** |
|---|---|---|
| 后端 | 可能直接 500，返回一堆堆栈信息，格式各不一样 | 全局捕获，统一返回 `{ "code": 500, "message": "服务器内部错误: ..." }` |
| 前端 | 有时拿到 HTML 错误页，JSON 解析失败 | 至少格式一致，能稳定弹「网络错误」类提示 |

---

## 实质好处

### 好处 1：前端写一次，全站复用

- **不用**：10 个页面 × 10 种返回格式 = 100 处重复判断
- **用了**：`request.js` 里写一次，所有 `api/memos.js`、`api/auth.js` 等直接拿 `res.data` 用

### 好处 2：业务失败 ≠ 程序崩溃

- **不用**：「备忘录不存在」可能被当成程序 bug，返回 500，用户看到「服务器内部错误」
- **用了**：这是**预期内的失败**，后端主动说「备忘录不存在」，用户看到准确提示

### 好处 3：后端各模块写法一致

- **不用**：A 接口 `return {"ok": true}`，B 接口 `return memo对象`，C 接口失败时 `return None`
- **用了**：所有 service 失败都 `raise BusinessException(...)`，所有 API 成功都 `return success(...)`

### 好处 4：联调、调试更省事

- **不用**：打开浏览器 Network，每个接口 JSON 结构都不一样，要逐个看
- **用了**：永远先看 `code`，0 就看 `data`，非 0 就看 `message`

### 好处 5：以后加新功能成本低

- **不用**：新加一个「分类管理」接口，前端又要新写一套错误处理
- **用了**：后端 `success` / `BusinessException`，前端自动走同一套拦截器

---

## 常见误解：500 和 404 不是一回事

对比表里：

- **左列「不用统一格式」** 列了三种可能：404 页面、`detail` JSON、未处理异常变 500
- **右列「用了统一格式」** 是：这类业务失败固定变成 `{ code: 404, message: "备忘录不存在" }`

所以不是在说「500 变成 404」，而是在说：

- **不用**：同一种「找不到备忘录」，前端可能收到完全不同的回话
- **用了**：这类失败固定长成标准 JSON，`code` 准确表达错误类型

---

## 为什么不同报错可以同样格式输出

因为格式统一，**只统一「外壳」**；**里面的 `code` 和 `message` 仍然不同**。

可以想成快递盒：

```
┌─────────────────────────┐
│ code    → 是什么类型的结果 │
│ message → 具体说明        │
│ data    → 实际内容（或 null）│
└─────────────────────────┘
```

| 情况 | code | message | data |
|------|------|---------|------|
| 成功 | 0 | success | 备忘录内容 |
| 找不到 | 404 | 备忘录不存在 | null |
| 没登录 | 401 | 未提供有效的认证令牌 | null |
| 没权限 | 403 | 权限不足 | null |
| 程序 bug | 500 | 服务器内部错误: ... | null |

**外壳一样**，前端只需写 `if (res.code !== 0) { 弹窗(res.message) }`，具体差异由 `code` 和 `message` 表达。

---

## 报错种类梳理

可以分成 **4 层**：

```
请求进来
   │
   ▼
┌──────────────────────────────────────┐
│ ① 参数校验失败（FastAPI/Pydantic 自动） │  ← 请求体/参数格式不对
└──────────────────────────────────────┘
   │ 通过
   ▼
┌──────────────────────────────────────┐
│ ② 认证/权限失败（BusinessException）   │  ← 没 token、token 过期、非管理员
└──────────────────────────────────────┘
   │ 通过
   ▼
┌──────────────────────────────────────┐
│ ③ 业务规则失败（BusinessException）    │  ← 找不到、密码错、用户名已存在
└──────────────────────────────────────┘
   │ 通过
   ▼
┌──────────────────────────────────────┐
│ ④ 系统异常（未捕获的 Exception）       │  ← 真正的程序 bug
└──────────────────────────────────────┘
```

### ① 参数校验失败

**例子**：创建备忘录时 `title` 没传、类型不对。

- **谁发现**：FastAPI 自动校验
- **本项目现状**：还没专门统一成 `{code, message, data}`，可能仍是 FastAPI 默认格式（如 `{"detail": [...]}`）
- **前端**：可能走 `request.js` 里第二个 `error` 分支，而不是 `res.code !== 0`

### ② 认证 / 权限失败（code 401 / 403）

| code | 例子 |
|------|------|
| 401 | 没 token、token 过期、用户名密码错 |
| 403 | 账号被禁用、非管理员访问管理页、查看密码验证失败 |

### ③ 业务规则失败（code 400 / 404 等）

**「业务上说得通、但操作做不成」**，不是程序 bug：

| code | 例子 |
|------|------|
| 400 | 用户名已存在、原密码错误、不能删当前登录用户 |
| 404 | 备忘录/待办/分类/用户不存在 |
| 403 | 查看专用密码错误 |

后端统一写法：`raise BusinessException("具体原因", code=xxx)`

项目示例（`server/app/services/memo_service.py`）：

```python
if not memo:
    raise BusinessException("备忘录不存在", code=404)
```

### ④ 系统异常（code 500）

**开发者没预料到的错误**：数据库挂了、空指针、配置缺失导致代码崩溃等。

- 若开发者**主动**用 `BusinessException(..., code=500)`（如「AES 密钥未配置」），仍走业务异常通道，格式一样
- 若**没捕获**的异常，走 `general_exception_handler`，也是 `{ code: 500, message: "...", data: null }`

---

## 前后端对照表

| 种类 | 后端怎么产生 | 回话长什么样 | 前端怎么处理 |
|------|-------------|-------------|-------------|
| 成功 | `return success(data)` | `code: 0`, `data` 有内容 | 直接用 `res.data` |
| 业务失败 | `raise BusinessException(...)` | `code: 4xx`, `message` 可读, `data: null` | `res.code !== 0` → 弹 `message` |
| 系统失败 | 未捕获异常 | `code: 500`, HTTP 也是 500 | 走 axios 的 error 回调 |
| 参数校验 | FastAPI 自动 | 可能是 `detail` 字段（未完全统一） | 可能走 error 回调 |

---

## 动手练习（5 道题）

由浅入深，建议按顺序做。第 3、4 题已有可执行脚本（见下一节）。

### 第 1 题：认识「信封」——三种回话长什么样

**要练会什么**：看到 JSON 就能判断：这是成功、业务失败，还是系统失败。

**测试数据**：

```python
resp_ok  = {"code": 0,   "message": "success",       "data": {"title": "买菜"}}
resp_biz = {"code": 404, "message": "备忘录不存在",   "data": None}
resp_sys = {"code": 500, "message": "服务器内部错误", "data": None}
```

**预期**：写 `describe(resp)`，成功打印数据，失败打印 message。

---

### 第 2 题：手写 `success()`——成功时怎么打包

**要练会什么**：后端「成功回话」固定格式返回。

**预期输出**：

```
{'code': 0, 'message': 'success', 'data': {'id': 1, 'title': 'test'}}
{'code': 0, 'message': '删除成功', 'data': None}
{'code': 0, 'message': 'success', 'data': None}
```

---

### 第 3 题：手写 `BusinessException` + 捕获

**要练会什么**：「找不到资源」用 `BusinessException` 主动抛出，转成统一 JSON，而不是 500 崩溃。

**测试**：

| 输入 | 预期 |
|------|------|
| `memo_id=1` | `code:0`, `data` 有内容 |
| `memo_id=99` | `code:404`, `message:备忘录不存在` |

**可执行脚本**：`demo/统一响应与异常_demo/exercise3.py`

---

### 第 4 题：前端拦截器——`code !== 0` 时怎么处理

**要练会什么**：前端在「响应拦截器」里统一处理，不用每个页面单独判断。

**测试**：模拟 3 种回话（code=0 / 404 / 401），401 额外打印跳转登录。

**可执行脚本**：`demo/统一响应与异常_demo/exercise4.js`

---

### 第 5 题（综合）：迷你「备忘录 API」

**要练会什么**：把 success、BusinessException、全局捕获、前端统一判断串成完整链路。

**后端要求**：

- `api_list()` → 返回列表
- `api_get(id)` → 不存在则 404
- `api_delete(id)` → 默认备忘录不允许删（400），不存在 404
- 未捕获异常 → 500

**预期**：

| 调用 | 预期 |
|------|------|
| `list` | `code:0` |
| `get(1)` | `code:0` |
| `get(999)` | `code:404` |
| `delete(1)` | `code:400` |
| `delete(999)` | `code:404` |

---

## 可执行 Demo 脚本

目录：`demo/统一响应与异常_demo/`

### 环境准备（Windows）

```powershell
cd demo\统一响应与异常_demo
```

- 第 3 题：Python 3.8+（无需 pip 安装）
- 第 4 题：Node.js

### 逐题运行

| 文件 | 命令 | 练什么 |
|------|------|--------|
| exercise3.py | `python exercise3.py` | BusinessException + 统一 JSON |
| exercise4.js | `node exercise4.js` | 前端响应拦截器（code !== 0） |

### 一键运行 Python 题

```powershell
python run_all.py
```

第 4 题需单独运行：`node exercise4.js`

### exercise3.py 预期输出

```
[PASS] get memo_id=1 -> code=0
[PASS] get memo_id=99 -> code=404
[PASS] delete memo_id=99 -> code=404
[PASS] plain Exception -> code=500
---
成功: {'code': 0, 'message': 'success', 'data': {'id': 1, 'title': '买菜清单'}}
404:  {'code': 404, 'message': '备忘录不存在', 'data': None}
500:  {'code': 500, 'message': '服务器内部错误: 数据库连接失败', 'data': None}
```

### exercise4.js 预期输出

```
--- 测试 1 ---
页面拿到: { title: '买菜' }
--- 测试 2 ---
[弹窗] 备忘录不存在
页面收到 reject: 备忘录不存在
--- 测试 3 ---
[弹窗] 请先登录
[跳转] /login
页面收到 reject: 请先登录
---
[PASS] code=0 -> 返回 data
[PASS] code=404 -> 弹窗 + reject
[PASS] code=401 -> 弹窗 + 跳转 + reject
```

---

## 练完后对照项目文件

按「从后端到前端」顺序看：

| 顺序 | 文件 | 对照什么 |
|------|------|----------|
| 1 | `server/app/core/exceptions.py` | `success`、`BusinessException`、全局 `exception_handler` |
| 2 | `server/app/services/memo_service.py` | `raise BusinessException("备忘录不存在", code=404)` |
| 3 | `server/app/api/memos.py` | `return success({...})` 在真实路由里怎么用 |
| 4 | `web/src/utils/request.js` | `if (res.code !== 0)` 拦截器 |
| 5 | `server/app/services/auth_service.py` | 更多业务异常例子（401 密码错、403 禁用等） |

| 练习题 | 项目里对照 |
|--------|-----------|
| exercise3.py | `server/app/core/exceptions.py`、`server/app/services/memo_service.py` |
| exercise4.js | `web/src/utils/request.js` |

**建议对照方式**：做完每道练习题后，打开对应文件，找一句「和我写的几乎一样」的代码，映射关系：**练习里的 `handle_request` ≈ 项目里的 `api` 路由 + `service`**。

---

## 总结

**统一响应格式**规定后端每次回话都用 `{ code, message, data }`；**业务异常**让「正常会发生的失败」用固定方式告诉前端，而不是让程序乱报错。

不用它，前后端像各说各话，每个接口都要单独处理；用了它，后端写 `success()` / `BusinessException`，前端在 `request.js` 里统一判断一次，全项目受益。

对你这种刚学前后端的项目来说，这是**最划算的基础设施之一**：代码不多，但能让后面几十个接口都省心、好维护。
