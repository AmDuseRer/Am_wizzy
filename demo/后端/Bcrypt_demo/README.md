# Bcrypt 密码哈希 -- 练习 2、3

复制粘贴即可运行，内置自动测试。练完可对照项目文件：

- `server/app/core/security.py` -- hash_password / verify_password
- `server/app/services/auth_service.py` -- 登录、改密码流程

## 环境准备（Windows）

```powershell
cd demo/Bcrypt_demo
pip install -r requirements.txt
```

## 逐题运行

| 文件 | 命令 | 练什么 |
|------|------|--------|
| exercise2.py | `python exercise2.py` | 用 verify 判断密码对错 |
| exercise3.py | `python exercise3.py` | 注册存哈希、登录验哈希 |

## 一键运行全部

```powershell
python run_all.py
```

## 预期输出（大致）

### exercise2.py

```
已生成哈希: $2b$12$...
正确密码   'abc123'   -> [PASS] 通过 (期望: 通过)
错一位     'abc124'   -> [PASS] 失败 (期望: 失败)
大小写不同 'ABC123'   -> [PASS] 失败 (期望: 失败)
空密码     ''         -> [PASS] 失败 (期望: 失败)
---
全部测试通过
```

### exercise3.py

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
