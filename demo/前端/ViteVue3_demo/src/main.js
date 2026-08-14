/**
 * 应用入口（和 web/src/main.js 同一角色，但这里只挂载 Vue，没有 Router / Pinia / UI 库）
 */
import { createApp } from 'vue'
import App from './App.vue'
import './style.css'

createApp(App).mount('#app')
