# 表单验证（前后端对齐）学习笔记

> 结合本项目（wizzy 小智工具箱）的通俗讲解，面向零基础。  
> 动手练习脚本：`demo/表单校验_demo/`  
> 后端 Schema 详解另见：`doc/技术学习/后端/PydanticSchema_study.md`

---

## 目录

1. [一句话理解](#一句话理解)
2. [表单验证是什么](#表单验证是什么)
3. [前后端对齐是什么](#前后端对齐是什么)
4. [在本项目中的作用](#在本项目中的作用)
5. [不用 vs 用了](#不用-vs-用了)
6. [实质好处（带对比）](#实质好处带对比)
7. [在本项目里怎么写](#在本项目里怎么写)
8. [前端 rules 与后端 Schema 对照表](#前端-rules-与后端-schema-对照表)
9. [完整提交流程（登录为例）](#完整提交流程登录为例)
10. [动手练习（4 道题）](#动手练习4-道题)
11. [可执行练习脚本](#可执行练习脚本)
12. [练完后对照项目文件](#练完后对照项目文件)
13. [自检清单](#自检清单)
14. [总结](#总结)

---

## 一句话理解

**表单验证 = 用户填完表点提交前，先检查内容合不合格；前后端对齐 = 网页上的检查规则和后端服务器的检查规则用同一套标准。前端管体验（立刻提示），后端管安全（绝不轻信浏览器），两边数字要一致。**

---

## 表单验证是什么

用户在网页上填表——登录、新建待办、写备忘录、改密码……填完后点「确定」或「登录」。

**表单验证**就是在真正发请求之前，先回答这些问题：

- 必填项填了吗？
- 长度对不对？（比如密码至少 6 位）
- 格式对不对？（比如角色只能是 admin 或 user）

在本项目里，前端验证主要靠 **Element Plus 的 `<el-form>` + `rules`**：

| 你写的代码 | 干什么 |
|------------|--------|
| `:model="form"` | 表单数据绑在哪里 |
| `:rules="rules"` | 每个字段的检查规则 |
| `prop="username"` | 这一行对应 rules 里的哪个字段 |
| `formRef.value.validate()` | 提交前手动触发检查 |

验证失败时，输入框下方会出现红字提示，**请求不会发出去**。

---

## 前后端对齐是什么

一个完整应用有**两个地方**会检查同一份数据：

| 位置 | 文件类型 | 作用 |
|------|----------|------|
| 前端（浏览器） | `.vue` 里的 `rules` | 立刻提示用户，少发无效请求 |
| 后端（服务器） | `schemas/*.py` 里的 Pydantic Schema | 最后一道防线，防止绕过网页的恶意请求 |

**对齐**的意思是：两边规则一致。例如登录时：

- 用户名都是 **2～50** 字
- 密码都是 **6～100** 字

如果前端允许 500 字标题、后端只收 200 字，用户会遇到：**网页没报错，一提交服务器却拒绝**——这就是「没对齐」的坑。

---

## 在本项目中的作用

小智工具箱里，几乎所有「用户填东西再提交」的功能都用到表单验证：

| 页面/功能 | 前端文件 | 后端 Schema |
|-----------|----------|-------------|
| 登录 | `views/LoginView.vue` | `schemas/auth.py` → `LoginRequest` |
| 修改密码 | `components/ChangePasswordDialog.vue` | `schemas/auth.py` → `ChangePasswordRequest` |
| 查看专用密码 | `components/ViewPasswordDialog.vue` | `schemas/auth.py` → `SetViewPasswordRequest` |
| 用户管理 | `views/UserManageView.vue` | `schemas/user.py` |
| 待办 | `views/TodoListView.vue` | `schemas/todo.py` |
| 备忘录 | `views/MemoListView.vue` | `schemas/memo.py` |
| 密码本 | `views/PasswordListView.vue` | `schemas/password.py` |
| 分类 | `components/CategorySelect.vue`（弹窗 pattern） | `schemas/category.py` |

**不可或缺在哪？**

1. **没有前端验证**：每次填错都要等网络请求，体验差。
2. **没有后端验证**：有人可以绕过网页直接攻击 API，脏数据可能进数据库。
3. **没有对齐**：前端和后端各说各话，用户困惑、排查困难。

---

## 不用 vs 用了

### 场景 A：登录密码只填 3 位

| 不用验证 | 用了验证 |
|----------|----------|
| 点登录 → 转圈等待 → 服务器返回 422 错误 → 用户不知道哪里错 | 光标离开输入框 → 立刻提示「密码长度 6-100 字符」→ 请求根本发不出去 |

### 场景 B：待办标题写了 300 字（后端上限 200）

| 前后端不对齐 | 前后端对齐 |
|--------------|------------|
| 网页认为 OK → 提交 → 服务器拒绝 → 用户懵 | 网页和后端都拒绝 → 用户立刻知道「标题太长」 |

### 场景 C：有人用工具绕过网页，直接发乱数据给 API

| 只有前端验证 | 前后端都有验证 |
|--------------|----------------|
| 攻击者直接 POST 空标题 → 可能写进数据库或程序崩溃 | 后端 Schema 拦在业务代码之前 → 返回 422，数据库安全 |

---

## 实质好处（带对比）

### 好处 1：用户立刻知道错在哪

- **不用**：填错 → 等网络 → 看报错 → 猜问题
- **用了**：填错 → 输入框下面马上红字，如「请输入用户名」

### 好处 2：少发无效请求，页面更流畅

- **不用**：每次乱填都打到服务器
- **用了**：`validate()` 不过就不调用 `authStore.login()` 等接口

### 好处 3：前后端说同一种「语言」

- **不用**：前端允许 500 字标题，后端只收 200 字
- **用了**：`LoginView.vue` 的 `rules` 与 `auth.py` 的 `LoginRequest` 数字一一对应

### 好处 4：后端是最后一道防线

- **不用**：坏人绕过网页直接发 `{ "title": "" }`
- **用了**：FastAPI + Pydantic 在 `create_todo()` 之前就拒绝

### 好处 5：改规则有章可循

- **不用**：「用户名最少几位？」要翻多处代码
- **用了**：看前端 `rules` + 后端 Schema，对照改即可

---

## 在本项目里怎么写

### 标准三步（以登录页为例）

**第 1 步：template 绑表单**

```html
<el-form ref="formRef" :model="form" :rules="rules">
  <el-form-item prop="username">
    <el-input v-model="form.username" />
  </el-form-item>
  <el-form-item prop="password">
    <el-input v-model="form.password" type="password" />
  </el-form-item>
</el-form>
```

**第 2 步：script 写 rules（与后端对齐）**

```javascript
/** 表单校验规则（与后端 Pydantic 对齐） */
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度 2-50 字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 100, message: '密码长度 6-100 字符', trigger: 'blur' },
  ],
}
```

**第 3 步：提交前先 validate()**

```javascript
async function handleLogin() {
  await formRef.value.validate()   // 不过会抛错，下面的代码不执行
  await authStore.login(form)      // 只发合格的数据
}
```

### 常见 rules 写法

| 规则 | 写法 | 对应后端 |
|------|------|----------|
| 必填 | `{ required: true, message: '...', trigger: 'blur' }` | `Field(...)` |
| 长度 | `{ min: 2, max: 50, message: '...', trigger: 'blur' }` | `min_length=2, max_length=50` |
| 下拉固定值 | 用 `<el-select>` 限制选项 | `pattern="^(admin\|user)$"` |
| 两次密码一致 | `{ validator: validateConfirm, trigger: 'blur' }` | **仅前端**，不发给后端 |

### 「仅前端」的字段（正常设计）

改密码、新增密码等表单里有 **确认密码** 字段：

- 前端：`confirm_password` —— 检查两次输入是否一致
- 后端：Schema 里**没有**这个字段 —— 提交时 `delete data.confirm_password`，只发最终密码

这不是 bug，是刻意设计：**确认框只为防手滑，后端不需要知道「你确认了几遍」。**

---

## 前端 rules 与后端 Schema 对照表

### 登录（完全对齐 —— 最佳样板）

| 字段 | 前端 `LoginView.vue` | 后端 `LoginRequest` |
|------|----------------------|------------------------|
| username | 必填，2～50 | `min_length=2, max_length=50` |
| password | 必填，6～100 | `min_length=6, max_length=100` |

### 修改密码

| 字段 | 前端 | 后端 `ChangePasswordRequest` |
|------|------|------------------------------|
| old_password | 必填，6～100 | `min_length=6, max_length=100` |
| new_password | 必填，6～100 | `min_length=6, max_length=100` |
| confirm_password | 必填 + 一致 | 无（仅前端） |

### 待办

| 字段 | 前端 `TodoListView.vue` | 后端 `TodoCreateRequest` |
|------|-------------------------|--------------------------|
| title | 必填，1～200 | `min_length=1, max_length=200` |
| priority | 必填（下拉） | `pattern="^(low\|medium\|high)$"` |
| status | 必填（下拉） | `pattern="^(pending\|...)$"` |
| description | **无 rules** | 默认 `""`，最长 **5000** |

> description 属于「前端少验、后端仍会拦」——安全没问题，体验略差。

### 备忘录

| 字段 | 前端 `MemoListView.vue` | 后端 `MemoCreateRequest` |
|------|-------------------------|--------------------------|
| title | 必填，1～200 | `min_length=1, max_length=200` |
| content | 最长 10000 | `max_length=10000`，默认 `""` |

### 密码本

| 字段 | 前端 `PasswordListView.vue` | 后端 `PasswordCreateRequest` |
|------|----------------------------|------------------------------|
| site_name | 必填，1～200 | `min_length=1, max_length=200` |
| password | 必填，1～500 | `min_length=1, max_length=500` |
| username / url / remark | **无 rules** | 后端有长度上限 |

### 分类（特殊：用弹窗 pattern，不是 el-form rules）

| 字段 | 前端 `CategorySelect.vue` | 后端 `CategoryCreateRequest` |
|------|---------------------------|------------------------------|
| name | `inputPattern: /^.{1,100}$/` | `min_length=1, max_length=100` |

### 总览

```
功能              前端 rules          后端 Schema           对齐情况
─────────────────────────────────────────────────────────────────
登录              LoginView         LoginRequest          完全对齐
改密码            ChangePassword    ChangePasswordRequest 对齐 + 确认框仅前端
查看专用密码      ViewPassword      SetViewPassword       对齐 + 确认框仅前端
新增用户          UserManage        UserCreateRequest     完全对齐
重置密码          UserManage        UserResetPassword     完全对齐
待办              TodoList          TodoCreateRequest     主字段对齐 / description 前端少验
备忘录            MemoList          MemoCreateRequest     title + content 对齐
密码本            PasswordList      PasswordCreateRequest 主字段对齐 / 网址备注等前端少验
分类              CategorySelect    CategoryCreateRequest 名称 1-100 对齐
```

---

## 完整提交流程（登录为例）

```
用户在 LoginView 输入账号密码
        │
        ▼
点击「登录」→ handleLogin()
        │
        ▼
formRef.validate()  ──失败──► 输入框红字，结束（不发请求）
        │
       通过
        │
        ▼
authStore.login(form)  →  POST /api/auth/login  →  JSON 到后端
        │
        ▼
FastAPI 用 LoginRequest 自动校验  ──失败──► HTTP 422
        │
       通过
        │
        ▼
业务逻辑验账号密码  →  返回 token  →  前端跳转首页
```

对应代码位置：

- 前端验证：`web/src/views/LoginView.vue` 第 57～70 行
- 后端 Schema：`server/app/schemas/auth.py` 第 9～13 行
- 发请求：`web/src/stores/auth.js` 里的 `login()`

---

## 动手练习（4 道题）

> 完整可运行代码见 [`demo/表单校验_demo/`](../../../demo/表单校验_demo/README.md)

### 第 1 题 · 模拟「前端校验」

**要练会什么：** 用户点提交之前，网页先检查一遍。

**环境：** Python（`demo/表单校验_demo/exercise1.py`）

**测试数据：**

| 用户名 | 密码 | 预期 |
|--------|------|------|
| admin | Admin@123 | 通过 |
| （空） | Admin@123 | 失败：请输入用户名 |
| a | Admin@123 | 失败：用户名长度 |
| admin | 123 | 失败：密码长度 |

---

### 第 2 题 · 模拟「后端校验」

**要练会什么：** 数据到服务器门口再查一遍；绕过网页也会被拦。

**环境：** Python + pydantic（`exercise2.py`）

**测试数据：**

| 数据 | 预期 |
|------|------|
| 正常登录 JSON | 通过 |
| username 为空 | 422 |
| password 只有 5 位 | 422 |
| username 传数字 123 | 422（类型错误） |

---

### 第 3 题 · 不对齐 vs 对齐

**要练会什么：** 前端 max=500、后端 max=200 时，300 字标题「前端 OK、后端拒绝」；改成都是 200 后两边一致。

**环境：** `exercise3.py`

**关键测试：** 标题 `"A" * 300` —— 不对齐时前端放行、后端拒绝；对齐后都拒绝。

---

### 第 4 题 · 迷你综合题

**要练会什么：** 串起来 `submit_login()` = 前端先验 → 通过才调 `backend_login()`。

**环境：** `exercise4.py`

**测试场景：**

| 场景 | 预期 |
|------|------|
| 正常登录 | stage=backend，返回 token |
| 密码太短 | stage=frontend，无 token |
| 绕过前端直打后端 | status=422 |
| 前端 4 字、后端 6 字（不对齐演示） | 前端过、后端挂 |

---

## 可执行练习脚本

### 环境准备（Windows）

```powershell
cd demo\表单校验_demo
pip install -r requirements.txt
```

### 一键运行

```powershell
python run_all.py
```

若中文乱码，先执行 `chcp 65001`（`run_all.py` 已尝试自动切换 UTF-8）。

### 逐题运行

| 文件 | 命令 | 练什么 |
|------|------|--------|
| exercise1.py | `python exercise1.py` | 前端先拦错 |
| exercise2.py | `python exercise2.py` | 后端 Schema |
| exercise3.py | `python exercise3.py` | 不对齐 vs 对齐 |
| exercise4.py | `python exercise4.py` | 完整流程 |

### 预期输出（大致）

全部通过时：

```
============================================================
练习 4 - 迷你综合（前端先验 + 后端再验）
============================================================
[PASS] 正常登录: stage=backend, token=fake-token-for-admin
[PASS] 密码太短: stage=frontend, messages=['密码长度 6-100 字符']
[PASS] 绕过前端直打后端: status=422, 后端仍拒绝
---
4/4 tests passed

ALL PASSED: 4/4 exercises
```

---

## 练完后对照项目文件

### 建议阅读顺序

`LoginView.vue`（最简、注释写明对齐） → `auth.py`（后端 LoginRequest） → `TodoListView.vue` + `todo.py`（列表页表单） → `MemoListView.vue` + `memo.py`（延伸） → `ChangePasswordDialog.vue`（确认密码仅前端）

### 文件与知识点对照

| 打开的文件 | 对照什么 |
|------------|----------|
| `web/src/views/LoginView.vue` | `:rules`、`validate()`、与后端对齐的注释 |
| `server/app/schemas/auth.py` | `LoginRequest`、`ChangePasswordRequest` |
| `web/src/views/TodoListView.vue` | 列表页弹窗表单 rules |
| `server/app/schemas/todo.py` | `TodoCreateRequest` 字段规则 |
| `web/src/views/MemoListView.vue` | title + content 长度校验 |
| `server/app/schemas/memo.py` | `MemoCreateRequest` |
| `web/src/components/ChangePasswordDialog.vue` | 确认密码 validator、提交时只发两个字段 |
| `web/src/views/PasswordListView.vue` | 编辑时密码可留空、`delete confirm_password` |
| `web/src/components/CategorySelect.vue` | 非 el-form 的 inputPattern 校验 |
| `demo/表单校验_demo/run_all.py` | 4 道练习的可运行版 |
| `doc/技术学习/后端/PydanticSchema_study.md` | 后端 Schema 深入 |

### 练习与项目对照

| 练习 | 项目文件 |
|------|----------|
| 1、2、4 | `LoginView.vue` + `auth.py` |
| 3 | `TodoListView.vue` + `todo.py` |
| 延伸 | `MemoListView.vue` + `memo.py` |

---

## 自检清单

- [ ] 能说出：前端验证管体验，后端验证管安全
- [ ] 能说出：`rules` 写在 `.vue` 的 script，`Schema` 写在 `server/app/schemas/`
- [ ] 能说出：提交前必须 `await formRef.value.validate()`
- [ ] 能说出：`confirm_password` 为什么不在后端 Schema 里
- [ ] 打开 `LoginView.vue` 和 `auth.py`，能找到 username/password 的长度规则并确认一致
- [ ] 能解释：「前端少验」和「没对齐」有什么区别（前者后端仍兜底，后者两边标准矛盾）
- [ ] 跑通 `demo/表单校验_demo/run_all.py`，看到 `ALL PASSED: 4/4 exercises`

---

## 总结

**表单验证（前后端对齐）**就是：网页和服务器用同一套填表规矩——用户在 `<el-form>` 里填完，`rules` 先帮他在本地纠错；合格的数据才通过 API 发到后端，再由 Pydantic Schema 做最后一道检查。

对本项目来说，登录、待办、备忘录、改密码等表单都遵循这个模式；`LoginView.vue` 与 `auth.py` 是最清晰的对照样板。初学记住三句：**前端管体验，后端管安全，两边数字要一致。** 动手练完 `demo/表单校验_demo/` 后，并排打开 `LoginView.vue` 和 `auth.py`，你会认出练习里的 `validate_login` 就是 `rules`，`LoginRequest` 就是后端的入境检查表。
