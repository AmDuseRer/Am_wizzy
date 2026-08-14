# JWT 鉴权 + Token 白名单学习笔记

> 结合本项目（wizzy 小智工具箱）的通俗讲解，面向零基础。  
> 动手练习脚本（练习 2、3、4）：`demo/JWT_demo/`

---

## 目录

1. [一句话理解](#一句话理解)
2. [在本项目中的作用](#在本项目中的作用)
3. [不用 vs 用了](#不用-vs-用了)
4. [实质好处（带对比）](#实质好处带对比)
5. [深入：密钥如何与 Token 关联](#深入密钥如何与-token-关联)
6. [深入：「对称签名」和「对称加密」别混了](#深入对称签名和对称加密别混了)
7. [深入：服务器签发 → 白名单 → 返回客户端](#深入服务器签发--白名单--返回客户端)
8. [动手练习（5 道题）](#动手练习5-道题)
9. [练完后对照项目文件](#练完后对照项目文件)
10. [总结](#总结)

---

## 一句话理解

**登录成功后，服务器发给你一张「电子通行证」（JWT）；以后每次访问私人数据，你出示这张证；服务器除了验真，还会查一份「有效通行证名单」（Token 白名单），登出或改密时立刻作废。**

---

## 在本项目中的作用

### 先打个比方

| 东西 | 对应什么 |
|------|----------|
| JWT | 登录后保安发的**电子通行证**（一串字符） |
| Token 白名单 | 保安电脑里的**有效名单**（数据库 `user_tokens` 表） |
| 登录 | 发证 + 登记到名单 |
| 每次请求 | 验证 + 查名单 |
| 登出 / 改密 | 从名单里作废 |

### 正常流程

```
你输入账号密码登录
    ↓
服务器验密码通过 → 用密钥签发 JWT → 把 jti 写入 user_tokens 白名单
    ↓
前端保存 access_token，之后每次请求自动带上 Authorization: Bearer xxx
    ↓
访问备忘录 / 密码本 / Todo 时：
  ① 验 JWT 签名（是不是我发的、有没有被改过）
  ② 查白名单（这张证有没有被登出/改密作废）
  ③ 查账号是否被禁用
    ↓
全部通过 → 返回你自己的数据
```

### 项目里用在哪

| 场景 | 处理方式 |
|------|----------|
| 登录 | 签发 JWT，写入 `user_tokens` |
| 每次请求 | 解析 JWT + 查表确认 jti 未 revoke |
| 登出 | revoke 当前 jti |
| 改密码 | revoke 该用户全部 jti（强制所有设备下线） |
| 禁用用户 | `is_active=False`，下次请求拒绝 |

### 哪些接口依赖它

本项目里几乎所有私人数据接口都要先过 `get_current_user`：

| 模块 | 文件 |
|------|------|
| 备忘录 | `server/app/api/memos.py` |
| Todo | `server/app/api/todos.py` |
| 密码本 | `server/app/api/passwords.py` |
| 分类 / 日志 | `server/app/api/categories.py`、`logs.py` |

**不可或缺在哪？** 没有它，后端就分不清「是张三在查自己的数据，还是陌生人在乱翻」，也无法在登出、改密、封号时立刻收回权限。

---

## 不用 vs 用了

| 场景 | 不用 | 用了（本项目） |
|------|------|----------------|
| 登录后访问数据 | 每次都要输账号密码，或干脆不验身份 | 登录一次，之后自动带 JWT 访问 |
| 看备忘录 / 密码本 | 谁都能调接口，可能看到别人的数据 | 必须带有效 JWT，且证在白名单里 |
| 点「退出登录」 | 前端删了 token，别人若复制过仍可能继续用 | 服务端把该证从白名单移除，立刻失效 |
| 改密码 / 账号被禁 | 旧证可能还能用很久（默认 7 天） | 该用户所有证批量作废，必须重新登录 |

**本质区别：**

- **不用** = 大门没锁，或锁了但钥匙复制出去就管不了
- **用了** = 有门禁 + 有作废名单，服务器能**主动收回**权限

---

## 实质好处（带对比）

### 好处一：不用每次操作都验密码

| 不用 | 用了 |
|------|------|
| 每打开一条备忘录都要查用户名、验密码 | 登录验一次，之后前端自动带通行证 |

### 好处二：数据不会串台

| 不用 | 用了 |
|------|------|
| 后端不知道当前是谁，要么全开放，要么大家看同一份数据 | JWT 里带有用户 ID，只返回**当前用户**的数据 |

### 好处三：能真正「退出登录」

| 不用（只有 JWT、没有白名单） | 用了（JWT + 白名单） |
|------------------------------|----------------------|
| 证像一张不能提前作废的票，过期前谁拿着都能用 | 登出时在名单里标记作废，同一张证立刻进不了门 |

### 好处四：改密码、封号能立刻生效

| 不用 | 用了 |
|------|------|
| 改密码或禁用账号后，旧证可能还能用 7 天 | 改密码作废全部证；禁用账号后直接拒绝 |

### 好处五：适合前后端分离

| 不用 | 用了 |
|------|------|
| 前后端绑得很紧，或安全边界模糊 | 后端只认带 Bearer token 的请求；前端存 token、自动带上 |

---

## 深入：密钥如何与 Token 关联

### 先说结论

**密钥不会写进 token 里。** 关联方式是：服务器用**同一把密钥**，签发时给 token「盖章」，验证时再检查「章还在不在、有没有被改过」。

### Token 长什么样（3 段）

一个 JWT 是三段用 `.` 拼起来的字符串：

```
头部.内容.签名
```

中间那段「内容」（payload）里是**明文信息**（只是 Base64 编码，不是加密），例如：

```json
{
  "sub": "1",
  "username": "zhang.san",
  "role": "user",
  "jti": "abc-123-uuid",
  "exp": 过期时间
}
```

最后一段「签名」才和密钥有关：

```
签名 = 用 JWT_SECRET 对「头部 + 内容」算出来的指纹
```

### 打个比方

| 东西 | 对应什么 |
|------|----------|
| Token 中间的内容 | 通行证上印的文字：「我是张三，编号 abc123」 |
| `JWT_SECRET` | 只有保安室知道的**专用印章** |
| 签名 | 印章盖在通行证上的印记 |
| 验证 | 保安用同一枚印章试盖一下，对得上才放行 |

**客户端会保存整个 token，但不知道 `JWT_SECRET`。** 密钥只存在于服务器 `.env` 里：

```env
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080
```

### 一个重要误区

JWT 的 payload **谁都能读**（Base64 解码即可）。签名只保证「没人能偷偷改内容而不被发现」，**不保证「别人看不到内容」**。

| 适合放 JWT 里 | 不适合放 JWT 里 |
|---------------|-----------------|
| 用户 ID、用户名、过期时间、jti | 密码、银行卡号等敏感信息 |

本项目里：登录密码用 Bcrypt 哈希；密码本内容用 AES 加密；JWT 只负责「证明你是谁、证还有效」。

### 完整验证流程

```
请求带来 token
    ↓
① 用 JWT_SECRET 验签（对称签名）  → 假的/改过的直接拒绝
    ↓
② 查 user_tokens 白名单           → 已登出/改密的拒绝
    ↓
③ 查用户是否被禁用                → 封号拒绝
    ↓
放行
```

---

## 深入：「对称签名」和「对称加密」别混了

「对称」的意思很简单：**加/验（或加/解）用的是同一把钥匙**。

本项目里其实有**两种不同用法**：

### 用法 1：JWT 验签（HS256）—— 对称签名，不是加密

| | 说明 |
|---|------|
| 用的密钥 | `.env` 里的 `JWT_SECRET` |
| 在干什么 | **签名 / 验签** |
| 谁有密钥 | 只有服务器 |
| 客户端 | 只拿 token，没有密钥 |
| 目的 | 证明 token 是「我发的、没被改过」 |
| 能不能读内容 | 能，payload 是明文编码 |

对应代码（`server/app/core/security.py`）：

```python
token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
```

### 用法 2：AES 加密（密码本）—— 这才是对称加密

| | 说明 |
|---|------|
| 用的密钥 | `.env` 里的 `AES_KEY` |
| 在干什么 | **加密 / 解密** |
| 目的 | 密文存库，需要时能还原明文给用户看 |

对应代码（`server/app/core/security.py`）：

```python
def aes_encrypt(plain_text: str) -> str: ...
def aes_decrypt(cipher_text: str) -> str: ...
```

### 一张表帮你区分

| | JWT（HS256） | AES（密码本） | Bcrypt（登录密码） |
|---|-------------|--------------|-------------------|
| 用的密钥 | `JWT_SECRET` | `AES_KEY` | 不需要固定密钥 |
| 在干什么 | 签名 / 验签 | 加密 / 解密 | 哈希（单向） |
| 是否对称 | 是（同密钥签+验） | 是（同密钥加+解） | 不适用 |
| 目的 | 证明 token 可信 | 密文存库、需要时能还原 | 存登录密码，永远不还原 |

---

## 深入：服务器签发 → 白名单 → 返回客户端

### 整体流程（4 步）

```
前端 POST /login
    ↓
① auth.py          接收登录请求
    ↓
② auth_service.py  验密码 → 调 create_access_token → 写入 user_tokens 白名单
    ↓
③ security.py      用 JWT_SECRET 签名，生成 token
    ↓
④ 返回 JSON 给前端  → 前端存 token
```

### 第 1 步：API 入口

`server/app/api/auth.py`：

```python
@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db), ip: str = Depends(get_client_ip)):
    token, user = await auth_service.login(db, req, ip)
    data = LoginResponse(
        access_token=token,
        user=auth_service.to_user_info(user),
    )
    return success(data.model_dump())
```

### 第 2 步：验密码 → 签名 → 加白名单

`server/app/services/auth_service.py`：

```python
async def login(db: AsyncSession, req: LoginRequest, ip: str = "127.0.0.1") -> tuple[str, User]:
    # ... 验密码、查 is_active ...

    token, jti, expire = create_access_token(user.id, user.username, user.role)

    # 写入 Token 表（白名单）
    token_record = UserToken(user_id=user.id, jti=jti, expires_at=expire.replace(tzinfo=None))
    db.add(token_record)
    await db.flush()

    return token, user
```

### 第 3 步：密钥签名（核心一行）

`server/app/core/security.py`：

```python
def create_access_token(user_id: int, username: str, role: str) -> tuple[str, str, datetime]:
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "jti": jti,
        "exp": expire,
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token, jti, expire
```

### 第 4 步：白名单表结构

`server/app/models/user.py`：

```python
class UserToken(Base):
    __tablename__ = "user_tokens"

    user_id: Mapped[int] = ...
    jti: Mapped[str] = ...           # 唯一通行证编号
    expires_at: Mapped[datetime] = ...
    is_revoked: Mapped[bool] = ...    # False=有效，True=已作废
```

登录成功后数据库多一行，例如：

| user_id | jti | expires_at | is_revoked |
|---------|-----|------------|------------|
| 1 | `a1b2c3d4-...` | 7 天后 | `False` |

`jti` 同时存在于 JWT 的 payload 里和 `user_tokens` 表里。

### 第 5 步：返回给客户端 + 前端存储

返回 JSON 大致如下（**没有** `JWT_SECRET`）：

```json
{
  "code": 200,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "user": { "id": 1, "username": "admin", "role": "admin" }
  }
}
```

前端 `web/src/stores/auth.js` 保存 token；`web/src/utils/request.js` 每次请求自动加：

```javascript
config.headers.Authorization = `Bearer ${authStore.token}`
```

### 请求回来时怎么验（对照用）

`server/app/core/deps.py` 的 `get_current_user`：

```python
async def get_current_user(authorization: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)) -> User:
    token = authorization[7:]  # 去掉 "Bearer "
    payload = decode_access_token(token)  # 验签
    user_id = int(payload.get("sub", 0))
    jti = payload.get("jti")

    # 查白名单
    result = await db.execute(
        select(UserToken).where(
            UserToken.jti == jti,
            UserToken.user_id == user_id,
            UserToken.is_revoked == False,
        )
    )
    if not token_record:
        raise BusinessException("令牌已失效，请重新登录", code=401)

    # 查用户是否被禁用
    ...
    return user
```

---

## 动手练习（5 道题）

练习 2、3、4 已做成可执行脚本，见 `demo/JWT_demo/`。练习 1、5 可复制下方代码到 `.py` 文件运行。

**环境准备（练习 2～4 / 一键运行）：**

```powershell
cd demo/JWT_demo
pip install -r requirements.txt
python run_all.py
```

---

### 第 1 题：看懂 JWT 里「藏了什么」（不用装库）

**要练会什么：** JWT 是「头部 + 内容 + 签名」三段拼在一起。这一题练：从 token 里读出用户是谁（先不管签名真假）。

```python
import json
import base64

fake_token = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJ6aGFuZy5zYW4iLCJyb2xlIjoidXNlciIsImp0aSI6ImFiYzEyMyIsImV4cCI6MTkwMDAwMDAwMH0."
    "fake-signature"
)

def read_payload(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("JWT 格式不对，应有 3 段")
    payload_b64 = parts[1]
    payload_b64 += "=" * (-len(payload_b64) % 4)
    payload_bytes = base64.urlsafe_b64decode(payload_b64)
    return json.loads(payload_bytes)

print(read_payload(fake_token))
```

**预期结果：**

| 检查项 | 应该看到 |
|--------|----------|
| `sub` | `"1"` |
| `username` | `"zhang.san"` |
| `jti` | `"abc123"` |

**对照项目：** 登录后 token 里会带上 `sub`、`username`、`role`、`jti`。

---

### 第 2 题：签发 + 验签

**要练会什么：** 服务器用密钥签发 JWT；篡改或过期必须拒绝。

**运行方式：**

```powershell
cd demo/JWT_demo
python exercise2.py
```

**预期输出（大致）：**

```
  正常 token 验签成功，sub=1, username=zhang.san
[PASS] 正常 token 验签成功，sub=1, username=zhang.san
[PASS] 篡改 token 后验签失败
[PASS] 过期 token 验签失败
[PASS] 错误密钥验签失败
---
全部测试通过
```

**对照项目：** `server/app/core/security.py` → `create_access_token` / `decode_access_token`

---

### 第 3 题：白名单（字典模拟 user_tokens 表）

**要练会什么：** 光有 JWT 不够，还要查「这张证是否还有效」。

**运行方式：**

```powershell
python exercise3.py
```

**预期输出（大致）：**

```
[PASS] 刚加入白名单 -> True
[PASS] revoke 后 -> False
[PASS] user_id 不匹配 -> False
[PASS] jti 不存在 -> False
---
全部测试通过
```

**对照项目：** `server/app/models/user.py` → `UserToken` 表

---

### 第 4 题：登录 → 访问 → 登出

**要练会什么：** 把练习 2、3 合在一起：登录发 token 并登记白名单；访问时验 JWT + 查白名单；登出作废。

**运行方式：**

```powershell
python exercise4.py
```

**预期输出（大致）：**

```
[PASS] 正确密码登录成功
[PASS] 错误密码登录失败
[PASS] 登录后 get_current_user 成功
[PASS] 登出后 get_current_user 失败
[PASS] 禁用账号后访问失败
---
全部测试通过
```

**对照项目：**

- `server/app/services/auth_service.py` → `login` / `logout`
- `server/app/core/deps.py` → `get_current_user`

---

### 第 5 题：迷你综合题（最接近本项目）

**要练会什么：** 完整模拟 4 个关键场景：双设备登录、单设备登出、改密码全设备下线、无 token 拒绝。

**环境准备：**

```powershell
pip install PyJWT
```

**可复制运行的完整脚本：**

```python
"""
练习 5：迷你综合题
运行：python exercise5_jwt_mini.py
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import jwt

SECRET = "practice-secret-for-jwt-mini-demo-32b"
ALGORITHM = "HS256"

users = {"zhang.san": {"id": 1, "password": "123456", "role": "user", "is_active": True}}
whitelist: dict[str, dict] = {}


def create_token(user_id: int, username: str, role: str) -> tuple[str, str]:
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    payload = {"sub": str(user_id), "username": username, "role": role, "jti": jti, "exp": expire}
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM), jti


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET, algorithms=[ALGORITHM])


def add_to_whitelist(jti: str, user_id: int) -> None:
    whitelist[jti] = {"user_id": user_id, "is_revoked": False}


def revoke_token(jti: str) -> None:
    if jti in whitelist:
        whitelist[jti]["is_revoked"] = True


def revoke_all_for_user(user_id: int) -> None:
    for jti, record in whitelist.items():
        if record["user_id"] == user_id:
            record["is_revoked"] = True


def is_token_allowed(jti: str, user_id: int) -> bool:
    record = whitelist.get(jti)
    if not record or record["user_id"] != user_id:
        return False
    return not record["is_revoked"]


def login(username: str, password: str) -> str:
    user = users.get(username)
    if not user or user["password"] != password:
        raise Exception("用户名或密码错误")
    if not user["is_active"]:
        raise Exception("账号已被禁用")
    token, jti = create_token(user["id"], username, user["role"])
    add_to_whitelist(jti, user["id"])
    return token


def access_memos(token: str) -> str:
    if not token:
        raise Exception("未提供有效的认证令牌")
    payload = decode_token(token)
    user_id = int(payload["sub"])
    jti = payload["jti"]
    if not is_token_allowed(jti, user_id):
        raise Exception("令牌已失效，请重新登录")
    username = payload["username"]
    user = users.get(username)
    if not user or not user["is_active"]:
        raise Exception("用户不存在或已被禁用")
    return f"{username} 的备忘录列表"


def logout(token: str) -> None:
    payload = decode_token(token)
    revoke_token(payload["jti"])


def change_password(username: str, old_pwd: str, new_pwd: str) -> None:
    user = users.get(username)
    if not user or user["password"] != old_pwd:
        raise Exception("原密码错误")
    user["password"] = new_pwd
    revoke_all_for_user(user["id"])


def reset_demo() -> None:
    whitelist.clear()
    users["zhang.san"] = {"id": 1, "password": "123456", "role": "user", "is_active": True}


def main() -> None:
    reset_demo()

    # 1. 双设备登录
    token_phone = login("zhang.san", "123456")
    token_pc = login("zhang.san", "123456")
    assert access_memos(token_phone) == "zhang.san 的备忘录列表"
    assert access_memos(token_pc) == "zhang.san 的备忘录列表"
    print("[PASS] 双设备登录成功")

    # 2. 手机登出，只影响手机
    logout(token_phone)
    try:
        access_memos(token_phone)
        raise AssertionError("手机 token 应该失效")
    except Exception:
        pass
    assert access_memos(token_pc) == "zhang.san 的备忘录列表"
    print("[PASS] 单设备登出，另一设备仍可用")

    # 3. 改密码 -> 所有设备下线
    change_password("zhang.san", "123456", "newpass")
    try:
        access_memos(token_pc)
        raise AssertionError("改密后旧 token 应全部失效")
    except Exception:
        pass
    print("[PASS] 改密码后全部 token 失效")

    # 4. 新密码重新登录
    token_new = login("zhang.san", "newpass")
    assert access_memos(token_new) == "zhang.san 的备忘录列表"
    print("[PASS] 新密码登录成功")

    # 5. 无 token
    try:
        access_memos("")
        raise AssertionError("没 token 应拒绝")
    except Exception:
        pass
    print("[PASS] 无 token 访问被拒绝")

    print("---")
    print("全部测试通过")


if __name__ == "__main__":
    main()
```

**预期结果：**

| 步骤 | 该成功还是失败 |
|------|----------------|
| 双设备登录 | 成功 |
| 手机登出后手机 token | 失败 |
| 电脑 token（未登出） | 仍成功 |
| 改密码后所有旧 token | 全部失败 |
| 新密码重新登录 | 成功 |
| 空 token | 失败 |

**对照项目：** `auth_service.change_password` 里的 `revoke_all_tokens` / `update(UserToken)...is_revoked=True`

---

## 练完后对照项目文件

建议按这个顺序打开：

| 顺序 | 文件 | 对照什么 |
|------|------|----------|
| 1 | `server/app/core/security.py` | 签发 / 解析 JWT（练习 2） |
| 2 | `server/app/models/user.py` | `UserToken` 白名单表（练习 3） |
| 3 | `server/app/services/auth_service.py` | 登录写白名单、登出 revoke、改密批量 revoke（练习 4、5） |
| 4 | `server/app/core/deps.py` | `get_current_user`：验 JWT + 查白名单（练习 4、5） |
| 5 | `server/app/api/auth.py` | 登录 / 登出 API 入口 |
| 6 | `web/src/stores/auth.js` | 前端存 token |
| 7 | `web/src/utils/request.js` | 请求自动带 `Authorization: Bearer ...` |
| 8 | `server/.env` | `JWT_SECRET`、`JWT_ALGORITHM`、`JWT_EXPIRE_MINUTES` |

练完 5 题再打开上述文件，你会认出：**「哦，这就是我在练习题里自己写过的那套，只是项目里还多了数据库、FastAPI 依赖注入、操作日志。」**

---

## 总结

**JWT + Token 白名单**就是网站的「电子门禁」：登录发通行证（JWT），每次访问私人数据时验身份；同时在数据库维护有效名单（白名单），以便登出、改密、封号时立刻作废。

**密钥**用同一把 `JWT_SECRET` 给 token 签名和验签，但密钥不在 token 里；JWT 内容可被读取，签名只防篡改，不防偷看。

**不用它**，要么数据不安全、分不清用户，要么每次都要重新登录。**用了它**，登录一次即可顺畅使用，同时服务器还能主动收回权限——对存备忘录、密码本这类敏感信息的工具箱项目来说，这是刚需而不是可选项。
