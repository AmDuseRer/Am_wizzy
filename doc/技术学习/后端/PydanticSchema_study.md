# Pydantic Schema 请求校验 学习笔记

> 结合本项目（wizzy 备忘录系统）的通俗讲解，面向零基础。  
> 动手练习脚本：`demo/PydanticSchema_demo/`

---

## 目录

1. [一句话理解](#一句话理解)
2. [打个比方](#打个比方)
3. [在本项目中的作用](#在本项目中的作用)
4. [不用 vs 用了](#不用-vs-用了)
5. [实质好处](#实质好处)
6. [深入：可选字段是怎么实现的](#深入可选字段是怎么实现的)
7. [深入：读懂 ValidationError 报错](#深入读懂-validationerror-报错)
8. [动手练习（7 道题）](#动手练习7-道题)
9. [可执行练习脚本（第 2、3、5、6 题）](#可执行练习脚本第-2356-题)
10. [练完后对照项目文件](#练完后对照项目文件)
11. [总结](#总结)

---

## 一句话理解

**Pydantic Schema 请求校验 = 给每个 API 请求写一张「入境检查表」：前端 JSON 进来先对照表格检查，合格才转成 Python 对象交给业务逻辑。**

JSON 能解析，不等于数据合格。校验是第二步——检查字段齐不齐、类型对不对、值合不合理。

---

## 打个比方

前端（Vue）和后端（FastAPI）之间传的是 **JSON 文本**，像快递包裹里的纸条：

```json
{ "title": "买牛奶", "priority": "high" }
```

后端收到后，不能 blindly 相信这张纸条——可能写错、漏写、乱写。

**Pydantic Schema 就是「海关入境表格」：**

| 方向 | Schema 类型 | 作用 |
|------|-------------|------|
| 入境 | `XxxCreateRequest` / `XxxUpdateRequest` | 检查前端传来的 JSON 合不合格 |
| 出境 | `XxxResponse` | 规定返回给前端的 JSON 长什么样 |

项目 demo 里的注释写得很形象：

```1:9:demo/FastAPI_demo/schemas/todo_schema.py
"""
数据映射层（Schema）—— 连接「HTTP 世界」和「程序内部世界」

前端 / 客户端发的是 JSON，程序内部用的是 Todo 对象。
Pydantic Schema 负责：
  1. 校验入参（类型、长度、必填）
  2. 定义出参格式（返回给前端的 JSON 长什么样）

类比：海关表格——入境要填表（Request），出境给你盖章的凭证（Response）。
```

---

## 在本项目中的作用

可以把它理解成 **API 门口的保安 + 翻译官**，两件事：

| 角色 | 在本项目里具体做什么 |
|------|----------------------|
| **保安** | 前端发来的 JSON 对不对？标题有没有？太长没有？优先级是不是 `low/medium/high` 之一？不对就拦在门外 |
| **翻译官** | 合格的 JSON 转成后端能直接用的 Python 对象（`req.title`、`req.priority`），后面的 Service 不用自己拆 JSON |

以创建备忘录为例，Schema 定义在 `server/app/schemas/memo.py`：

```11:17:server/app/schemas/memo.py
class MemoCreateRequest(BaseModel):
    """创建备忘录"""

    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(default="", max_length=10000)
    category_id: Optional[int] = None
    is_pinned: bool = False
```

路由里只要写 `req: MemoCreateRequest`，FastAPI 就会自动按这张表检查：

```42:50:server/app/api/todos.py
@router.post("")
async def create_todo(
    req: TodoCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建待办"""
    todo = await todo_service.create_todo(db, current_user, req)
    return success(todo.model_dump(), "创建成功")
```

**校验失败直接返回 422，不会进入函数体**——坏数据进不了业务逻辑和数据库。

---

## 不用 vs 用了

### 场景 A：前端创建待办，标题是空的

| 不用 Pydantic | 用了 Pydantic（本项目） |
|---------------|-------------------------|
| 空标题可能一路进到数据库，列表里出现一条空白待办 | 规则写了 `min_length=1`，请求在进 `create_todo` 之前就被拒，返回 422 |
| 你要自己写：`if not title: return 错误` | 不用写，`MemoCreateRequest` 已经替你做了 |

### 场景 B：前端把优先级写成 `"urgent"`（项目只认 low/medium/high）

| 不用 Pydantic | 用了 Pydantic |
|---------------|---------------|
| 可能存进数据库，后面筛选、展示全乱套 | `pattern="^(low|medium|high)$"` 当场拦住 |
| bug 可能几天后才被发现 | 前端一提交就知道传错了 |

### 场景 C：前端漏传 `title` 字段

| 不用 Pydantic | 用了 Pydantic |
|---------------|---------------|
| 代码里 `data["title"]` 可能直接报错崩溃（500） | 自动返回 422，明确说「缺少 title」 |
| 用户看到「服务器错误」，开发者还要查日志 | 用户看到「你填错了什么」 |

### 场景 D：后端业务代码里用数据

| 不用 Pydantic | 用了 Pydantic |
|---------------|---------------|
| Service 拿到的是「一坨字典」，不知道里面有什么 | Service 拿到的是 `TodoCreateRequest`，确定有 `.title`、`.priority` |
| 每层都要重复检查「这个字段在不在、类型对不对」 | Service 只关心业务，比如 demo 里直接 `req.title.strip()` |

---

## 实质好处

### 好处一：坏数据进不了核心业务

- **不用**：错误数据可能穿过路由 → Service → 数据库，越往里越难查、越难修。
- **用了**：在 API 最外层就挡住，Service 和数据库可以默认「进来的数据已经合格」。

### 好处二：前后端对「该传什么」有同一份说明书

- **不用**：前端猜字段名，后端猜前端会传什么，联调靠口头约定和反复试错。
- **用了**：Schema 就是说明书——创建待办要哪些字段、多长、默认值是什么，写死在 `TodoCreateRequest` / `MemoCreateRequest` 里。

### 好处三：少写大量重复的 if/else 检查代码

- **不用**：每个接口都要写「标题不能为空、长度限制、priority 合法吗……」，todo、memo、用户注册各写一遍。
- **用了**：规则集中在 `server/app/schemas/` 目录，路由只写 `req: XxxRequest`，检查自动完成。

### 好处四：错误信息统一、友好

- **不用**：有的接口返回 `"error"`，有的抛异常，前端不好统一处理。
- **用了**：校验失败统一是 422，并列出哪个字段错了，前端可以提示「标题不能超过 200 字」。

### 好处五：写代码时更不容易手滑

- **不用**：`data.get("titile")` 拼错字段名，运行时才发现是 `None`。
- **用了**：IDE 能提示 `req.title`，拼错字段名写代码时就能发现。

---

## 深入：可选字段是怎么实现的

更新接口里常见写法：

```python
class MemoUpdateRequest(BaseModel):
    title: str | None = None      # 全可选
    is_pinned: bool | None = None
```

「可选」靠 **两个东西一起配合**：

| 写法 | 解决什么问题 |
|------|-------------|
| `= None` | JSON 里 **缺这个字段** 时不报错，自动填 `None` |
| `str \| None` | 字段值 **可以是 None**（类型上合法） |

### 三个具体请求

**请求 A：只改置顶**

```json
{"is_pinned": true}
```

- `title` 没传 → 自动变成 `None` → 表示「我不想改标题」
- `is_pinned` 为 `True` → 表示「我要改成置顶」
- 结果：校验通过

**请求 B：两个都不传**

```json
{}
```

- `title=None`，`is_pinned=None`
- 结果：校验通过（业务上等于「啥也没改」）

**请求 C：两个都传**

```json
{"title": "新标题", "is_pinned": false}
```

- 结果：校验通过，两个字段都有具体值

### 和「创建」对比

| | 创建 `MemoCreateRequest` | 更新 `MemoUpdateRequest` |
|--|--------------------------|--------------------------|
| title | **必须传**（`Field(...)` 里的 `...` 表示必填） | **可以不传**（默认 `None`） |
| 业务含义 | 新建备忘录，总得有个标题 | 可能只想改置顶，不想动标题 |

项目真实代码：

```14:26:server/app/schemas/memo.py
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(default="", max_length=10000)
    category_id: Optional[int] = None
    is_pinned: bool = False


class MemoUpdateRequest(BaseModel):
    """更新备忘录"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, max_length=10000)
    category_id: Optional[int] = None
    is_pinned: Optional[bool] = None
```

### 后端业务代码怎么用

```python
if req.title is not None:
    memo.title = req.title        # 用户想改标题

if req.is_pinned is not None:
    memo.is_pinned = req.is_pinned  # 用户想改置顶
```

- `title=None` → 跳过，保留原标题
- `title="新标题"` → 真的去改

### 容易踩的坑

项目版更新写法：

```python
title: Optional[str] = Field(None, min_length=1, max_length=200)
```

含义是：

- **不传** `title` → OK（None）
- **传了** `"新标题"` → OK
- **传了** `""` 空字符串 → 失败（传了就要至少 1 个字）

**「可选」≠「传什么都行」，而是「可以不出现；一旦出现，就要合格」。**

---

## 深入：读懂 ValidationError 报错

校验失败时，Pydantic 抛出 `ValidationError`，`e.errors()` 返回错误列表（一条 bad 数据可能有多处问题）。

```python
for err in e.errors():
    print("  字段:", err["loc"])
    print("  原因:", err["msg"])
    print("  传入值:", err.get("input"))
    print("  ---")
```

| 打印项 | 回答的问题 | 含义 |
|--------|------------|------|
| `loc` | **哪儿错了？** | 哪个字段出问题，如 `('title',)`、`('ids',)` |
| `msg` | **为什么错？** | 人话描述，如 `Field required`、`String should match pattern ...` |
| `input` | **实际传来的是什么？** | 用户提交的坏数据本身 |

### 举例

```python
bad_data = {"ids": [], "status": "done"}
```

可能打印：

```
一共 2 个错误：
  字段: ('ids',)
  原因: List should have at least 1 item after validation, not 0
  传入值: []
  ---
  字段: ('status',)
  原因: String should match pattern '^(pending|completed)$'
  传入值: done
  ---
```

在 FastAPI 项目里，校验失败会自动返回 **HTTP 422**，响应体结构类似。以后接口报错，按「字段 → 原因 → 传入值」逐条读就行。

---

## 动手练习（7 道题）

> 第 2、3、5、6 题已有完整可执行脚本，见下一节。  
> 第 1、4、7 题可在本地新建 `.py` 文件自行练习。

### 开始之前

```powershell
pip install pydantic
python -c "import pydantic; print(pydantic.__version__)"
```

---

### 第 1 题 · 热身：认识「请求数据长什么样」

**要练会什么：** 前端发给后端的是 JSON 文本，后端要先搞清楚「里面有哪些字段、值是什么类型」。

**环境：** 浏览器控制台（F12 → Console）

```javascript
JSON.parse('{"title": "买牛奶"}')   // A
JSON.parse('{"done": false}')      // B
JSON.parse('{title: "买牛奶"}')     // C
JSON.parse('{"title": 123}')       // D
```

| 数据 | 结果 |
|------|------|
| A | 成功，得到 `{ title: "买牛奶" }` |
| B | JSON 能解析，但 **没有 title**（后端若要求 title 必填，应拒绝） |
| C | 直接报错（连 JSON 都不是） |
| D | JSON 能解析，但 title 是 **数字不是文字**（后端若要求 str，应拒绝） |

**记住：** JSON 能解析 ≠ 数据合格。

---

### 第 2 题 · 最小 Schema：合格放行，不合格报错

**要练会什么：** 用 Pydantic 写第一张「入境检查表」，体验成功 vs 失败。

**脚本：** `demo/PydanticSchema_demo/exercise2.py`

```python
from pydantic import BaseModel, ValidationError

class TodoCreateRequest(BaseModel):
    title: str

def try_create(data: dict):
    try:
        req = TodoCreateRequest(**data)
        print("[OK]", req.title)
    except ValidationError as e:
        print("[FAIL]", e.errors()[0]["msg"])
```

| 测试数据 | 预期 |
|----------|------|
| `{"title": "买牛奶"}` | 成功 |
| `{}` | 失败（缺少 title） |
| `{"title": 123}` | 失败（title 必须是字符串） |

---

### 第 3 题 · 必填 vs 可选 + 默认值

**要练会什么：** 区分「创建时必须填」和「更新时可以只改一部分」。

**脚本：** `demo/PydanticSchema_demo/exercise3.py`

| 测试 | 预期 |
|------|------|
| 创建 `{"title": "购物清单"}` | 成功，`content=""`, `is_pinned=False` |
| 创建 `{"title": ""}` | 失败（标题至少 1 个字） |
| 创建 `{}` | 失败（缺 title） |
| 更新 `{"is_pinned": True}` | 成功，只有 `is_pinned=True` |
| 更新 `{}` | 成功（更新允许什么都不改） |

---

### 第 4 题 · 长度、范围：把「业务规则」写进 Schema

**要练会什么：** 用 `min_length` / `max_length` / `ge` / `le` 限制非法值。

```python
from pydantic import BaseModel, Field, ValidationError

class MemoListQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)

class ShortTitleRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
```

| 测试 | 预期 |
|------|------|
| `MemoListQuery(page=1, page_size=10)` | 成功 |
| `MemoListQuery(page=0)` | 失败（page 必须 >= 1） |
| `MemoListQuery(page_size=999)` | 失败（page_size 最大 100） |
| `ShortTitleRequest(title="a"*201)` | 失败（超过 200 字） |
| `ShortTitleRequest(title="OK")` | 成功 |

对照项目：`server/app/schemas/memo.py` 里的 `MemoListQuery`。

---

### 第 5 题 · 枚举/格式：只允许固定几个值

**要练会什么：** 用 `pattern` 限制字段只能是规定值。

**脚本：** `demo/PydanticSchema_demo/exercise5.py`

| 测 | 数据 | 预期 |
|----|------|------|
| 1 | `{"title": "写报告", "priority": "high"}` | 成功 |
| 2 | `{"title": "写报告", "priority": "urgent"}` | 失败 |
| 3 | `{"title": "写报告"}`（不传 priority） | 成功，默认 medium |
| 4 | `{"title": "", "priority": "low"}` | 失败 |

对照项目：`server/app/schemas/todo.py` 里的 `priority`、`status` 字段。

---

### 第 6 题 · 读懂报错：像前端一样知道「错在哪」

**要练会什么：** 校验失败时读出哪个字段、什么规则、什么值。

**脚本：** `demo/PydanticSchema_demo/exercise6.py`

坏数据：

```python
bad_data = {"ids": [], "status": "done"}
```

预期：至少 **2 个错误**——`ids` 不能为空列表；`status` 的 `"done"` 不符合 pattern。

---

### 第 7 题 · 迷你综合题（最接近真实项目）

**要练会什么：** 把 Create / Update / Response 串起来，模拟「路由收到 JSON → 校验 → 交给业务函数」。

```python
from pydantic import BaseModel, Field, ValidationError

class TodoCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")

class TodoUpdateRequest(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    status: str | None = Field(None, pattern="^(pending|completed)$")

class TodoResponse(BaseModel):
    id: int
    title: str
    priority: str
    status: str
    model_config = {"from_attributes": True}
```

链路：

```
前端 JSON → TodoCreateRequest 校验 → todo_service.create_todo → TodoResponse 返回
```

| 步骤 | 预期 |
|------|------|
| 创建 `{"title": "学 Pydantic", "priority": "high"}` | 成功 |
| 创建 `{"title": "坏数据", "priority": "urgent"}` | 失败，数据进不了「数据库」 |
| 更新 `{"status": "completed"}` | 成功，只改 status |
| 更新 `{"title": ""}` | 失败 |

---

## 可执行练习脚本（第 2、3、5、6 题）

完整代码在 `demo/PydanticSchema_demo/`，复制即可运行，内置自动测试。

### 环境准备（Windows）

```powershell
cd demo\PydanticSchema_demo
pip install -r requirements.txt
```

若中文乱码，可先执行 `chcp 65001` 切换到 UTF-8。

### 一键运行全部

```powershell
python run_all.py
```

### 逐题运行

| 文件 | 命令 | 练什么 |
|------|------|--------|
| exercise2.py | `python exercise2.py` | 最小 Schema，成功 vs 失败 |
| exercise3.py | `python exercise3.py` | 必填 vs 可选 + 默认值 |
| exercise5.py | `python exercise5.py` | pattern 限制固定取值 |
| exercise6.py | `python exercise6.py` | 读懂 ValidationError 报错 |

### 预期输出（大致）

**exercise2.py**

```
[PASS] 测1: 成功 -> title='买牛奶'
[PASS] 测2: 失败 -> Field required
[PASS] 测3: 失败 -> Input should be a valid string
---
3/3 tests passed
```

**exercise3.py**

```
[PASS] 创建-只传title: 成功 -> {'title': '购物清单', 'content': '', 'is_pinned': False}
[PASS] 创建-空标题: 失败 -> String should have at least 1 character
[PASS] 创建-啥也不传: 失败 -> Field required
[PASS] 更新-只改置顶: 成功 -> {'title': None, 'is_pinned': True}
[PASS] 更新-空对象: 成功 -> {'title': None, 'is_pinned': None}
---
5/5 tests passed
```

**exercise5.py**

```
[PASS] 测1: 成功 -> {'title': '写报告', 'priority': 'high'}
[PASS] 测2: 失败 -> String should match pattern '^(low|medium|high)$'
[PASS] 测3: 成功 -> {'title': '写报告', 'priority': 'medium'}
[PASS] 测4: 失败 -> String should have at least 1 character
---
4/4 tests passed
```

**exercise6.py**

```
一共 2 个错误：
  字段: ('ids',)
  原因: List should have at least 1 item after validation, not 0
  传入值: []
  ---
  字段: ('status',)
  原因: String should match pattern '^(pending|completed)$'
  传入值: done
  ---
[PASS] 检测到 2 个校验错误
---
1/1 tests passed
```

### 自测清单

- [ ] 能解释：JSON 合法 ≠ 请求合格
- [ ] 能区分 `Field(...)`（必填）和 `default=`（可不传）
- [ ] 知道 Create 和 Update 为什么规则不同
- [ ] 看到 `ValidationError` 能读出「哪个字段错了」
- [ ] 理解「校验在业务代码**之前**」——坏数据进不了 `create_todo`

---

## 练完后对照项目文件

按「从易到难」建议顺序：

| 顺序 | 文件 | 对照什么 |
|------|------|----------|
| 1 | `demo/FastAPI_demo/schemas/todo_schema.py` | 最短的 Create / Update / Response 示例，注释友好 |
| 2 | `demo/FastAPI_demo/api/todo_router.py` | Schema 怎么挂在路由参数上（`req: TodoCreateRequest`） |
| 3 | `server/app/schemas/memo.py` | 默认值、Optional、分页 Query |
| 4 | `server/app/schemas/todo.py` | 更完整的规则：pattern、datetime、批量更新 |
| 5 | `server/app/api/todos.py` | 真实项目里校验通过后如何进 Service |

---

## 总结

**Pydantic Schema 请求校验** 就是给每个 API 请求定一张「入境表格」：前端 JSON 进来先对照表格检查，合格才转成 Python 对象交给业务逻辑。

不用它，你要在每个接口里手写检查，容易漏、容易崩、前后端容易对不上；用了它，坏请求在门外就被拦住，业务代码更干净，前后端也有一份共同的字段约定。

对你这个 wizzy 项目来说，todo、memo、登录等所有「前端传数据过来」的接口，都靠 `server/app/schemas/` 下的 Schema 保证数据靠谱。
