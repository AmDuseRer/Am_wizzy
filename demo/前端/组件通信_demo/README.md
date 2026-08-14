# Vue 组件通信 · 练习 1~4（v-model / defineExpose）

> 对应概念：父子组件数据同步、弹窗开关、分类选择、defineExpose 刷新  
> 练会：v-model 双向绑定、modelValue + emit、ref 调用子组件方法

---

## 目录结构

```
demo/前端/组件通信_demo/
├── README.md                        # 本文件
├── package.json                     # npm test 快捷命令
├── run_all.js                       # 一键运行练习 1~4 自动测试
├── exercise1-v-model-input.js       # 练习1：Node 自动测试
├── exercise1-v-model-input.html     # 练习1：浏览器动手版
├── exercise2-v-model-dialog.js
├── exercise2-v-model-dialog.html
├── exercise3-v-model-select.js
├── exercise3-v-model-select.html
├── exercise4-define-expose.js
└── exercise4-define-expose.html
```

---

## 方式 A：Node.js 自动测试（推荐先做）

### 运行方式（Windows PowerShell / CMD）

在仓库根目录 `wizzy` 下：

```powershell
cd demo\前端\组件通信_demo
node run_all.js
```

或单独跑某一题：

```powershell
node exercise1-v-model-input.js
node exercise2-v-model-dialog.js
node exercise3-v-model-select.js
node exercise4-define-expose.js
```

或使用 npm：

```powershell
npm test
npm run exercise1
```

**说明：**

- **无需** `npm install`（零依赖）
- **无需** 浏览器、后端或 wizzy 主项目
- 需要已安装 **Node.js 18+**（终端执行 `node -v` 检查）

### 预期输出（大致样子）

```
========================================
  Vue 组件通信 Demo：运行全部练习
========================================

=== 练习 1：v-model 基础（输入框与文字同步）===

[OK] 初始 message 为空
[OK] 初始字符数为 0
[OK] 输入 hello 后 display 同步
     display="hello"
[OK] 输入 hello 后字符数为 5
...

结果：7 通过，0 失败
全部通过。浏览器版请打开 exercise1-v-model-input.html 亲手输入试试。

=== 练习 2：父子 v-model（弹窗开关）===
...

========================================
练习 1~4 全部通过。
建议再用浏览器打开 exercise1~4 的 .html 文件亲手操作一遍。
========================================
```

若有失败会显示 `[FAIL]` 和具体原因。

---

## 方式 B：浏览器动手版（配合 HTML）

### 运行方式

1. 用资源管理器双击打开对应 `.html` 文件  
2. 或 PowerShell 中：

```powershell
start demo\前端\组件通信_demo\exercise1-v-model-input.html
start demo\前端\组件通信_demo\exercise2-v-model-dialog.html
start demo\前端\组件通信_demo\exercise3-v-model-select.html
start demo\前端\组件通信_demo\exercise4-define-expose.html
```

**说明：**

- 需要能访问 CDN（`unpkg.com`）加载 Vue 3
- **无需** 启动本地服务器，直接打开即可
- 每个页面底部有自动测试面板，显示 `[OK]` / `[FAIL]`

### 各题手动测试预期

| 练习 | 操作 | 预期 |
|------|------|------|
| 1 | 输入 `hello` | 下方显示 hello，字符数 5 |
| 1 | 清空输入框 | 字符数 0 |
| 2 | 点「打开弹窗」 | 弹窗出现，visible=true |
| 2 | 点弹窗内「关闭」 | 弹窗消失，visible=false |
| 3 | 选「工作」 | id=1，筛选出「写报告、开会」 |
| 3 | 选「生活」 | 筛选出「买菜」 |
| 4 | 点「新增分类」 | 列表**不变**（仍是 3 项） |
| 4 | 再点「刷新」 | 列表变成 4 项，出现「运动」 |

---

## 练完后对照项目文件

| 练习 | 对照看什么 |
|------|------------|
| 1 | `web/src/views/LoginView.vue`（表单 v-model） |
| 2 | `web/src/layouts/MainLayout.vue` + `web/src/components/ChangePasswordDialog.vue` |
| 3 | `web/src/components/CategorySelect.vue` + `web/src/views/TodoListView.vue` |
| 4 | `CategorySelect.vue` 的 `defineExpose` + `TodoListView.vue` 的 `?.refresh()` |
