/**
 * 应用入口
 * 初始化 Vue3、Pinia、Router、Element Plus
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

import App from './App.vue'
import router from './router'
import { useAppStore } from './stores/app'

const app = createApp(App)
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)
app.use(ElementPlus, { locale: zhCn })

// 初始化暗色模式
const appStore = useAppStore()
if (appStore.darkMode) {
  document.documentElement.classList.add('dark')
}

app.mount('#app')
