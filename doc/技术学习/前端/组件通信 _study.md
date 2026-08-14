# Vue 组件通信（v-model / defineExpose）学习笔记

> 结合本项目（wizzy 小智工具箱）的通俗讲解，面向零基础。  
> 动手练习脚本（练习 1~4）：`demo/前端/组件通信_demo/`

---

## 目录

1. [一句话理解](#一句话理解)
2. [组件通信是什么](#组件通信是什么)
3. [v-model 是什么](#v-model-是什么)
4. [defineExpose 是什么](#defineexpose-是什么)
5. [在本项目中的作用](#在本项目中的作用)
6. [不用 vs 用了](#不用-vs-用了)
7. [实质好处（带对比）](#实质好处带对比)
8. [代码写在哪（三层用法）](#代码写在哪三层用法)
9. [v-model 与 defineExpose 基础骨架](#v-model-与-defineexpose-基础骨架)
10. [在本项目里具体怎么用](#在本项目里具体怎么用)
11. [一次完整交互流程](#一次完整交互流程)
12. [动手练习（5 道题）](#动手练习5-道题)
13. [练完后对照项目文件](#练完后对照项目文件)
14. [总结](#总结)

---

## 一句话理解

**Vue 页面像俄罗斯套娃，外面是父组件、里面是子组件。`v-model` 让父子共用同一份数据（弹窗开不开、选了哪个分类、输入框里是什么），改一边另一边自动跟上；`defineExpose` 让父组件在需要时主动叫子组件干活（比如刷新分类列表），而不必把子组件内部逻辑全搬到外面。**

---

## 组件通信是什么

一个 Vue 页面往往由很多**小组件**拼成：顶栏、侧边栏、弹窗、下拉框、表单……

这些组件之间需要**传数据、同步状态**：

- 父页面要知道弹窗是开还是关
- 父页面要知道用户选了哪个分类
- 父页面要在某个时机让子组件重新加载数据

**组件通信**就是解决「父 ↔ 子之间怎么配合」的问题。

本项目里最常用的两种方式：

| 方式 | 干什么 | 典型场景 |
|------|--------|----------|
| **v-model** | 父子**共用同一份数据**，自动同步 | 弹窗开关、分类选择、表单输入 |
| **defineExpose** | 子组件**暴露方法**，父组件用 ref 调用 | 刷新分类下拉列表 |

---

## v-model 是什么

可以把它想成：**界面上的值** 和 **变量** 绑在一起，改任意一边，另一边立刻跟着变。

### 在普通输入框上

```html
<input v-model="message" />
<p>{{ message }}</p>
```

你在输入框打字 → `message` 变量更新 → 下面 `<p>` 自动显示新内容。

### 在自定义子组件上

父组件写：

```html
<ChangePasswordDialog v-model="showChangePassword" />
```

等价于两行（Vue 帮你简写了）：

```html
<ChangePasswordDialog
  :modelValue="showChangePassword"
  @update:modelValue="showChangePassword = $event"
/>
```

子组件收到 `modelValue`，改完要通知父组件时 `emit('update:modelValue', 新值)`。

**记住：** 组件上的 `v-model` 不是魔法，就是 **传值 + 通知更新** 的语法糖。

---

## defineExpose 是什么

Vue 3 的 `<script setup>` 里，组件内部变量和方法**默认对外不可见**——父组件拿不到。

**defineExpose** = 子组件主动「递钥匙」，告诉父组件：你可以调用这几个方法。

```javascript
defineExpose({ refresh: loadCategories })
```

父组件配合 `ref` 使用：

```html
<CategorySelect ref="filterRef" v-model="categoryId" />
```

```javascript
filterRef.value?.refresh()
```

**记住：** 没有 defineExpose，父组件就像站在子组件门外，按门铃也无人应答。

---

## 在本项目中的作用

小智工具箱的待办、备忘录、密码本页面，大量用到「弹窗 + 表单 + 分类下拉」。这些 UI 被拆成独立小组件，**父页面必须和子组件保持同步**。

### 1. v-model 控制弹窗开关

`MainLayout.vue` 里一行代码控制修改密码弹窗：

```html
<ChangePasswordDialog v-model="showChangePassword" />
```

用户点「修改密码」→ `showChangePassword = true` → 弹窗打开；  
用户点「取消」或改完密码 → 子组件把值改回 `false` → 弹窗关闭。

### 2. v-model 同步分类选择

`TodoListView.vue` 里：

```html
<CategorySelect v-model="filters.category_id" module-type="todo" />
```

用户选了「工作」→ `filters.category_id` 立刻变成对应 id → 列表按分类筛选。

### 3. v-model 绑定表单字段

`ChangePasswordDialog.vue` 里每个输入框：

```html
<el-input v-model="form.old_password" type="password" show-password />
```

打字 → `form` 更新 → 点「确定」时提交到后端。

### 4. defineExpose 刷新分类列表

待办页有**两个** `CategorySelect`（筛选区一个、编辑弹窗里一个）。在筛选区新建分类后，弹窗里的下拉不会自动知道——父页面调用：

```javascript
filterCategorySelectRef.value?.refresh()
dialogCategorySelectRef.value?.refresh()
```

`CategorySelect.vue` 里暴露了 `refresh`：

```javascript
defineExpose({ refresh: loadCategories })
```

**不可或缺在哪？** 没有 v-model，弹窗、下拉、表单要手写大量传值和事件，易漏接、易不同步；没有 defineExpose，父组件无法让子组件刷新，两个下拉会显示不一致。

---

## 不用 vs 用了

### 场景 A：控制弹窗开关

| 不用 v-model | 用了 v-model |
|--------------|--------------|
| 父写 `:visible="show"` + `@close="show=false"` 等多行；子也要配合写事件 | 父组件一行 `v-model="showChangePassword"` |

### 场景 B：分类选择

| 不用 | 用了 |
|------|------|
| 父组件手动监听 `@change`，自己更新 `category_id` | `v-model="filters.category_id"`，选完自动同步 |

### 场景 C：表单输入

| 不用 | 用了 |
|------|------|
| 每个输入框写 `:value="form.xxx"` + `@input="form.xxx = $event"` | 一个 `v-model="form.old_password"` |

### 场景 D：刷新分类列表

| 不用 defineExpose | 用了 defineExpose |
|-------------------|-------------------|
| 没法从外部叫子组件刷新；只能改 key 强制重建，或把逻辑全搬到父组件 | `ref.value.refresh()` 直接叫子组件重新加载 |

### 场景 E：子组件关闭弹窗但不通知父组件

| 不用 emit | 用了 emit（v-model 底层机制） |
|-----------|-------------------------------|
| 子组件以为关了，父组件 `visible` 仍是 true，弹窗关不掉或状态错乱 | 子 emit `update:modelValue`，父子始终一致 |

---

## 实质好处（带对比）

### 好处一：代码更短、更不容易写错

| 不用 | 用了 |
|------|------|
| 弹窗要接 3～4 行 props + 事件 | `MainLayout` 里就一行 `v-model="showChangePassword"` |
| 6 个输入框 × 2 行绑定 = 12 行 | 6 个 `v-model`，一眼能看懂绑的是谁 |

### 好处二：数据和界面始终一致

| 不用 | 用了 |
|------|------|
| 父组件以为弹窗开着，子组件已经关了 | 弹窗开/关只认 `showChangePassword` 这一个变量 |
| 选了分类但忘记写事件 → 筛选条件没变 | `v-model` 保证「选了什么 = 存了什么」 |

### 好处三：组件可以真正「复用」

| 不用 | 用了 |
|------|------|
| `CategorySelect` 每个页面复制粘贴一套通信代码 | 待办、备忘录、密码本都用同一个组件，父页面只写 `v-model="category_id"` |
| 刷新逻辑散落在各页面 | `defineExpose({ refresh })` 统一出口，父页面按需调用 |

### 好处四：职责清晰，好维护

| 不用 | 用了 |
|------|------|
| 父组件既要管页面逻辑，又要管弹窗内部细节 | 弹窗自己管表单校验、提交；父组件只管「开不开」 |
| 刷新分类的逻辑被迫提到父组件 | 加载分类留在 `CategorySelect` 内部；父组件只在需要时说「刷新一下」 |

---

## 代码写在哪（三层用法）

| 做什么 | 写在哪 | 例子 |
|--------|--------|------|
| **父组件绑定** | 父 `.vue` 的 `<template>` | `<CategorySelect v-model="categoryId" ref="xxx" />` |
| **子组件接收 + 通知** | 子 `.vue` 的 `<script setup>` | `defineProps`、`defineEmits`、computed 中转 |
| **子组件暴露方法** | 子 `.vue` 的 `<script setup>` 末尾 | `defineExpose({ refresh })` |
| **父组件调用子方法** | 父 `.vue` 的 `<script setup>` | `xxxRef.value?.refresh()` |

---

## v-model 与 defineExpose 基础骨架

### 骨架 A：子组件支持 v-model（弹窗 / 下拉通用）

```javascript
// 子组件 script setup
const props = defineProps({ modelValue: Boolean })  // 或 Number、String 等
const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})
```

```html
<!-- 父组件 -->
<MyDialog v-model="dialogVisible" />
```

### 骨架 B：子组件暴露 refresh

```javascript
// 子组件
async function loadData() { /* 从 API 拉数据 */ }

defineExpose({ refresh: loadData })
```

```html
<!-- 父组件 -->
<MyList ref="listRef" />
<button @click="listRef?.refresh()">刷新</button>
```

### 三个易错点

1. **子组件改父组件数据必须 emit**，不能直接改 props（props 是只读的）
2. **v-model 在组件上默认绑的是 `modelValue`**，子组件要配合 `update:modelValue`
3. **ref 要在子组件挂载后才能用**，所以常写 `xxxRef.value?.refresh()`（`?.` 防止 null）

---

## 在本项目里具体怎么用

### 例 1：修改密码弹窗（v-model 双层）

**父组件** `web/src/layouts/MainLayout.vue`：

```html
<ChangePasswordDialog v-model="showChangePassword" />
```

```javascript
const showChangePassword = ref(false)
// 用户点菜单「修改密码」时：showChangePassword.value = true
```

**子组件** `web/src/components/ChangePasswordDialog.vue`：

```javascript
const props = defineProps({ modelValue: Boolean })
const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})
```

模板里 `<el-dialog v-model="visible">` 和表单 `<el-input v-model="form.xxx">` 是同一套思路。

### 例 2：分类选择（v-model + defineExpose）

**子组件** `web/src/components/CategorySelect.vue`：

```html
<el-select
  :model-value="modelValue"
  @update:model-value="$emit('update:modelValue', $event)"
>
```

```javascript
defineExpose({ refresh: loadCategories })
```

**父组件** `web/src/views/TodoListView.vue`：

```html
<CategorySelect
  ref="filterCategorySelectRef"
  v-model="filters.category_id"
  module-type="todo"
  @updated="onCategoryUpdated"
/>
```

```javascript
async function onCategoryUpdated() {
  filterCategorySelectRef.value?.refresh()
  dialogCategorySelectRef.value?.refresh()
}
```

### 常用写法速查

```html
<!-- 弹窗 -->
<MyDialog v-model="visible" />

<!-- 下拉 / 自定义组件 -->
<CategorySelect v-model="categoryId" ref="catRef" />

<!-- 输入框 -->
<el-input v-model="form.title" />
```

```javascript
catRef.value?.refresh()
visible.value = true
```

---

## 一次完整交互流程

以「待办页筛选区新建分类」为例：

```
用户在 CategorySelect 里点「新增分类」
    ↓
子组件调 API 创建分类，emit('update:modelValue', 新id)
    ↓
父组件 filters.category_id 自动更新（v-model）
    ↓
子组件 emit('updated') 通知父组件「分类有变动」
    ↓
父组件 onCategoryUpdated() 调用两个 ref 的 refresh()
    ↓
filterCategorySelectRef 和 dialogCategorySelectRef 各自重新 loadCategories
    ↓
筛选区和弹窗里的下拉列表显示一致
```

---

## 动手练习（5 道题）

由浅入深。练习 1~4 已有可执行脚本（Node + HTML）；练习 5 为迷你综合题（浏览器单文件）。

---

### 练习 1：输入框和文字「绑在一起」（v-model 基础）

#### 要练会什么

`v-model` = 界面和数据自动同步：输入框打字，下面文字跟着变。

#### 可执行代码

```
demo/前端/组件通信_demo/exercise1-v-model-input.js
demo/前端/组件通信_demo/exercise1-v-model-input.html
```

#### 运行方式（Windows）

```powershell
cd demo\前端\组件通信_demo
node exercise1-v-model-input.js
```

或浏览器：

```powershell
start demo\前端\组件通信_demo\exercise1-v-model-input.html
```

无需 `npm install`，Node 版零依赖。

#### 预期结果

| 操作 / 断言 | 预期 |
|-------------|------|
| 初始 | message 为空，字符数 0 |
| 输入 `hello` | display 显示 hello，字符数 5 |
| 清空 | 字符数 0 |
| 输入 `你好` | 字符数 2 |

终端应出现 `[OK]` 共 8 条，最后 `8 通过，0 失败`。

#### 核心逻辑（摘要）

```javascript
function createRef(initial) {
  let value = initial
  return { get: () => value, set: (v) => { value = v } }
}

function createInputVModel(messageRef) {
  return {
    type(text) { messageRef.set(text) },
    displayText() { return messageRef.get() },
    length() { return messageRef.get().length },
  }
}
```

---

### 练习 2：父组件控制子弹窗「开 / 关」（父子 v-model）

#### 要练会什么

父组件 `v-model` 绑定变量；子组件通过 `props.modelValue` + `emit('update:modelValue')` 同步。

#### 可执行代码

```
demo/前端/组件通信_demo/exercise2-v-model-dialog.js
demo/前端/组件通信_demo/exercise2-v-model-dialog.html
```

运行方式同练习 1（把文件名中的 `1` 换成 `2`）。

#### 预期结果

| 操作 / 断言 | 预期 |
|-------------|------|
| 初始 | 弹窗关闭，visible=false |
| 父组件点打开 | visible=true，弹窗显示 |
| 子组件点关闭 | visible=false，弹窗消失 |
| 负面：子不 emit | 父 visible 仍为 true（关不掉） |

终端应显示 `4 通过，0 失败`。

#### 核心逻辑（摘要）

```javascript
// 子组件关闭 = emit('update:modelValue', false)
function close() {
  parent.onUpdateModelValue(false)
}
```

---

### 练习 3：下拉框把选中值传回父组件（v-model 传 id）

#### 要练会什么

`v-model` 不只传 true/false，也可传分类 id；父组件用 id 做筛选。

#### 可执行代码

```
demo/前端/组件通信_demo/exercise3-v-model-select.js
demo/前端/组件通信_demo/exercise3-v-model-select.html
```

#### 测试数据与预期

| 选择 | categoryId | 筛选结果 |
|------|------------|----------|
| 请选择 | null | （空） |
| 工作 (id=1) | 1 | 写报告、开会 |
| 生活 (id=2) | 2 | 买菜 |
| 学习 (id=3) | 3 | 背单词 |

终端应显示 `8 通过，0 失败`。

---

### 练习 4：父组件叫子组件刷新（defineExpose）

#### 要练会什么

子组件 `defineExpose({ refresh })`；父组件 `ref.value.refresh()` 重新加载数据。

#### 可执行代码

```
demo/前端/组件通信_demo/exercise4-define-expose.js
demo/前端/组件通信_demo/exercise4-define-expose.html
```

#### 预期结果

| 步骤 | 预期 |
|------|------|
| 初始 | 列表 3 项：工作、生活、学习 |
| 模拟新增「运动」（不 refresh） | 列表仍是 3 项 |
| 父组件调用 refresh | 列表变 4 项，含「运动」 |
| 无 expose 时 | 父调不到 refresh（undefined） |

浏览器版：先点「新增」，不点「刷新」→ 列表不变；再点「刷新」→ 出现「运动」。

终端应显示 `8 通过，0 失败`。

#### 核心逻辑（摘要）

```javascript
function createCategoryListWithExpose() {
  let list = [...db]
  function refresh() { list = [...db] }
  return { getList: () => [...list], refresh }
}
```

---

### 练习 5：迷你综合题（最接近真实项目）

#### 要练会什么

`v-model`（弹窗开关 + 分类选择）+ `defineExpose`（刷新）合在一起。  
结构接近 `TodoListView` + `CategorySelect` + 弹窗。

#### 怎么做

在浏览器中新建或打开单文件 HTML（可参考第一次学习对话中的 `05-mini-todo-category.html` 完整代码），包含：

- 筛选区 `CategorySelect` + `v-model="filterId"`
- 新增待办弹窗 `v-model="dialogVisible"`
- 弹窗内嵌第二个 `CategorySelect`
- `onSaved` 后调用两个 ref 的 `refresh()`

#### 测试清单

| 步骤 | 操作 | 预期（成功） |
|------|------|--------------|
| 1 | 打开页面 | 列表 2 条：写周报、买菜 |
| 2 | 筛选选「工作」 | 只显示「写周报」 |
| 3 | 新增待办，标题留空点保存 | alert「标题不能为空」，弹窗不关 |
| 4 | 填标题但不选分类 | alert「请选择分类」 |
| 5 | 选「工作」保存 | 弹窗关闭，列表多一条 |
| 6 | 筛选区新建分类「学习」 | 下拉出现「学习」 |
| 7 | 新增「背单词」选「学习」 | 筛选「学习」只显示该条 |

#### 与主项目对应

| 迷你题 | 主项目 |
|--------|--------|
| `v-model="dialogVisible"` | `ChangePasswordDialog` / 各页编辑弹窗 |
| `v-model="filterId"` | `TodoListView` 的 `filters.category_id` |
| `filterRef.refresh()` | `onCategoryUpdated()` 里两个 `?.refresh()` |
| `defineExpose({ refresh })` | `CategorySelect.vue` 第 97 行 |

---

### 一键运行练习 1~4

```powershell
cd demo\前端\组件通信_demo
node run_all.js
```

或 `npm test`。

全部通过时终端末尾：

```
练习 1~4 全部通过。
建议再用浏览器打开 exercise1~4 的 .html 文件亲手操作一遍。
```

---

## 练完后对照项目文件

### 练习与文件对照

| 练完题号 | 打开的文件 | 对照什么 |
|----------|------------|----------|
| 练习 1 | `web/src/views/LoginView.vue` | 表单 `v-model="form.xxx"` |
| 练习 2 | `web/src/layouts/MainLayout.vue` | `<ChangePasswordDialog v-model="showChangePassword" />` |
| 练习 2 | `web/src/components/ChangePasswordDialog.vue` | `defineProps` + computed visible + emit |
| 练习 3 | `web/src/components/CategorySelect.vue` | `:model-value` + `@update:model-value` |
| 练习 3 | `web/src/views/TodoListView.vue` | `v-model="filters.category_id"` |
| 练习 4 | `web/src/components/CategorySelect.vue` 第 97 行 | `defineExpose({ refresh: loadCategories })` |
| 练习 4 | `web/src/views/TodoListView.vue` | `filterCategorySelectRef.value?.refresh()` |
| 练习 5 | `web/src/views/TodoListView.vue` 全文 | 筛选 + 弹窗 + 两个 CategorySelect + `onCategoryUpdated` |
| 练习 5 | `web/src/views/MemoListView.vue` | 同样模式复用 CategorySelect |
| 练习 5 | `web/src/views/PasswordListView.vue` | 弹窗 + ViewPasswordDialog v-model |

### demo 与主项目对照

| demo（组件通信_demo） | 主项目 |
|-----------------------|--------|
| `createInputVModel` | `<el-input v-model="form.xxx">` |
| `createMyDialog` + emit | `ChangePasswordDialog.vue` 的 visible computed |
| `createCategoryPicker` + filter | `CategorySelect` + 列表筛选 |
| `child.refresh()` | `CategorySelect` defineExpose + 父 ref 调用 |
| 两个下拉都要 refresh | `TodoListView` 的 filterRef + dialogRef |

### 补充 demo（父子传值入门）

| 文件 | 内容 |
|------|------|
| `demo/前端/APIAndScriptSetup_demo/src/components/LessonPropsEmit.vue` | props 传入 + emit 传出（v-model 的底层原理） |

### 建议阅读顺序

`LoginView.vue`（练习1）→ `ChangePasswordDialog.vue` + `MainLayout.vue`（练习2）→ `CategorySelect.vue` + `TodoListView.vue`（练习3、4）→ `MemoListView.vue` / `PasswordListView.vue`（复用验证）

### 自检清单

- [ ] 能说出 v-model = 父子共用一份数据，改一边另一边跟上
- [ ] 能说出组件 v-model 底层是 modelValue + update:modelValue
- [ ] 能说出 defineExpose = 子组件暴露方法，父组件 ref 调用
- [ ] 能解释为什么新建分类后要 refresh 两个 CategorySelect
- [ ] 跑通 `demo/前端/组件通信_demo`，`node run_all.js` 显示全部通过

---

## 总结

**v-model** 让父组件和子组件共用同一份数据（弹窗开不开、选了哪个分类、输入框里是什么），是 Vue 里最常用的组件通信方式。**defineExpose** 让父组件在需要时主动叫子组件干活（如刷新分类列表），而不必把子组件内部逻辑搬到外面。在本项目中，它们让弹窗、表单、CategorySelect 等小组件能拆出来并在待办/备忘录/密码本多处复用；不用它们，父子通信会变成大量重复、易错的传值和事件监听。动手练完 `demo/前端/组件通信_demo` 后，按 `ChangePasswordDialog.vue` → `CategorySelect.vue` → `TodoListView.vue` 顺序对照主项目即可。
