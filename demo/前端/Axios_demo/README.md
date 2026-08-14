# Axios 练习2：封装与拦截器

> 对应学习题：**亲手写「迷你封装 + 拦截器」**  
> 练会：公共配置写一处、请求前自动带 token、响应后统一判断 `code`

---

## 目录结构

```
demo/前端/Axios_demo/
├── package.json      # 依赖 axios（Node 版测试用）
├── run-tests.js      # Node 自动测试（推荐 Windows 命令行运行）
├── index.html        # 浏览器交互版（按钮 + 自动测试）
└── README.md         # 本文件
```

---

## 方式一：Node 命令行（推荐，适合 Windows）

### 运行步骤

在仓库根目录 `wizzy` 下打开 **PowerShell** 或 **CMD**：

```powershell
cd demo\前端\Axios_demo
npm install
node run-tests.js
```

或一条命令跑测试：

```powershell
npm test
```

**无需启动后端、无需打开 wizzy 主项目。**

### 预期输出（大致样子）

全部通过时，终端应类似：

```
========================================
  Axios 练习2：封装 + 拦截器 自动测试
========================================

--- 用例：1. GET /memos（无需登录，应成功） ---
  [请求拦截] GET /api/memos，未带 token
  [响应拦截] 成功，data={"items":[{"id":1,"title":"买牛奶"},{"id":2,"title":"学 Axios"}],"total":2}
[OK] 1. GET /memos（无需登录，应成功）
     页面拿到的 data：{"items":[...],"total":2}

--- 用例：2. GET /secret（未登录，应失败） ---
  [请求拦截] GET /api/secret，未带 token
  [响应拦截] 失败 code=401，message=未登录
[OK] 2. GET /secret（未登录，应失败）（按预期失败）
     捕获错误：未登录

--- 用例：3. GET /secret（已登录，应成功） ---
  [请求拦截] GET /api/secret，已带 token
  [响应拦截] 成功，data="机密数据"
[OK] 3. GET /secret（已登录，应成功）
     页面拿到的 data："机密数据"

--- 用例：4. GET /bad（业务 code=500，应失败） ---
  [请求拦截] GET /api/bad，已带 token
  [响应拦截] 失败 code=500，message=服务器开小差了
[OK] 4. GET /bad（业务 code=500，应失败）（按预期失败）
     捕获错误：服务器开小差了

========================================
  测试结果：4 通过，0 失败
========================================
```

若有 `[FAIL]` 或最后一行显示 `1 失败`，说明拦截器或假后端逻辑写错，对照 `run-tests.js` 检查。

---

## 方式二：浏览器（可视化按钮）

### 运行步骤

1. 用 **Chrome** 直接双击打开 `index.html`  
   （路径：`demo\前端\Axios_demo\index.html`）
2. 点击 **「运行全部测试」**，看下方黑色日志区

若 CDN 加载 axios 失败，可在本目录执行：

```powershell
npx serve .
```

浏览器访问提示的地址（通常是 `http://localhost:3000`），再打开页面。

### 手动按钮测试

| 操作 | 预期 |
|------|------|
| 不设置 token，点 **GET /secret** | 日志出现 `未登录`，页面 catch 到错误 |
| 点 **设置 token**，再点 **GET /secret** | 成功，显示 `机密数据` |
| 点 **GET /memos** | 成功，共 2 条，第一条「买牛奶」 |
| 点 **GET /bad** | 失败，提示「服务器开小差了」 |

---

## 代码对应关系（练完对照主项目）

| 本 demo | wizzy 主项目 |
|---------|----------------|
| `run-tests.js` 里的 `request` + 拦截器 | `web/src/utils/request.js` |
| `listMemos` / `getSecret` | `web/src/api/memos.js` 等 |
| `fakeToken` | `web/src/stores/auth.js` 里的 `token` |
| `fakeServer` 返回 `{ code, data, message }` | 后端 FastAPI 的 `success()` 格式 |

---

## 要练会什么（自检）

- [ ] 能说出「封装」：`axios.create` 把 `baseURL`、超时写在一处
- [ ] 能说出「请求拦截器」：发出前自动加 `Authorization`
- [ ] 能说出「响应拦截器」：`code !== 0` 时 reject，页面走 catch
- [ ] 能区分：api 层只写路径，页面只 `await listMemos()` 拿 `res.data`
