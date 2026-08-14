# Bcrypt 密码哈希学习笔记

> 结合本项目（wizzy 备忘录系统）的通俗讲解，面向零基础。  
> 动手练习脚本（练习 2、3）：`demo/Bcrypt_demo/`

---

## 目录

1. [一句话理解](#一句话理解)
2. [在本项目中的作用](#在本项目中的作用)
3. [不用 vs 用了](#不用-vs-用了)
4. [实质好处（带对比）](#实质好处带对比)
5. [深入：「能验证、但拿不回去」](#深入能验证但拿不回去)
6. [动手练习（5 道题）](#动手练习5-道题)
7. [练完后对照项目文件](#练完后对照项目文件)
8. [总结](#总结)

---

## 一句话理解

**Bcrypt 把用户的真实密码变成一串「只能用来核对、没法还原成原密码」的乱码，存进数据库。**

登录时，你照常输入密码；服务器再算一遍，看跟库里那串乱码是否对得上——全程不需要、也不能把乱码变回明文。

---

## 在本项目中的作用

先分清两件事：

| 密码类型 | 存法 | 原因 |
|----------|------|------|
| **登录密码、查看专用密码** | Bcrypt 哈希 | 只需判断「对不对」，不需要把原密码读出来 |
| **密码本里的网站密码** | AES 加密 | 以后还要解密拿出来看，走另一条路 |

Bcrypt 只管**账号密码**。

### 正常流程

```
你输入 abc123
    ↓
服务器用 Bcrypt 搅成一串乱码，比如 $2b$12$k3j8...（很长）
    ↓
数据库里只存这串乱码，不存 abc123
    ↓
下次登录：你再输入 abc123 → 服务器再搅一遍 → 看跟库里那串是否对得上
```

### 项目里用在哪

| 场景 | 做什么 |
|------|--------|
| 管理员创建用户 | `hash_password(req.password)` → 存进 `password_hash` |
| 用户登录 | `verify_password(你输入的, 库里存的)` → 对上了才发 Token |
| 改密码 / 重置密码 | 旧密码先验证，新密码再 `hash_password` |
| 设置「查看专用密码」 | 同样 hash 后存进 `view_password_hash` |

### 对应代码

`server/app/core/security.py`：

```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    """使用 Bcrypt 对明文密码进行不可逆哈希"""
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)
```

登录时的调用（`server/app/services/auth_service.py`）：

```python
if not user or not verify_password(req.password, user.password_hash):
    raise BusinessException("用户名或密码错误", code=401)
```

数据库字段（`server/app/models/user.py`）：

```python
password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
view_password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
```

**不可或缺在哪？** 因为服务器**不应该、也不能**在数据库里存你的真实密码。Bcrypt 就是干这件事的：把密码变成「能验证、但拿不回去」的形式。

---

## 不用 vs 用了

### 方案 A：不用 Bcrypt，明文存密码

数据库 `users` 表可能是：

| username | password |
|----------|----------|
| 张三 | abc123 |
| 李四 | hello888 |

**后果：**

- 数据库被拖走 → 黑客直接看到所有人的真实密码
- 很多用户多个网站用同一密码 → 一个站泄露，别的站也危险
- 连管理员、开发自己查库都能看见用户密码

### 方案 B：用了 Bcrypt（本项目现在的做法）

数据库 `users` 表是：

| username | password_hash |
|----------|---------------|
| 张三 | `$2b$12$k3j8f...很长一串...` |
| 李四 | `$2b$12$x9m2a...另一串...` |

**后果：**

- 数据库被拖走 → 黑客看到的只是一堆乱码，**不能直接当密码用**
- 登录仍然正常：你输入 `abc123`，服务器用 Bcrypt 比对，对上了就让你进
- 开发、DBA 查库也**看不到**你的真实密码

---

## 实质好处（带对比）

### 好处一：数据库泄露时，密码不会「原样曝光」

| 不用 Bcrypt | 用了 Bcrypt |
|-------------|-------------|
| 泄露后：`password = "abc123"`，黑客直接拿去别的网站试 | 泄露后：只有 `$2b$12$...`，**没法直接登录** |

### 好处二：系统内部的人也看不到你的密码

| 不用 Bcrypt | 用了 Bcrypt |
|-------------|-------------|
| 开发查库：`SELECT password FROM users` 就能看到 | 开发查库：只能看到哈希，**还原不出原密码** |

### 好处三：同样密码，存进库里的字符串也不一样

Bcrypt 每次都会加随机「调料」（salt）。

| 不用 Bcrypt | 用了 Bcrypt |
|-------------|-------------|
| 两个用户都设 `123456`，库里两行都是 `123456`，一眼就能猜常见密码 | 两个用户都设 `123456`，库里是两串**完全不同**的乱码，黑客没法靠「相同字符串」批量破解 |

### 好处四：故意算得慢，拖慢暴力猜密码

| 不用 Bcrypt（或普通快速算法） | 用了 Bcrypt |
|------------------------------|-------------|
| 电脑一秒能试几百万个密码 | Bcrypt 故意慢，猜一个要更久，**暴力破解成本高很多** |

### 好处五：登录流程依然简单（对你透明）

| 不用 Bcrypt | 用了 Bcrypt |
|-------------|-------------|
| 你照常输入密码登录 | 你也照常输入密码登录，**体验完全一样** |
| 只是背后不安全 | 背后多了一层保护，前端不用改 |

---

## 深入：「能验证、但拿不回去」

### 「拿不回去」

注册时你输入密码 `abc123`，服务器调用 `hash_password("abc123")`，得到类似：

```
$2b$12$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p9ldGx8gsw
```

数据库里存的就是这串，**不是** `abc123`。

| 方向 | 能不能做 |
|------|----------|
| `abc123` → `$2b$12$N9qo...` | 能（注册/改密码时） |
| `$2b$12$N9qo...` → `abc123` | **不能** |

- 黑客拖库 → 只能看到 `$2b$12$...`，**读不出** `abc123`
- 管理员查数据库 → 同样**看不到**真实密码
- 代码里也没有 `unhash()` 这种东西

这就是「**拿不回去**」：哈希是**单向**的，像把苹果打成汁——能尝出是不是苹果味，但**不能把汁还原成整颗苹果**。

### 「能验证」

登录时你输入 `abc123`，服务器调用 `verify_password("abc123", 数据库里那串哈希)`。

Bcrypt 内部大致是：

```
1. 从你输入的 abc123 出发
2. 用哈希里自带的「调料」（salt）再算一遍
3. 算出来的结果和库里那串比一比
4. 一样 → 返回 True（密码对）
   不一样 → 返回 False（密码错）
```

| 你输入 | 结果 |
|--------|------|
| `abc123` | 验证通过，发 Token 让你登录 |
| `abc124` | 验证失败，提示密码错误 |

整个过程**不需要**先把 `$2b$12$...` 变回 `abc123`，只需要回答：**「你刚输入的，和当初存的是不是一对？」**

### 完整例子

```
【注册】
你输入：abc123
存进库：$2b$12$k3j8f2a...（乱码）

【登录 - 密码正确】
你输入：abc123
服务器：verify → True → 登录成功
（全程没有出现过「从乱码还原出 abc123」这一步）

【登录 - 密码错误】
你输入：wrong123
服务器：verify → False → 密码错误

【黑客拖库】
看到：$2b$12$k3j8f2a...
拿不到：abc123
```

**一句话：** 「拿不回去」= 乱码没法变回 `abc123`；「能验证」= 你再输入 `abc123` 时，系统能判断「对，就是当初那个密码」，而不需要先把乱码还原。

就像**指纹锁**：锁里存的是指纹模板，不是你的手；你按上去，它只回答「匹配 / 不匹配」，不会「打印出你的手指」。

---

## 动手练习（5 道题）

**环境准备（只需做一次）：**

```powershell
pip install passlib bcrypt
```

练习 2、3 已做成可执行脚本，见 `demo/Bcrypt_demo/`。练习 1、4、5 可复制下方代码到 `.py` 文件运行。

---

### 第 1 题：亲眼看见「密码变成乱码」

**要练会什么：** 明文密码经过 Bcrypt 后会变成一长串乱码，而且**不是**原密码本身。

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

plain = "abc123"
hashed = pwd_context.hash(plain)

print("明文:", plain)
print("哈希:", hashed)
print("明文 == 哈希?", plain == hashed)
print("哈希长度大约:", len(hashed))
```

**预期结果：**

| 检查项 | 应该看到 |
|--------|----------|
| `明文` | `abc123` |
| `哈希` | 以 `$2b$` 开头的一长串 |
| `明文 == 哈希?` | `False` |
| 哈希长度 | 大约 60 字符 |

**再试一次：** 对 `hash("abc123")` 运行两次，两次哈希**应该不一样**——这就是「随机调料（salt）」在起作用。

---

### 第 2 题：练「能验证」——对的上、对不上

**要练会什么：** 用 `verify` 判断密码是否正确，**不需要**把哈希变回明文。

**可执行脚本：** `demo/Bcrypt_demo/exercise2.py`

**运行方式（Windows PowerShell）：**

```powershell
cd demo/Bcrypt_demo
pip install -r requirements.txt
python exercise2.py
```

**预期输出（大致）：**

```
已生成哈希: $2b$12$...
正确密码   'abc123'   -> [PASS] 通过 (期望: 通过)
错一位     'abc124'   -> [PASS] 失败 (期望: 失败)
大小写不同 'ABC123'   -> [PASS] 失败 (期望: 失败)
空密码     ''         -> [PASS] 失败 (期望: 失败)
---
全部测试通过
```

**测试用例预期：**

| 输入 | 预期 |
|------|------|
| `abc123` | 通过 |
| `abc124` | 失败 |
| `ABC123` | 失败 |
| `""` | 失败 |

---

### 第 3 题：模拟「数据库只存哈希」

**要练会什么：** 注册时存哈希、登录时验哈希——理解「库里没有明文密码」。

**可执行脚本：** `demo/Bcrypt_demo/exercise3.py`

**运行方式：**

```powershell
cd demo/Bcrypt_demo
python exercise3.py
```

**预期输出（大致）：**

```
注册成功: 张三
  库里存的是: $2b$12$...
[PASS] 正确密码登录 -> (True, '登录成功')
[PASS] 错误密码登录 -> (False, '密码错误')
[PASS] 不存在用户登录 -> (False, '用户不存在')
[PASS] 数据库中没有明文密码
---
数据库内容: {'张三': '$2b$12$...'}
全部测试通过
```

**一键运行练习 2、3：**

```powershell
python run_all.py
```

---

### 第 4 题：对比「不用 Bcrypt」有多危险

**要练会什么：** 直观感受：明文存库 vs 哈希存库，泄露时长什么样。

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

bad_db = {}   # 明文存库（错误做法）
good_db = {}  # Bcrypt 存库（正确做法）

def bad_register(user, pwd):
    bad_db[user] = pwd

def good_register(user, pwd):
    good_db[user] = pwd_context.hash(pwd)

bad_register("alice", "123456")
bad_register("bob",   "123456")
good_register("alice", "123456")
good_register("bob",   "123456")

print("=== 黑客拖库后看到的内容 ===")
print("明文库 bad_db:")
print(bad_db)
print()
print("哈希库 good_db:")
for user, h in good_db.items():
    print(f"  {user}: {h[:30]}...")
print()
print("两个用户密码相同，明文库:", bad_db["alice"] == bad_db["bob"])
print("两个用户密码相同，哈希库:", good_db["alice"] == good_db["bob"])
```

**预期结果：**

| 检查项 | 预期 |
|--------|------|
| `bad_db` | `{'alice': '123456', 'bob': '123456'}` —— 密码直接可见 |
| `good_db` | 两串都以 `$2b$` 开头的乱码 |
| 明文库两用户相同？ | `True` |
| 哈希库两用户相同？ | `False` |

---

### 第 5 题：迷你综合题（最接近本项目）

**要练会什么：** 串起来练「注册 → 登录 → 改密码 → 旧密码失效 → 新密码生效」，对应 `auth_service.py` 的逻辑。

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users = {}  # username -> {"password_hash": "..."}

def hash_password(plain):
    return pwd_context.hash(plain)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def register(username, password):
    if username in users:
        return False, "用户名已存在"
    users[username] = {"password_hash": hash_password(password)}
    return True, "注册成功"

def login(username, password):
    if username not in users:
        return False, "用户名或密码错误"
    if not verify_password(password, users[username]["password_hash"]):
        return False, "用户名或密码错误"
    return True, "登录成功，发 Token"

def change_password(username, old_password, new_password):
    if username not in users:
        return False, "用户不存在"
    if not verify_password(old_password, users[username]["password_hash"]):
        return False, "原密码错误"
    users[username]["password_hash"] = hash_password(new_password)
    return True, "密码已修改"

# ========== 按顺序跑测试 ==========
assert register("admin", "admin123") == (True, "注册成功")
assert login("admin", "admin123") == (True, "登录成功，发 Token")
assert login("admin", "wrong") == (False, "用户名或密码错误")
assert change_password("admin", "admin123", "newpass456") == (True, "密码已修改")
assert login("admin", "admin123") == (False, "用户名或密码错误")  # 旧密码失效
assert login("admin", "newpass456") == (True, "登录成功，发 Token")  # 新密码生效
assert change_password("admin", "admin123", "xxx") == (False, "原密码错误")

print("全部测试通过")
print("最终库里存的哈希:", users["admin"]["password_hash"][:40], "...")
```

**预期结果：**

| 步骤 | 预期 |
|------|------|
| 注册 `admin` / `admin123` | 成功 |
| 用 `admin123` 登录 | 成功 |
| 用 `wrong` 登录 | 失败 |
| 改密码：旧 `admin123` → 新 `newpass456` | 成功 |
| 再用 `admin123` 登录 | **失败** |
| 用 `newpass456` 登录 | 成功 |
| 改密码时旧密码填错 | `(False, '原密码错误')` |
| 最后打印 | `全部测试通过` |

---

## 练完后对照项目文件

按这个顺序看，和上面练习一一对应：

| 顺序 | 文件 | 对照什么 |
|------|------|----------|
| 1 | `server/app/core/security.py` | 练习 1～2 的 `hash_password` / `verify_password` |
| 2 | `server/app/services/auth_service.py` | 练习 5 的登录、改密码流程 |
| 3 | `server/app/services/user_service.py` | 创建用户、管理员重置密码时的 `hash_password` |
| 4 | `server/app/models/user.py` | `password_hash`、`view_password_hash` 字段 |

**对照关系：**

- 练习里的 `users` 字典 ≈ 数据库 `users` 表
- 练习里的 `hash_password` / `verify_password` ≈ `security.py` 里同名函数
- 练习里的 `login` / `change_password` ≈ `auth_service.py` 里的同名逻辑

练完 5 题再打开 `security.py` 和 `auth_service.py`，你会认出：**「哦，这就是我在练习题里自己写过的那套，只是项目里还多了数据库、JWT、日志。」**

---

## 总结

**Bcrypt 的作用：** 用户注册或改密码时，把真实密码变成「只能验证、不能还原」的乱码存进数据库；登录时再比对输入是否正确，全程不存明文。

**不用 vs 用了：** 不用的话，数据库一泄露就等于所有用户密码裸奔；用了之后，就算库被拖走，黑客拿到的也只是一堆很难猜的乱码，没法直接登录。

**一句话：** Bcrypt 是 Web 项目里保护用户密码的标配做法——本项目已用在登录密码和查看专用密码上；密码本里的网站密码则用 AES 加密，因为那些密码以后还要解密拿出来看。
