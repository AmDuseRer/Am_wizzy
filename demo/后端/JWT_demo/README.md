# JWT + Token 白名单 -- 练习 2、3、4

复制粘贴即可运行，内置自动测试。练完可对照项目文件：

- `server/app/core/security.py` -- 签发 / 解析 JWT（练习 2）
- `server/app/models/user.py` -- UserToken 白名单表（练习 3）
- `server/app/services/auth_service.py` -- login / logout（练习 4）
- `server/app/core/deps.py` -- get_current_user（练习 4）

## 环境准备（Windows）

```powershell
cd demo/JWT_demo
pip install -r requirements.txt
```

## 逐题运行

| 文件 | 命令 | 练什么 |
|------|------|--------|
| exercise2.py | `python exercise2.py` | 用密钥签发 JWT、验签、拒绝篡改/过期 |
| exercise3.py | `python exercise3.py` | 字典模拟白名单，revoke 后失效 |
| exercise4.py | `python exercise4.py` | 登录 -> 访问 -> 登出完整流程 |

## 一键运行全部

```powershell
python run_all.py
```

## 预期输出（大致）

### exercise2.py

```
[PASS] 正常 token 验签成功，sub=1, username=zhang.san
  正常 token 验签成功，sub=1, username=zhang.san
[PASS] 篡改 token 后验签失败
[PASS] 过期 token 验签失败
[PASS] 错误密钥验签失败
---
全部测试通过
```

### exercise3.py

```
[PASS] 刚加入白名单 -> True
[PASS] revoke 后 -> False
[PASS] user_id 不匹配 -> False
[PASS] jti 不存在 -> False
---
全部测试通过
```

### exercise4.py

```
[PASS] 正确密码登录成功
[PASS] 错误密码登录失败
[PASS] 登录后 get_current_user 成功
[PASS] 登出后 get_current_user 失败
[PASS] 禁用账号后访问失败
---
全部测试通过
```

### run_all.py

```
==================================================
运行 exercise2.py
==================================================
...（同上）...

==================================================
运行 exercise3.py
==================================================
...（同上）...

==================================================
运行 exercise4.py
==================================================
...（同上）...

==================================================
练习 2、3、4 全部通过
==================================================
```
