/**
 * Vite 构建配置（最简版）
 * 开发时：npm run dev → 启动本地服务器 + 热更新
 * 上线前：npm run build → 打包成静态文件
 */
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '127.0.0.1',
    port: 5174,
  },
})
