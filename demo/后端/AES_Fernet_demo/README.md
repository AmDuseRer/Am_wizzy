# AES/Fernet 对称加密 -- 练习 1、2

复制粘贴即可运行，内置自动测试。练完可对照项目文件：

- `server/app/core/security.py` -- get_fernet / aes_encrypt / aes_decrypt / mask_password
- `server/app/services/password_service.py` -- create_password / list_passwords / reveal_password
- `server/app/core/config.py` + `server/.env.example` -- AES_KEY 配置
- `server/app/models/password_entry.py` -- password_enc 字段

## 环境准备（Windows）

```powershell
cd demo/AES_Fernet_demo
pip install -r requirements.txt
```

## 逐题运行

| 文件 | 命令 | 练什么 |
|------|------|--------|
| exercise1.py | `python exercise1.py` | 同钥加解密；错钥、改密文、空密钥应失败 |
| exercise2.py | `python exercise2.py` | 迷你密码本：存密文 / 列表脱敏 / 验证后查看 |

## 一键运行全部

```powershell
python run_all.py
```

## 预期输出（大致）

### exercise1.py

```
密文开头: gAAAAA...
解密结果: 'GitHubPass123'
[PASS] 用错误密钥解密 — 正确失败
[PASS] 篡改密文后解密 — 正确失败
[PASS] 空密钥 — 正确失败
---
全部测试通过
```

### exercise2.py

```
[PASS] 库里不是明文
[PASS] 列表只显示脱敏
[PASS] 验证通过后看到明文: 'GitHubPass123'
[PASS] 错误查看密码被拦住
[PASS] 换密钥后解密失败
---
全部测试通过 — 你已经摸到了项目里密码本的完整流程
```

## 练习与项目对照

| 练习 | 对照文件 |
|------|----------|
| 练习 1 | `server/app/core/security.py` |
| 练习 2 | `server/app/services/password_service.py` |
| 配置 | `server/app/core/config.py` + `server/.env.example` |
| 数据模型 | `server/app/models/password_entry.py` |
