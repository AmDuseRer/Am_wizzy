# 依赖注入（Depends）学习笔记

> 结合本项目（wizzy 备忘录系统）的通俗讲解，面向零基础。  
> 动手练习脚本：`demo/Depends_demo/`

---

## 目录

1. [一句话理解](#一句话理解)
2. [打个比方](#打个比方)
3. [格式是什么样的](#格式是什么样的)
4. [在本项目中的作用](#在本项目中的作用)
5. [不用 vs 用了](#不用-vs-用了)
6. [实质好处](#实质好处)
7. [深入：Depends + yield（自动关连接）](#深入depends--yield自动关连接)
8. [动手练习（5 道题）](#动手练习5-道题)
9. [练完后对照项目文件](#练完后对照项目文件)
10. [总结](#总结)

---

## 一句话理解

**`Depends(某个函数)` = 「调用我这个接口之前，请先帮我运行那个函数，把结果当参数传进来」。**

它不是你手动调用的，是 FastAPI 在收到请求时自动帮你调的。

---

## 打个比方

想象你是餐厅服务员（**接口函数**），客人点了一道菜（**HTTP 请求**）。

做菜需要三样东西：

- **数据库连接**（后厨的灶台）
- **当前登录用户**（确认是谁点的菜）
- **管理员权限**（有些菜只有经理能点）

**`Depends` 的作用就是：客人点菜之后、你把菜端上去之前，FastAPI 自动帮你把这三样东西准备好，直接递到你手里。**

你只管写「上菜」这件事（业务逻辑），不用每次重复「开灶台、查身份证、问是不是经理」。

---

## 格式是什么样的

依赖注入在本项目里，核心格式就一行：

```python
参数名: 类型 = Depends(准备函数名)
```

### 1. 最基础：接口里用 Depends

```python
from fastapi import Depends

async def list_memos(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 这里直接用 db 和 current_user
    ...
```

| 部分 | 含义 |
|------|------|
| `db` | 变量名，函数里用的名字 |
| `AsyncSession` | 类型提示 |
| `Depends(get_db)` | 告诉 FastAPI：去调用 `get_db`，把返回值给我 |

**注意：** 写 `Depends(get_db)`，不要写 `Depends(get_db())`（不要自己加括号调用）。

### 2. 准备函数本身怎么写

**格式 A：普通依赖（直接 return）**

```python
def get_client_ip(x_forwarded_for: Optional[str] = Header(None)) -> str:
    ...
    return "127.0.0.1"
```

**格式 B：带 yield 的依赖（借出 + 自动收尾）**

```python
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session          # 先借出去
            await session.commit() # 用完后自动执行
        except Exception:
            await session.rollback()
            raise
```

- **return**：给东西，函数就结束
- **yield**：给东西，暂停；外面用完后，函数从 yield 后面继续跑（用来关连接、提交事务）

### 3. 依赖套依赖（链式）

依赖函数的参数里，也可以写 `Depends`：

```python
async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),              # 依赖里再用依赖
) -> User:
    ...
    return user

async def require_admin(
    current_user: User = Depends(get_current_user),  # 又套一层
) -> User:
    if current_user.role != "admin":
        raise BusinessException("权限不足", code=403)
    return current_user
```

接口里只写一行：

```python
admin: User = Depends(require_admin)
```

FastAPI 自动按顺序执行：

```
require_admin -> get_current_user -> get_db
```

### 4. 多个依赖一起用

```python
async def create_user(
    req: UserCreateRequest,                 # 普通参数（请求体）
    db: AsyncSession = Depends(get_db),     # 依赖 1
    admin: User = Depends(require_admin),     # 依赖 2
    ip: str = Depends(get_client_ip),       # 依赖 3
):
    ...
```

### 5. 不需要返回值时

只想要「校验通过」，不需要用到返回的用户对象，用 `_` 当变量名：

```python
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),   # 只验管理员，不用这个变量
):
    ...
```

### 6. 本项目四种典型写法

| 用途 | 准备函数 | 接口里怎么写 |
|------|----------|--------------|
| 数据库 | `get_db` | `db: AsyncSession = Depends(get_db)` |
| 当前用户 | `get_current_user` | `current_user: User = Depends(get_current_user)` |
| 管理员 | `require_admin` | `admin: User = Depends(require_admin)` |
| 客户端 IP | `get_client_ip` | `ip: str = Depends(get_client_ip)` |

> 对应练习：格式入门见 [`demo/Depends_demo/exercise2.py`](../../demo/Depends_demo/exercise2.py)，链式见 [`exercise3.py`](../../demo/Depends_demo/exercise3.py)。

---

## 在本项目中的作用

在本项目里，几乎每个正式接口都要用到「公共准备」：

| 准备项 | 对应函数 | 放在哪 | 干什么 |
|--------|----------|--------|--------|
| 数据库连接 | `get_db` | `server/app/core/database.py` | 打开数据库，请求结束后自动提交/关闭 |
| 当前用户 | `get_current_user` | `server/app/core/deps.py` | 从请求头拿 Token，校验是否登录 |
| 管理员权限 | `require_admin` | `server/app/core/deps.py` | 在已登录基础上，再检查是不是 admin |
| 客户端 IP | `get_client_ip` | `server/app/core/deps.py` | 从请求头读取 IP，写操作日志用 |

**项目里的真实写法**（`server/app/api/memos.py`）：

```python
async def list_memos(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    memos, total = await memo_service.list_memos(db, current_user, ...)
    ...
```

**为什么不可或缺：**

1. **本项目有数据库 + 登录体系**，几乎每个接口都要「连库 + 认人」，没有 `Depends` 就要在每个函数里手写。
2. **`get_db` 还要负责用完关闭连接**，靠 `Depends` + `yield` 配合完成，漏关会导致连接泄漏（见下文第七节）。
3. **权限是链式的**：`require_admin` 内部又 `Depends(get_current_user)`，逻辑集中在一处。

> 补充：`demo/FastAPI_demo` 是极简 demo，故意没用 `Depends`（没有数据库）；正式后端 `server/app/` 才是完整用法。专门练 Depends 请看 `demo/Depends_demo/`。

---

## 不用 vs 用了

### 整体对比

| | **不用 Depends** | **用了 Depends** |
|---|------------------|------------------|
| 写法 | 每个接口开头自己写一堆准备代码 | 参数里写 `Depends(某个函数)` |
| 代码量 | 10 个接口 x 重复 20 行 = 200 行重复 | 准备逻辑只写 1 次 |
| 改登录逻辑 | 要改 10 个文件 | 只改 `deps.py` 里 1 个函数 |
| 忘关数据库 | 某个接口忘了 `close`，程序变慢/崩溃 | `get_db` 统一处理，不会漏 |

### 对比一：查备忘录列表

**不用 Depends：**

```python
async def list_memos(request: Request):
    session = AsyncSessionLocal()
    try:
        auth = request.headers.get("authorization")
        if not auth or not auth.startswith("Bearer "):
            raise HTTPException(401, "未登录")
        # ... 解析 Token、查库、验用户（十几行）...
        memos, total = await memo_service.list_memos(session, user, ...)
        await session.commit()
        return success(...)
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()  # 忘了这句就出事
```

**用了 Depends（本项目实际写法）：**

```python
async def list_memos(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    memos, total = await memo_service.list_memos(db, current_user, ...)
    return success(...)
```

业务代码从 30 行缩到 3 行。

### 对比二：管理员才能访问的用户列表

**用了 Depends（`server/app/api/users.py`）：**

```python
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),  # 一行：登录 + 管理员校验
):
    users, total = await user_service.list_users(db, page, page_size)
    ...
```

`require_admin` 内部已经调用了 `get_current_user`，写一行，背后自动做两步检查。

> 对应练习：[`demo/Depends_demo/exercise3.py`](../../demo/Depends_demo/exercise3.py)（admin-token 成功 / user-token 403）。

### 对比三：登录时记录 IP

**用了 Depends（`server/app/api/auth.py`）：**

```python
async def login(
    req: LoginRequest,
    db: AsyncSession = Depends(get_db),
    ip: str = Depends(get_client_ip),
):
    token, user = await auth_service.login(db, req, ip)
```

`get_client_ip` 写一次，登录、登出、改密码等接口都能复用。

---

## 实质好处

### 好处 1：少写重复代码

| 不用 | 用了 |
|------|------|
| 每个接口复制「连库 + 验 Token + 关库」 | 参数里声明 `Depends`，函数体只写业务 |
| `memos.py`、`todos.py`、`passwords.py` 各写一遍 | 全项目共用 `get_db`、`get_current_user` |

### 好处 2：行为一致，不容易漏检

| 不用 | 用了 |
|------|------|
| A 接口验 Token，B 接口忘了验 -> 安全漏洞 | 所有 `Depends(get_current_user)` 的接口规则相同 |
| 改登录逻辑只改了 3 个接口忘了第 4 个 | 改 `deps.py` 一处，全项目生效 |

### 好处 3：改一处，处处受益

| 不用 | 用了 |
|------|------|
| 改 Token 校验要搜遍所有 API 文件 | 只改 `get_current_user`（`deps.py`） |
| 换数据库连接方式，每个接口都要动 | 只改 `get_db`（`database.py`） |

### 好处 4：资源自动回收

| 不用 | 用了 |
|------|------|
| 某个接口 `try/finally` 写漏了，连接不释放 | `get_db` 用 yield：自动 commit/rollback/关闭 |
| 程序跑久了越来越慢 | 连接生命周期统一管理 |

### 好处 5：依赖可以链式复用

本项目的依赖链：

```
list_users 接口
    └── require_admin（必须是 admin）
            └── get_current_user（必须已登录）
                    └── get_db（需要查 Token 表和用户表）
```

FastAPI 会按正确顺序自动执行，不用操心谁先谁后。

> 对应练习：链式见 [`exercise3.py`](../../demo/Depends_demo/exercise3.py)，yield 见 [`exercise4.py`](../../demo/Depends_demo/exercise4.py)。

---

## 深入：Depends + yield（自动关连接）

这是初学者最容易卡住的地方，单独展开。

### 数据库连接为什么要「还」？

数据库像**电话客服中心**，连接数有限。借了连接必须挂断；一直占着不还会**连接泄漏**，程序越跑越慢，最后连不上库。

### get_db 在项目里长什么样

```python
# server/app/core/database.py
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session          # 暂停，把 session 交给接口用
            await session.commit() # 接口跑完后继续：提交
        except Exception:
            await session.rollback()  # 出错：撤销
            raise
    # 出了 with 块，session 自动关闭
```

接口里：

```python
db: AsyncSession = Depends(get_db)
```

### yield 是什么？

把 `yield` 理解成：**「先借给你用，你用完我再继续干后面的收尾工作。」**

借充电宝类比：

1. 店员拿出充电宝（`yield session`）
2. 你用手机（接口函数用 `db` 查数据）
3. 你用完了（接口函数结束）
4. 店员自动还充电宝、记账（`commit/rollback`，然后关闭 session）

### 一次请求的完整时间线

以 `GET /memos` 为例：

```
1. 请求进来
2. FastAPI 看到 Depends(get_db)，开始执行 get_db()
3. get_db 打开 session
4. 遇到 yield session -> 暂停，交给 list_memos 的 db 参数
5. list_memos 用 db 查备忘录
6. list_memos 返回 JSON
7. get_db 从 yield 后面继续：commit 或 rollback
8. session 自动关闭，连接已归还
```

| 阶段 | 谁在做 | 干什么 |
|------|--------|--------|
| 请求开始前 | `get_db`（yield 之前） | 打开连接 |
| 请求处理中 | 你的接口函数 | 用 `db` 查/写数据 |
| 请求结束后 | `get_db`（yield 之后） | 提交/回滚 + 关闭连接 |

### 连接泄漏是什么？

假设连接池最多 10 条，每次请求借了不还：

```
第 1 次：借 1 条，没还 -> 剩 9 条
第 10 次：借 1 条，没还 -> 剩 0 条
第 11 次：没有连接可借 -> 报错/超时/网站卡住
```

**Depends + yield 的价值：** 即使用户代码忘了关，FastAPI 也会在请求结束时自动跑 yield 后面的收尾代码。

> 动手感受：运行 [`demo/Depends_demo/exercise4.py`](../../demo/Depends_demo/exercise4.py)，观察借出/归还日志；加分实验见该目录 README（注释掉 `finally` 里的归还逻辑，模拟泄漏）。

---

## 动手练习（5 道题）

所有脚本在 **`demo/Depends_demo/`**，复制即可运行，每题内置自动测试。

### 环境准备（Windows）

```powershell
cd demo\Depends_demo
pip install -r requirements.txt
```

### 一键运行全部

```powershell
python run_all.py
```

成功时最后一行：`ALL PASSED: 5/5 exercises`

---

### 练习 1：理解「注入」概念（纯 Python）

| 项目 | 内容 |
|------|------|
| **脚本** | [`demo/Depends_demo/exercise1.py`](../../demo/Depends_demo/exercise1.py) |
| **命令** | `python exercise1.py` |
| **要练会** | 函数自己不准备工具，外面先准备好再传进来（Depends 的核心思想） |
| **预期** | `[PASS] morning greeting` / `[PASS] evening greeting`，输出「早上好，小明！」等 |

---

### 练习 2：Depends 基本格式

| 项目 | 内容 |
|------|------|
| **脚本** | [`demo/Depends_demo/exercise2.py`](../../demo/Depends_demo/exercise2.py) |
| **命令** | `python exercise2.py` |
| **要练会** | `参数名: 类型 = Depends(函数名)` |
| **预期** | `GET /welcome` 返回 `{'message': '欢迎光临'}` |
| **可选** | `uvicorn exercise2:app --reload`，浏览器打开 `/docs` |

---

### 练习 3：链式 Depends + 成功/失败

| 项目 | 内容 |
|------|------|
| **脚本** | [`demo/Depends_demo/exercise3.py`](../../demo/Depends_demo/exercise3.py) |
| **命令** | `python exercise3.py` |
| **要练会** | `admin_only -> require_admin -> get_user -> get_token` 链条 |
| **测试数据** | 请求头 `X-Token` |
| **预期** | `admin-token` -> 200；`user-token` -> 403；`wrong-token` -> 401；不传 -> 422 |
| **对应项目** | `server/app/core/deps.py` 里的 `require_admin` |

---

### 练习 4：yield 借还（模拟 get_db）

| 项目 | 内容 |
|------|------|
| **脚本** | [`demo/Depends_demo/exercise4.py`](../../demo/Depends_demo/exercise4.py) |
| **命令** | `python exercise4.py` |
| **要练会** | yield 前借出，yield 后归还；理解连接池 |
| **预期** | 控制台打印 `[get_conn] borrow ...` / `returned ...`；两次请求后 `pool after tests: ['conn-1', 'conn-2']` |
| **对应项目** | `server/app/core/database.py` 里的 `get_db` |
| **加分实验** | 注释掉 `finally` 里的 `POOL.append(conn)`，再运行，观察连接被借光 |

---

### 练习 5：迷你综合（最接近本项目）

| 项目 | 内容 |
|------|------|
| **脚本** | [`demo/Depends_demo/exercise5.py`](../../demo/Depends_demo/exercise5.py) |
| **命令** | `python exercise5.py` |
| **要练会** | `get_db(yield)` + `get_current_user(Header + Depends)` + 业务接口 |
| **测试数据** | 请求头 `Authorization: Bearer token-alice` 或 `Bearer token-bob` |
| **预期** | alice 只看到自己的 memo；无 token / 错误 token -> 401 |
| **对应项目** | `database.py` + `deps.py` + `api/memos.py` 的简化版 |
| **可选** | `uvicorn exercise5:app --reload`，在 `/docs` 里填 Authorization 测试 |

---

### 建议练习顺序（约 1~2 小时）

```
练习 1（10 分钟）-> 搞懂「注入」概念
练习 2（15 分钟）-> 会写 Depends 基本格式
练习 3（20 分钟）-> 链式依赖 + 成功/失败测试
练习 4（20 分钟）-> 理解 yield 借还
练习 5（30 分钟）-> 迷你综合，对照真实项目
```

更多运行说明见 [`demo/Depends_demo/README.md`](../../demo/Depends_demo/README.md)。

---

## 练完后对照项目文件

按此顺序阅读效果最好：

| 顺序 | 文件 | 看什么 | 对应练习 |
|------|------|--------|----------|
| 1 | `server/app/core/database.py` | 真实版 `get_db` + yield + commit/rollback | exercise4 |
| 2 | `server/app/core/deps.py` | `get_current_user`、`require_admin` 链式 Depends | exercise3、exercise5 |
| 3 | `server/app/api/memos.py` | 业务接口怎么「只写一行 Depends」 | exercise5 |
| 4 | `server/app/api/users.py` | `Depends(require_admin)` 管理员场景 | exercise3 |
| 5 | `server/app/api/auth.py` | 多个 Depends 混用（db + user + ip） | exercise2、exercise5 |
| 6 | `demo/FastAPI_demo/` | 极简版（故意没用 Depends），对比学习 | - |

---

## 总结

`Depends` 在本项目里负责**自动准备数据库、登录用户、权限和 IP**，让几十个 API 接口不用重复写同样的「开场白」。

- **格式：** `参数名: 类型 = Depends(准备函数名)`
- **不用它：** 每个接口复制粘贴准备代码，容易漏验登录、漏关数据库
- **用了它：** 接口只关心业务，改规则只改 `database.py` / `deps.py`，全项目生效
- **yield：** `get_db` 借连接给接口用，请求结束后自动提交/回滚/关闭

建议路径：**先读本文 -> 按顺序做 `demo/Depends_demo/` 五道题 -> 再对照 `server/app/` 真实代码**。
