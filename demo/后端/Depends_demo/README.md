# Depends 依赖注入 -- 5 道动手练习题

复制粘贴即可运行，每题独立一个脚本，内置自动测试。

## 环境准备（Windows）

```powershell
cd demo\Depends_demo
pip install -r requirements.txt
```

## 一键运行全部

```powershell
python run_all.py
```

## 逐题运行

| 文件 | 命令 | 练什么 |
|------|------|--------|
| exercise1.py | `python exercise1.py` | 理解「注入」概念（纯 Python） |
| exercise2.py | `python exercise2.py` | Depends 基本格式 |
| exercise3.py | `python exercise3.py` | 链式 Depends + 成功/失败 |
| exercise4.py | `python exercise4.py` | yield 借还（模拟 get_db） |
| exercise5.py | `python exercise5.py` | 迷你综合（db + 登录 + 业务） |

## 预期输出（大致）

### exercise1.py

```
[PASS] morning greeting
[PASS] evening greeting
---
早上好，小明！
晚上好，小红！
```

### exercise2.py

```
[PASS] GET /welcome -> 200 {'message': '欢迎光临'}
---
status=200 body={'message': '欢迎光临'}
```

### exercise3.py

```
[PASS] admin-token -> 200
[PASS] user-token -> 403
[PASS] wrong-token -> 401
[PASS] no token -> 422
---
admin: status=200 body={'ok': True, 'user': {'name': '管理员', 'role': 'admin'}}
user:  status=403 body={'detail': '权限不足'}
wrong: status=401 body={'detail': '无效 token'}
none:  status=422
```

### exercise4.py

```
--- request 1 ---
[get_conn] borrow conn-1, pool left=1
[get_conn] normal finish, return conn-1
[get_conn] returned conn-1, pool size=2
--- request 2 ---
[get_conn] borrow conn-1, pool left=1
[get_conn] normal finish, return conn-1
[get_conn] returned conn-1, pool size=2
[PASS] first request returns conn-1, pool_size=1
[PASS] second request returns conn-2, pool_size=1
[PASS] pool restored after two requests
---
first:  status=200 body={'used': 'conn-1', 'pool_size': 1}
second: status=200 body={'used': 'conn-2', 'pool_size': 1}
pool after tests: ['conn-1', 'conn-2']
```

### exercise5.py

```
[PASS] Bearer token-alice -> 200, 1 memo
[PASS] Bearer token-bob -> 200, 1 memo
[PASS] Bearer wrong -> 401
[PASS] no Authorization -> 401
---
alice: status=200 body={'items': [{'id': 1, 'user_id': 1, 'title': 'Alice 的备忘'}]}
bob:   status=200 body={'items': [{'id': 2, 'user_id': 2, 'title': 'Bob 的备忘'}]}
wrong: status=401 body={'detail': '无效 token'}
none:  status=401 body={'detail': '未登录'}
```

## 可选：启动 Web 服务手动体验

练习 2~5 都内置了 FastAPI app，可以用 uvicorn 启动后在浏览器访问 `/docs`：

```powershell
uvicorn exercise2:app --reload
uvicorn exercise3:app --reload
uvicorn exercise4:app --reload
uvicorn exercise5:app --reload
```

手动测试要点：

- exercise3：请求头 `X-Token` 分别填 `admin-token` / `user-token` / `wrong-token`
- exercise5：请求头 `Authorization` 填 `Bearer token-alice` 或 `Bearer token-bob`

## 加分实验：连接泄漏（exercise4）

1. 打开 `exercise4.py`
2. 注释掉 `finally` 里的 `POOL.append(conn)`
3. 再运行 `python exercise4.py`
4. 第 2 次请求可能还能成功，但连接池会逐渐被借光（真实项目里就是连接泄漏）

## 练完后对照本项目

| 练习题 | 项目真实文件 |
|--------|--------------|
| get_db + yield | `server/app/core/database.py` |
| get_current_user / require_admin | `server/app/core/deps.py` |
| 业务接口写法 | `server/app/api/memos.py` |
| 管理员接口 | `server/app/api/users.py` |
| 多 Depends 混用 | `server/app/api/auth.py` |
| 学习笔记 | `doc/技术学习/Depends_study.md` |
