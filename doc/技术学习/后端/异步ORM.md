# SQLAlchemy 2.x 异步 ORM 学习笔记

> 结合本项目（wizzy 小智工具箱）的通俗讲解，面向零基础。  
> 动手练习脚本：`demo/异步ORM_demo/`（练习 1～4 可一键运行）

---

## 目录

1. [一句话理解](#一句话理解)
2. [打个比方](#打个比方)
3. [在本项目中的作用](#在本项目中的作用)
4. [不用 vs 用了](#不用-vs-用了)
5. [实质好处](#实质好处)
6. [深入：异步是如何实现的](#深入异步是如何实现的)
7. [动手练习（5 道题）](#动手练习5-道题)
8. [可执行练习脚本（第 1～4 题）](#可执行练习脚本第-14-题)
9. [练完后对照项目文件](#练完后对照项目文件)
10. [总结](#总结)

---

## 一句话理解

**SQLAlchemy 2.x 异步 ORM = 用 Python 类和对象读写 MySQL，而且等数据库回复时不会把整个后端卡死。**

拆开看：

| 词 | 通俗含义 |
|----|----------|
| **ORM** | 用 Python 类（如 `Memo`）代表数据库表（如 `memos`），不用手写 SQL 字符串 |
| **2.x** | SQLAlchemy 2.0 新写法：`select()`、`Mapped`、`mapped_column` |
| **异步** | 访问数据库时用 `await`，等待期间服务器可以去处理别的请求 |

---

## 打个比方

把后端想象成一家餐厅：

- **MySQL** = 仓库（数据真正存放的地方）
- **SQLAlchemy ORM** = 服务员和仓库之间的「翻译官 + 办事员」
- **AsyncSession** = 每个客人（HTTP 请求）专用的一张「办事工单」
- **`await`** = 办事员向仓库发请求后，不傻站着，先去招呼别的客人；仓库回话了再回来继续

前端点「保存备忘录」时，数据流大致是：

```
前端 Vue  →  FastAPI 接口  →  memo_service  →  SQLAlchemy  →  MySQL
```

你写的是「新建一个 Memo 对象」，SQLAlchemy 在背后帮你生成 SQL 并执行。

---

## 在本项目中的作用

### 它不可或缺在哪里？

本项目所有需要**持久保存**的数据——用户、备忘录、待办、密码本、登录 Token、操作日志——都通过 SQLAlchemy 读写 MySQL。

以创建备忘录为例：

```51:62:server/app/services/memo_service.py
async def create_memo(db: AsyncSession, user: User, req: MemoCreateRequest) -> Memo:
    """创建备忘录"""
    memo = Memo(
        user_id=user.id,
        title=req.title,
        content=req.content,
        category_id=req.category_id,
        is_pinned=req.is_pinned,
    )
    db.add(memo)
    await db.flush()
    return memo
```

你操作的是 Python 对象 `Memo(...)`，不是 SQL 字符串。

**没有它**：后端就没有统一、可靠的方式把用户数据写进 MySQL；`server/app/models/`、`server/app/services/` 整套结构也搭不起来。

### 项目里的三层分工

```
API 层 (app/api/)       →  接收 HTTP，注入 db
Service 层 (app/services/) →  业务逻辑 + await db.execute(...)
Model 层 (app/models/)   →  表结构定义（Memo、User、Todo ...）
基础设施 (core/database.py) →  引擎、Session、get_db
```

架构文档里的描述：

```
FastAPI 异步框架 + SQLAlchemy ORM + MySQL 5.7
```

数据库连接串（注意 `mysql+aiomysql`，异步驱动）：

```14:15:server/app/core/config.py
    # 数据库
    DATABASE_URL: str = "mysql+aiomysql://wizzy:wizzy123@127.0.0.1:3306/wizzy_db"
```

---

## 不用 vs 用了

### 整体对比

| | **不用 SQLAlchemy** | **用了（本项目）** |
|--|---------------------|-------------------|
| 写代码方式 | 自己拼 SQL 字符串 | 写 Python 类和对象 |
| 和 FastAPI 配合 | 自己管连接开/关 | `Depends(get_db)` 自动借还 |
| 多人协作 | 每人 SQL 写法可能不同 | 表结构集中在 `models/` |
| 出错时 | 自己处理「写一半失败」 | `get_db()` 自动 commit 或 rollback |

### 例子 A：查备忘录列表

- **不用**：手写  
  `SELECT * FROM memos WHERE user_id = 123 AND title LIKE '%关键词%' ...`  
  还要自己把每一行转成 Python 字典。
- **用了**：  
  `select(Memo).where(Memo.user_id == user.id)`  
  查出来直接是 `Memo` 对象。

### 例子 B：创建备忘录

- **不用**：拼 `INSERT INTO memos (...) VALUES (...)`，自己防 SQL 注入、自己回滚。
- **用了**：`memo = Memo(...)` → `db.add(memo)` → `await db.flush()`。

### 例子 C：和 FastAPI 配合

- **不用**：每个接口自己开连接、关连接，忘了关就泄漏。
- **用了**：接口写 `db: AsyncSession = Depends(get_db)`，请求结束自动提交或回滚：

```34:42:server/app/core/database.py
async def get_db():
    """依赖注入：获取数据库会话，请求结束自动关闭"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

---

## 实质好处

### 好处 1：用 Python 对象操作数据库

- **不用**：改字段名要全局搜 SQL，漏一处就 bug。
- **用了**：表结构在 `models/memo.py` 一处定义；业务里写 `memo.title = req.title`。

```14:24:server/app/models/memo.py
class Memo(Base):
    """备忘录表"""

    __tablename__ = "memos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
```

### 好处 2：异步 —— 等数据库时还能接别的请求

- **不用（同步）**：线程等 MySQL 期间什么都干不了，请求容易排队。
- **用了（异步）**：`await db.execute(...)` 时让出执行权，FastAPI 可处理其他请求。

### 好处 3：出错自动回滚

- **不用**：插入成功、后续步骤失败，可能留下脏数据。
- **用了**：`get_db()` 里任何一步抛错都会 `rollback()`，本次请求的数据库改动全部撤销。

### 好处 4：和 Pydantic Schema 配合顺畅

- **不用**：查出来是元组，还要手动拼 JSON。
- **用了**：`Memo` 对象 → `MemoResponse.model_validate(m)` 转成 API 响应（见 `api/memos.py`）。

> Schema（`schemas/memo.py`）不负责异步；它管入参校验和出参格式。异步发生在更下层的 `AsyncSession` ↔ MySQL。

### 好处 5：表关系有明确定义

- **不用**：删用户时可能忘了删他的备忘录，留下孤儿数据。
- **用了**：模型里 `ForeignKey(..., ondelete="CASCADE")`，规则写在模型上。

---

## 深入：异步是如何实现的

### 异步在本项目里指什么？

不是「多核 CPU 并行算题」，而是：

> **等 MySQL 回话（网络 I/O）时，不占用整个服务器傻等，先去处理别的请求；MySQL 有结果了再回来继续。**

### 五层配合（从外到内）

| 层级 | 本项目用的 | 作用 |
|------|-----------|------|
| 1. Web 服务器 | **Uvicorn**（ASGI） | 用事件循环调度 `async def` 接口 |
| 2. Web 框架 | **FastAPI** | 路由、`Depends` 依赖注入 |
| 3. 业务代码 | `async def` + `await` | 等数据库时不阻塞 |
| 4. ORM | **SQLAlchemy AsyncSession** | 异步执行 SQL |
| 5. 数据库驱动 | **aiomysql** | 和 MySQL 非阻塞通信 |

### 启动时：创建异步引擎

```11:25:server/app/core/database.py
# 异步数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_recycle=3600,
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
```

- **`create_async_engine`**：异步连接池管理器（借连接、还连接）。
- **`async_sessionmaker`**：生产 `AsyncSession` 的工厂；每个 HTTP 请求借一个 Session。

注意：必须用 `create_async_engine`，不能用同步的 `create_engine`。

### 每个请求：`get_db` 借 Session

FastAPI 的 `Depends(get_db)` 在每个接口执行前自动调用 `get_db`：

1. `async with` 打开 Session
2. `yield session` 交给接口用
3. 接口跑完后 `await session.commit()` 或 `rollback()`
4. 自动关闭 Session，连接还回池子

接口接入方式：

```python
async def create_memo(
    req: MemoCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    memo = await memo_service.create_memo(db, current_user, req)
```

鉴权里也会 `await db.execute(...)` 查 Token 和用户（`core/deps.py`）。

### 业务层：凡是碰数据库都要 `await`

```35:38:server/app/services/memo_service.py
    total = (await db.execute(count_query)).scalar() or 0
    query = query.order_by(Memo.is_pinned.desc(), Memo.updated_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
```

- `db.add(memo)`：放进 session 缓存，很快，不用 await。
- `await db.flush()` / `await db.execute(...)`：真正发到 MySQL，必须 await。

### 同步 vs 异步（底层直觉）

**同步：**

```
请求 A → 发 SQL → 线程卡住等 50ms → 收到结果 → 继续
请求 B → 可能得等 A 的空档
```

**异步：**

```
请求 A → await db.execute → 注册「等 MySQL」→ A 暂停
请求 B → 也可以 await 自己的查询
MySQL 回 A → 事件循环唤醒 A，从 await 下一行继续
```

- `async def`：函数里会有「暂停点」。
- `await`：I/O 等待时主动让出执行权。
- Uvicorn 维护**事件循环**，在多个请求之间切换。

### 走一遍「创建备忘录」时间线

1. Uvicorn 收到 `POST /api/memos`
2. `Depends(get_db)` 打开 `AsyncSession`
3. `Depends(get_current_user)` 两次 `await db.execute` 验 Token、查用户
4. `await memo_service.create_memo` → `db.add` → `await db.flush()`
5. 返回 JSON
6. `get_db` 收尾：`await session.commit()`
7. 关闭 Session

### 两个常见误解

| 误解 | 实际情况 |
|------|----------|
| 「用了 async 一定更快」 | 单次请求 SQL 还是要等 MySQL；好处在**多人同时访问**时不堵死 |
| 「写了 async def 就自动异步」 | 若在 async 里调用阻塞代码（同步 pymysql、`time.sleep`），仍会卡住事件循环 |

---

## 动手练习（5 道题）

练习 1～4 已有可执行脚本（见下一节）。练习 5 为纸面/自写综合题，最接近真实项目。

### 练习 1：感受「异步等数据库」

**要练会什么：** `create_async_engine`、`await`、`asyncio.run()`

**任务：** 连接内存 SQLite，执行 `SELECT 1`，打印结果。

**预期：**

| 情况 | 结果 |
|------|------|
| 正确 `await conn.execute(...)` | 打印 `查询结果: 1` |
| 漏写 `await` | 得到 coroutine 对象，不是数字 1 |

**脚本：** `demo/异步ORM_demo/exercise1.py`

---

### 练习 2：用 ORM 类代表一张表

**要练会什么：** `DeclarativeBase`、`Mapped`、`mapped_column`、建表、插入、查询

**测试数据：** `title="买菜"`, `content="鸡蛋、牛奶"`

**预期：**

| 情况 | 结果 |
|------|------|
| 成功 | 打印 `1 买菜 鸡蛋、牛奶` |
| 漏 `await session.commit()` | 新 session 查不到数据 |

**脚本：** `demo/异步ORM_demo/exercise2.py`

---

### 练习 3：查询 + 筛选 + 分页

**要练会什么：** `select().where().order_by().offset().limit()`、`func.count()`、`or_()`

**测试数据（插入 4 条）：**

| title | content |
|-------|---------|
| 周末计划 | 去爬山 |
| 购物清单 | 买水果 |
| 学习笔记 | 复习 SQLAlchemy |
| 临时备忘 | 打电话 |

**预期：**

| 调用 | items 的 title | total |
|------|----------------|-------|
| 默认第 1 页，page_size=2 | 临时备忘, 学习笔记 | 4 |
| page=2 | 购物清单, 周末计划 | 4 |
| keyword="购物" | 购物清单 | 1 |
| keyword="xyz" | （空） | 0 |

**脚本：** `demo/异步ORM_demo/exercise3.py`

---

### 练习 4：模拟 `get_db` —— 提交与回滚

**要练会什么：** `yield session` → 成功 commit → 失败 rollback

**场景 A（成功）：** 插入 `title="A"` → 正常结束 → 数据库里能查到 A

**场景 B（失败）：** 插入 `title="B"` → `raise ValueError` → 数据库里**没有** B

**脚本：** `demo/异步ORM_demo/exercise4.py`

---

### 练习 5：迷你综合题（自写，无脚本）

**要练会什么：** Model + Service +「API 层」+ 简单校验，串成最小闭环

**模型：** 简化版 `Memo`（含 `user_id`、`title`、`content`、`is_pinned`）

**业务规则：**

1. 只查 `user_id == 1` 的数据（模拟当前用户隔离）
2. 创建时 `title` 不能为空
3. 列表支持 keyword、分页；排序：`is_pinned` 降序，再 `id` 降序
4. 查别的 user_id 的 memo 要报「不存在」

**自测检查表：**

| 步骤 | 成功/失败 | 预期 |
|------|-----------|------|
| 创建「置顶」 | 成功 | 返回带 id |
| 创建「普通」 | 成功 | total = 2 |
| 创建空 title | **失败** | 数据库仍只有 2 条 |
| 列表 | 成功 | 「置顶」在「普通」前面 |
| keyword=普通 | 成功 | 只 1 条 |
| 插入 user_id=2 的数据 | 列表查不到 | 隔离生效 |

---

## 可执行练习脚本（第 1～4 题）

### 环境准备（Windows）

```powershell
cd demo\异步ORM_demo
pip install -r requirements.txt
```

依赖：`sqlalchemy`、`aiosqlite`（练习用内存 SQLite，语法与项目一致，无需装 MySQL）

### 一键运行

```powershell
python run_all.py
```

### 逐题运行

| 文件 | 命令 | 练什么 |
|------|------|--------|
| exercise1.py | `python exercise1.py` | create_async_engine + await |
| exercise2.py | `python exercise2.py` | ORM 模型 + insert/select |
| exercise3.py | `python exercise3.py` | 筛选 + 分页 + count |
| exercise4.py | `python exercise4.py` | get_db 风格 commit/rollback |

### 预期输出（大致）

**exercise1.py**

```
... SELECT 1 AS n ...
查询结果: 1
漏写 await 时得到 coroutine 对象，而不是查询结果
[PASS] query returns 1
[PASS] missing await detected
---
```

**exercise2.py**

```
[PASS] insert and select
[PASS] commit required
---
1 买菜 鸡蛋、牛奶
```

**exercise3.py**

```
[PASS] page 1 titles
[PASS] page 2 titles
[PASS] keyword filter
[PASS] empty keyword
---
page1: ['临时备忘', '学习笔记'] total=4
page2: ['购物清单', '周末计划'] total=4
keyword: ['购物清单'] total=1
empty: [] total=0
```

**exercise4.py**

```
[PASS] scenario A committed
[PASS] scenario B rolled back
---
场景 A: 找到 title=A
场景 B: 未找到 title=B (回滚生效)
```

**run_all.py** 最后一行：

```
ALL PASSED: 4/4 exercises
```

---

## 练完后对照项目文件

按「从底层到接口」顺序看：

| 你练到的能力 | 项目文件 |
|-------------|----------|
| 异步引擎、Session 工厂、`get_db` | `server/app/core/database.py` |
| 数据库连接串（aiomysql） | `server/app/core/config.py` |
| ORM 模型（`Mapped`、`ForeignKey`） | `server/app/models/memo.py` |
| `select` / 筛选 / 分页 / CRUD | `server/app/services/memo_service.py` |
| 请求里注入 `db`、调 service | `server/app/api/memos.py` |
| 鉴权里的 `await db.execute` | `server/app/core/deps.py` |
| 入参/出参（Schema，分层搭档） | `server/app/schemas/memo.py` |
| 整体架构说明 | `doc/后端技术架构.md` |

做完练习 4 后，重点对照 `database.py` 和 `memo_service.py`；做完练习 5 后，再通读 `api/memos.py` 看完整请求链路。

---

## 总结

在本项目里，**SQLAlchemy 2.x 异步 ORM** 是 Python 与 MySQL 之间的翻译官：你用类和 `await db.execute(...)` 读写数据，它负责生成 SQL、管理连接，出错时自动回滚。  
不用它也能存数据，但要自己拼 SQL、管连接、处理并发和失败，成本高且易错。  
用了之后，业务代码像「操作 Python 对象」，与 FastAPI 的异步风格一致；动手练习见 `demo/异步ORM_demo/`，练完对照 `models/`、`services/`、`core/database.py` 即可看懂真实项目。
