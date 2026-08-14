/**
 * Vite 构建配置
 * 端口 5175：避免与 ViteVue3_demo(5174)、web/(5173) 冲突
 */
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '127.0.0.1',
    port: 5175,
  },
})
