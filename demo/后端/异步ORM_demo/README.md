# SQLAlchemy 2.x 异步 ORM -- 4 道动手练习题

复制粘贴即可运行，每题独立一个脚本，内置自动测试。

## 环境准备（Windows）

```powershell
cd demo\异步ORM_demo
pip install -r requirements.txt
```

## 一键运行全部

```powershell
python run_all.py
```

## 逐题运行

| 文件 | 命令 | 练什么 |
|------|------|--------|
| exercise1.py | `python exercise1.py` | create_async_engine + await |
| exercise2.py | `python exercise2.py` | ORM 模型 + insert/select |
| exercise3.py | `python exercise3.py` | 筛选 + 分页 + count |
| exercise4.py | `python exercise4.py` | get_db 风格 commit/rollback |

## 预期输出（大致）

### exercise1.py

```
202x-xx-xx ... INFO sqlalchemy.engine.Engine SELECT 1 AS n
202x-xx-xx ... INFO sqlalchemy.engine.Engine [generated in ...] ()
查询结果: 1
漏写 await 时得到 coroutine 对象，而不是查询结果
[PASS] query returns 1
[PASS] missing await detected
---
```

### exercise2.py

```
[PASS] insert and select
[PASS] commit required
---
1 买菜 鸡蛋、牛奶
```

### exercise3.py

```
[PASS] page 1 titles
[PASS] page 2 titles
[PASS] keyword filter
[PASS] empty keyword
---
page1: ['临时备忘', '学习笔记'] total=4
page2: ['购物清单', '周末计划'] total=4
keyword: ['购物清单'] total=1
empty: [] total=0
```

### exercise4.py

```
[PASS] scenario A committed
[PASS] scenario B rolled back
---
场景 A: 找到 title=A
场景 B: 未找到 title=B (回滚生效)
```

### run_all.py

四题依次输出 `[PASS]`，最后一行：

```
ALL PASSED: 4/4 exercises
```

## 练完后对照项目文件

| 练到的能力 | 项目文件 |
|-----------|----------|
| 异步引擎、Session、get_db | `server/app/core/database.py` |
| ORM 模型定义 | `server/app/models/memo.py` |
| select / 筛选 / 分页 | `server/app/services/memo_service.py` |
| 接口注入 db | `server/app/api/memos.py` |
