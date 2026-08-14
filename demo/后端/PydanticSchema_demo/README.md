# Pydantic Schema 请求校验 -- 动手练习题（第 2、3、5、6 题）

复制粘贴即可运行，每题独立一个脚本，内置自动测试。

## 环境准备（Windows）

```powershell
cd demo\PydanticSchema_demo
pip install -r requirements.txt
```

## 一键运行全部

```powershell
python run_all.py
```

## 逐题运行

| 文件 | 命令 | 练什么 |
|------|------|--------|
| exercise2.py | `python exercise2.py` | 最小 Schema，成功 vs 失败 |
| exercise3.py | `python exercise3.py` | 必填 vs 可选 + 默认值 |
| exercise5.py | `python exercise5.py` | pattern 限制固定取值 |
| exercise6.py | `python exercise6.py` | 读懂 ValidationError 报错 |

## 预期输出（大致）

### exercise2.py

```
[PASS] 测1: 成功 -> title='买牛奶'
[PASS] 测2: 失败 -> Field required
[PASS] 测3: 失败 -> Input should be a valid string
---
3/3 tests passed
```

### exercise3.py

```
[PASS] 创建-只传title: 成功 -> {'title': '购物清单', 'content': '', 'is_pinned': False}
[PASS] 创建-空标题: 失败 -> String should have at least 1 character
[PASS] 创建-啥也不传: 失败 -> Field required
[PASS] 更新-只改置顶: 成功 -> {'title': None, 'is_pinned': True}
[PASS] 更新-空对象: 成功 -> {'title': None, 'is_pinned': None}
---
5/5 tests passed
```

### exercise5.py

```
[PASS] 测1: 成功 -> {'title': '写报告', 'priority': 'high'}
[PASS] 测2: 失败 -> String should match pattern '^(low|medium|high)$'
[PASS] 测3: 成功 -> {'title': '写报告', 'priority': 'medium'}
[PASS] 测4: 失败 -> String should have at least 1 character
---
4/4 tests passed
```

### exercise6.py

```
一共 2 个错误：
  字段: ('ids',)
  原因: List should have at least 1 item after validation, not 0
  传入值: []
  ---
  字段: ('status',)
  原因: String should match pattern '^(pending|completed)$'
  传入值: done
  ---
[PASS] 检测到 2 个校验错误
---
1/1 tests passed
```

## 练完后对照项目文件

| 顺序 | 文件 | 对照什么 |
|------|------|----------|
| 1 | `demo/FastAPI_demo/schemas/todo_schema.py` | 最简 Create / Update / Response |
| 2 | `server/app/schemas/memo.py` | 默认值、Optional、分页 Query |
| 3 | `server/app/schemas/todo.py` | pattern、datetime、批量更新 |
| 4 | `server/app/api/todos.py` | 校验通过后如何进 Service |
