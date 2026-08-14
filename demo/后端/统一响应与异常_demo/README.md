# 统一响应与异常 -- 动手练习题（第 3、4 题）

复制粘贴即可运行，内置自动测试。

## 环境准备（Windows）

```powershell
cd demo\统一响应与异常_demo
```

- 第 3 题：Python 3.8+（无需额外 pip 安装）
- 第 4 题：Node.js（`node --version` 能输出版本号即可）

## 逐题运行

| 文件 | 命令 | 练什么 |
|------|------|--------|
| exercise3.py | `python exercise3.py` | BusinessException + 统一 JSON |
| exercise4.js | `node exercise4.js` | 前端响应拦截器（code !== 0） |

## 一键运行 Python 题

```powershell
python run_all.py
```

第 4 题需单独运行：`node exercise4.js`

## 预期输出（大致）

### exercise3.py

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

### exercise4.js

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

## 练完后对照项目文件

| 练习题 | 项目里对照 |
|--------|-----------|
| exercise3.py | `server/app/core/exceptions.py`、`server/app/services/memo_service.py` |
| exercise4.js | `web/src/utils/request.js` |
