# Element Plus 组件库学习笔记

> 结合本项目（wizzy 小智工具箱）的通俗讲解，面向零基础。

---

## 目录

1. [一句话理解](#一句话理解)
2. [Element Plus 是什么](#element-plus-是什么)
3. [在本项目中的作用](#在本项目中的作用)
4. [不用 vs 用了](#不用-vs-用了)
5. [实质好处（带对比）](#实质好处带对比)
6. [代码写在哪（三层位置）](#代码写在哪三层位置)
7. [在本项目里具体怎么用](#在本项目里具体怎么用)
8. [本项目常用组件速查](#本项目常用组件速查)
9. [典型页面长什么样](#典型页面长什么样)
10. [对照项目文件](#对照项目文件)
11. [总结](#总结)

---

## 一句话理解

**Element Plus 是一套现成的网页界面零件（按钮、表格、输入框、弹窗、菜单……），别人已经做好样式和基本交互，你直接拿来拼页面；本项目几乎所有可见界面都靠它搭起来，让你专注写「查数据、存数据」的业务逻辑，而不是从零画界面。**

---

## Element Plus 是什么

做一个网站，页面里总要有很多**重复出现的东西**：

- 登录框、输入框、按钮
- 左侧菜单、顶栏
- 数据表格、分页
- 新增/编辑时的弹窗
- 「保存成功」「确定删除吗？」这类提示

如果每个都自己用 HTML + CSS 从零写，**又慢、又难统一、还容易漏细节**（比如删除前忘记确认）。

**Element Plus** 就是为 Vue 3 准备的一套 **UI 组件库**：  
把上面这些常见界面元素做成**可直接使用的组件**，标签名一般以 `el-` 开头，例如：

| 你写的标签 | 实际是什么 |
|------------|------------|
| `<el-button>` | 按钮 |
| `<el-input>` | 输入框 |
| `<el-table>` | 表格 |
| `<el-dialog>` | 弹窗 |
| `<el-menu>` | 菜单 |

可以把它想成**装修好的家具**：桌子、椅子、柜子都现成的，你只需要按房间功能摆好，不用自己砍木头做家具。

---

## 在本项目中的作用

小智工具箱是一个**需要登录的后台管理类应用**（用户管理、备忘录、密码本、待办）。Element Plus 在这里负责**整个前端界面的「骨架和外观」**。

### 1. 全局安装：一次接入，全站可用

在 `web/src/main.js` 里引入样式、中文语言包，并注册到 Vue：

```javascript
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

app.use(ElementPlus, { locale: zhCn })
```

同时还配合了**暗色模式**（顶栏开关切换时，给 `<html>` 加 `dark` class）。

### 2. 各页面「拼界面」

| 页面/功能 | 文件 | Element Plus 提供的零件 |
|-----------|------|-------------------------|
| 登录 | `views/LoginView.vue` | 卡片、表单、输入框、登录按钮、校验 |
| 主布局 | `layouts/MainLayout.vue` | 侧边栏菜单、顶栏、折叠按钮、暗色开关、下拉菜单 |
| 用户管理 | `views/UserManageView.vue` | 表格、分页、弹窗表单、标签、开关 |
| 待办列表 | `views/TodoListView.vue` | 搜索区、表格多选、日期选择、标签、提示 |
| 密码本 | `views/PasswordListView.vue` | 表格、工具提示、弹窗表单 |
| 备忘录 | `views/MemoListView.vue` | 同上类列表页模式 |

### 3. 全局反馈：提示和确认

不只在页面里用组件，还在 JS 里调用**消息工具**：

| 工具 | 干什么 | 用在哪里 |
|------|--------|----------|
| `ElMessage.success()` | 右上角绿色成功提示 | 保存成功、删除成功 |
| `ElMessage.error()` | 红色错误提示 | `utils/request.js` 请求失败时 |
| `ElMessageBox.confirm()` | 「确定删除吗？」确认框 | 删除用户、待办等危险操作前 |

**不可或缺在哪？** 没有 Element Plus，现有登录页、布局、四个业务列表页和多个弹窗组件几乎都要重写；界面风格也会从「一套完整产品」退化成「各自为政的拼凑页」。

---

## 不用 vs 用了

### 场景 A：做登录页

| 不用 Element Plus | 用了 Element Plus |
|-------------------|-------------------|
| 自己写 HTML + CSS 做输入框、按钮，可能要几十行样式才像样 | `<el-card>` + `<el-form>` + `<el-input>` + `<el-button>`，几行就能拼出完整登录页 |
| 表单校验要自己写逻辑和错误展示 | `<el-form :rules="rules">` 内置校验，不填或格式错会自动提示 |

### 场景 B：做用户/待办/密码列表页

| 不用 | 用了 |
|------|------|
| 表格、分页、加载动画、斑马纹都要自己实现，一个列表页可能几百行 | `<el-table>` + `<el-pagination>` + `v-loading`，主要精力写「查什么、删什么」 |
| 各页面表格边框、行高、按钮样式容易不一致 | 全站 `<el-button>`、`<el-table>` 风格自动统一 |

### 场景 C：新增 / 编辑数据

| 不用 | 用了 |
|------|------|
| 自己写弹层、遮罩、关闭逻辑 | `<el-dialog v-model="dialogVisible">` 一行控制显示隐藏 |
| 下拉、日期、开关各写各的 | `<el-select>`、`<el-date-picker>`、`<el-switch>` 直接绑定 `v-model` |

### 场景 D：删除操作

| 不用 | 用了 |
|------|------|
| 可能忘记做确认，用户一点就删了 | `ElMessageBox.confirm('确定删除？')` 删前必弹确认 |
| 删完没反馈，用户不知道成没成功 | `ElMessage.success('删除成功')` 右上角自动提示 |

### 场景 E：请求报错

| 不用 | 用了 |
|------|------|
| 每个 API 调用处自己写 `alert` 或手写提示条 | `request.js` 里统一 `ElMessage.error(...)`，一处处理全站报错样式 |

### 场景 F：中文与暗色模式

| 不用 | 用了 |
|------|------|
| 日期选择器、分页可能是英文，要自己翻译 | `main.js` 配置 `locale: zhCn`，界面文案是中文 |
| 暗色模式要逐个组件改颜色 | 引入暗色主题 CSS + 顶栏 `el-switch`，切换后全局生效 |

---

## 实质好处（带对比）

### 好处一：省时间 —— 不用重复造轮子

| 不用 | 用了 |
|------|------|
| 每个页面自己画按钮、表格、弹窗，一个管理后台可能要几周 | 待办页：搜索区 + 表格 + 分页 + 编辑弹窗，界面零件直接拼，主要写业务逻辑 |

### 好处二：界面统一 —— 看起来像正经软件

| 不用 | 用了 |
|------|------|
| 登录按钮蓝色、用户页绿色、表格粗细不一，像拼凑的 | 登录、用户管理、密码本、待办，按钮/表格/标签颜色风格一致 |

### 好处三：交互细节现成 —— 少踩坑

| 不用 | 用了 |
|------|------|
| 密码显示隐藏、表格多选、加载状态、表单校验都要自己实现 | `show-password`、`type="selection"`、`v-loading="loading"`、`:rules="rules"` 开箱即用 |

### 好处四：和 Vue 3 配合自然

| 不用 | 用了 |
|------|------|
| 自写组件和数据绑定可能要额外对接 | `<el-input v-model="form.username">` 和 Vue 写法一致，改数据界面自动更新 |

### 好处五：本项目已深度依赖 —— 换掉成本很高

| 不用 | 用了 |
|------|------|
| 要重写登录、布局、4 个业务页、多个弹窗，以及 `request.js` 里的错误提示 | 现有代码直接运行，新功能继续加 `<el-xxx>` 即可 |

---

## 代码写在哪（三层位置）

Element Plus **不是**全部写在同一个文件里，分三层理解：

| 做什么 | 写在哪 | 例子 |
|--------|--------|------|
| **安装**（全局注册 + 样式 + 语言） | `web/src/main.js` | `app.use(ElementPlus, { locale: zhCn })` |
| **拼界面**（模板里的组件） | 各 `.vue` 的 `<template>` | `<el-table>`、`<el-button>`、`<el-dialog>` |
| **调工具**（JS 里弹提示/确认） | 各 `.vue` 的 `<script setup>` 或 `.js` | `ElMessage.success(...)`、`ElMessageBox.confirm(...)` |

依赖声明在 `web/package.json`：

```json
"element-plus": "^2.9.1"
```

图标单独来自 `@element-plus/icons-vue`（如 `MainLayout.vue` 里的 `User`、`Lock` 等）。

---

## 在本项目里具体怎么用

### 第 1 步：main.js 全局安装（只做一次）

```javascript
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

app.use(ElementPlus, { locale: zhCn })
```

### 第 2 步：在 .vue 模板里写组件

**登录页（LoginView.vue）—— 最简表单：**

```html
<el-card class="login-card">
  <el-form ref="formRef" :model="form" :rules="rules">
    <el-form-item prop="username">
      <el-input v-model="form.username" placeholder="用户名" />
    </el-form-item>
    <el-form-item prop="password">
      <el-input v-model="form.password" type="password" show-password />
    </el-form-item>
    <el-button type="primary" :loading="loading" @click="handleLogin">登录</el-button>
  </el-form>
</el-card>
```

**列表页通用模式 —— 表格 + 分页 + 加载：**

```html
<el-table :data="users" v-loading="loading" stripe border>
  <el-table-column prop="username" label="用户名" />
  <!-- 更多列... -->
</el-table>

<el-pagination
  v-model:current-page="page"
  v-model:page-size="pageSize"
  :total="total"
  @current-change="loadData"
/>
```

**编辑弹窗：**

```html
<el-dialog v-model="dialogVisible" title="编辑用户" width="420px">
  <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
    <el-form-item label="用户名" prop="username">
      <el-input v-model="form.username" />
    </el-form-item>
  </el-form>
  <template #footer>
    <el-button @click="dialogVisible = false">取消</el-button>
    <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
  </template>
</el-dialog>
```

### 第 3 步：在 script 里调消息工具

```javascript
import { ElMessage, ElMessageBox } from 'element-plus'

// 成功提示
ElMessage.success('操作成功')

// 删除前确认
await ElMessageBox.confirm(`确定删除用户 ${row.username}？`, '警告', { type: 'warning' })
ElMessage.success('删除成功')
```

**在普通 JS 里也能用（request.js）：**

```javascript
import { ElMessage } from 'element-plus'

if (res.code !== 0) {
  ElMessage.error(res.message || '请求失败')
}
```

### 第 4 步：暗色模式（与 appStore 配合）

顶栏 `el-switch` 切换 → `appStore.darkMode` 变化 → 给 `<html>` 加/去 `dark` class → Element Plus 暗色 CSS 变量生效。

`PageHeader.vue` 等自定义样式也会用 Element Plus 提供的颜色变量，例如：

```css
color: var(--el-text-color-primary);
```

---

## 本项目常用组件速查

| 组件 | 常见用途 | 出现位置举例 |
|------|----------|--------------|
| `el-container` / `el-aside` / `el-header` / `el-main` | 整体布局 | `MainLayout.vue` |
| `el-menu` / `el-menu-item` / `el-sub-menu` | 左侧导航 | `MainLayout.vue` |
| `el-button` | 各种操作按钮 | 所有列表页 |
| `el-table` / `el-table-column` | 数据列表 | 用户、待办、密码、备忘录 |
| `el-pagination` | 分页 | 所有列表页 |
| `el-form` / `el-form-item` | 表单结构与校验 | 登录、弹窗编辑 |
| `el-input` | 文本/密码/多行输入 | 登录、搜索、表单 |
| `el-select` / `el-option` | 下拉选择 | 角色、状态、优先级筛选 |
| `el-dialog` | 弹窗 | 新增/编辑/重置密码 |
| `el-tag` | 状态标签（启用/禁用、优先级等） | 表格列 |
| `el-switch` | 开关（暗色模式、用户启用状态） | 布局顶栏、用户编辑 |
| `el-date-picker` | 日期时间选择 | 待办截止时间 |
| `el-card` | 卡片容器 | 登录页、搜索区 |
| `el-tooltip` | 鼠标悬停显示完整内容 | 长备注、长描述 |
| `el-dropdown` | 顶栏用户菜单 | `MainLayout.vue` |
| `el-icon` | 图标容器 | 菜单、按钮内图标 |
| `ElMessage` | 轻提示（成功/失败） | 各页面 + `request.js` |
| `ElMessageBox` | 确认对话框 | 删除等危险操作 |

---

## 典型页面长什么样

以**用户管理页**为例，Element Plus 零件如何分工：

```
PageHeader（自定义） + el-button「新增用户」
        ↓
el-table 展示用户列表（v-loading 加载中）
  ├── el-tag 显示角色、状态
  └── el-button link 编辑 / 重置密码 / 删除
        ↓
el-pagination 翻页
        ↓
el-dialog + el-form 新增/编辑用户
  ├── el-input 用户名、密码
  ├── el-select 角色
  └── el-switch 启用/禁用
        ↓
脚本里：ElMessageBox.confirm 删前确认 → ElMessage.success 操作成功
```

**主布局（MainLayout.vue）** 则是：

```
el-container
  ├── el-aside + el-menu（左侧菜单 + 图标）
  └── el-container
        ├── el-header（折叠按钮 + 暗色开关 + el-dropdown 用户菜单）
        └── el-main（<router-view> 子页面内容）
```

---

## 对照项目文件

### 建议阅读顺序

`main.js`（安装与中文/暗色） → `LoginView.vue`（最简表单） → `MainLayout.vue`（布局与菜单） → `UserManageView.vue`（表格+弹窗+消息完整范例） → `TodoListView.vue`（搜索+多选+日期） → `utils/request.js`（全局错误提示）

### 文件与知识点对照

| 打开的文件 | 对照什么 |
|------------|----------|
| `web/src/main.js` | 全局 `app.use(ElementPlus)`、中文 `zhCn`、暗色 CSS |
| `web/package.json` | 依赖版本 `element-plus` |
| `web/src/views/LoginView.vue` | `el-card`、`el-form`、`:rules`、`ElMessage` |
| `web/src/layouts/MainLayout.vue` | 布局组件、菜单、图标、`el-switch` 暗色 |
| `web/src/views/UserManageView.vue` | 表格、分页、弹窗、`ElMessageBox.confirm` |
| `web/src/views/TodoListView.vue` | 搜索表单、`el-date-picker`、表格多选、`el-tooltip` |
| `web/src/views/PasswordListView.vue` | 复杂表单、密码显示切换 |
| `web/src/utils/request.js` | 非页面场景使用 `ElMessage.error` |
| `web/src/components/PageHeader.vue` | 自定义组件使用 `--el-*` 主题变量 |

### 自检清单

- [ ] 能说出 Element Plus = 现成的界面零件库，标签以 `el-` 开头
- [ ] 能说出安装写在 `main.js`，使用写在各 `.vue` 的 template 和 script
- [ ] 能区分 `ElMessage`（轻提示）和 `ElMessageBox`（确认框）
- [ ] 能说出列表页常见组合：`<el-table>` + `<el-pagination>` + `<el-dialog>`
- [ ] 打开 `UserManageView.vue`，能找到表格、弹窗、删除确认三处 Element Plus 用法

---

## 总结

**Element Plus** 是为 Vue 3 准备的一套现成界面组件（按钮、表格、表单、弹窗、菜单等），本项目在 `main.js` 全局接入并配置了中文与暗色主题，登录、布局、用户/待办/密码/备忘录等页面几乎都靠 `<el-xxx>` 拼成。不用它页面也能做，但要自己写大量样式和交互，慢且难统一；用了之后开发快、风格一致，删除确认、加载动画、表单校验、全局报错提示等细节都省心。建议从 `main.js` → `LoginView.vue` → `MainLayout.vue` → `UserManageView.vue` → `request.js` 顺序对照阅读，把「安装 → 拼界面 → 调消息」三步串起来。
