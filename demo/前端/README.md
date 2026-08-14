# 前端 Demo 示例集

本目录用于存放前端技术栈的独立学习示例，每个子目录对应一种技术或框架。

## 目录

| 目录 | 说明 |
|------|------|
| [ViteVue3_demo](./ViteVue3_demo/) | Vue 3 + Vite 最简入门（组件、响应式、热更新） |
| [Axios_demo](./Axios_demo/) | Axios 封装与拦截器练习（Node 自动测试 + 浏览器版） |
| [Pinia_demo](./Pinia_demo/) | Pinia 练习 1~3：共用仓库 / 持久化 / defineStore 骨架（Node 零依赖） |

## 约定

- 每个子目录自包含：代码、依赖（`package.json`）、独立 README
- 在对应子目录内执行 `npm install` 与 `npm run dev`（详见各子目录 README）
- 正式项目前端在仓库根目录 [`web/`](../../web/)，demo 学完后请对照阅读
- 新增其他前端 demo 时，在 `demo/前端/` 下新建同级目录即可

## 与后端 demo 的配合

| 你想理解… | 建议组合 |
|-----------|----------|
| 页面怎么跑起来 | 本目录 `ViteVue3_demo` |
| API 怎么设计 | `demo/后端/FastAPI_demo` |
| 前后端怎么联调 | `web/` + `server/` 一起启动 |
