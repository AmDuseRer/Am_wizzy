# 表单校验（前后端对齐）-- 动手练习题

4 道由浅入深的练习题，复制粘贴即可运行，内置自动测试。
规则与 wizzy 项目 `LoginView.vue` / `auth.py` / `TodoListView.vue` / `todo.py` 对齐。

## 环境准备（Windows）

```powershell
cd demo\表单校验_demo
pip install -r requirements.txt
```

仅需安装 `pydantic`（练习 1、3 的前半段不依赖它，但一键运行需要）。

## 一键运行全部

```powershell
python run_all.py
```

若中文显示乱码，可先执行 `chcp 65001` 再运行（`run_all.py` 已尝试自动切换 UTF-8）。

## 逐题运行

| 文件 | 命令 | 练什么 |
|------|------|--------|
| exercise1.py | `python exercise1.py` | 前端先拦错（模拟 `rules` + `validate()`） |
| exercise2.py | `python exercise2.py` | 后端再复查（`LoginRequest` Schema） |
| exercise3.py | `python exercise3.py` | 规则不对齐的坑 + 修到对齐 |
| exercise4.py | `python exercise4.py` | 完整流程：前端先验 -> 发请求 -> 后端再验 |

## 预期输出（大致）

### exercise1.py

```
[PASS] 测1-正常登录: OK -> 前端放行，可以发请求
[PASS] 测2-用户名为空: BLOCK -> 请输入用户名
[PASS] 测3-用户名太短: BLOCK -> 用户名长度 2-50 字符
[PASS] 测4-密码太短: BLOCK -> 密码长度 6-100 字符
---
4/4 tests passed
```

### exercise2.py

```
[PASS] 测1-正常登录: OK -> username='admin'
[PASS] 测2-用户名为空: 422 -> String should have at least 2 characters
[PASS] 测3-密码太短: 422 -> String should have at least 6 characters
[PASS] 测4-用户名类型错误: 422 -> Input should be a valid string
---
4/4 tests passed
```

### exercise3.py

```
阶段 A：前后端不对齐（前端 max=500，后端 max=200）
[PASS] 300字标题: 前端=OK, 后端=标题长度 1-200
       -> 用户困惑：网页没报错，一提交服务器却拒绝

阶段 B：前后端对齐（前端 max=200，后端 max=200）
[PASS] 测1-空标题: 前端=请输入标题, 后端=标题长度 1-200
[PASS] 测2-正常标题: 前端=OK, 后端=OK
[PASS] 测3-200字边界: 前端=OK, 后端=OK
[PASS] 测4-201字超长: 前端=标题不能超过 200 字, 后端=标题长度 1-200
---
5/5 checks passed
```

### exercise4.py

```
[PASS] 正常登录: stage=backend, token=fake-token-for-admin
[PASS] 密码太短: stage=frontend, messages=['密码长度 6-100 字符']
[PASS] 绕过前端直打后端: status=422, 后端仍拒绝
[PASS] 不对齐演示: 前端放行(5字), 后端拒绝 status=422
---
4/4 tests passed
```

### run_all.py

依次输出上述 4 段，最后一行：

```
ALL PASSED: 4/4 exercises
```

## 练完后对照项目文件

| 顺序 | 前端 | 后端 | 对应练习 |
|------|------|------|----------|
| 1 | `web/src/views/LoginView.vue` | `server/app/schemas/auth.py` | 练习 1、2、4 |
| 2 | `web/src/views/TodoListView.vue` | `server/app/schemas/todo.py` | 练习 3 |
| 3 | `web/src/views/MemoListView.vue` | `server/app/schemas/memo.py` | 延伸对照 |
