/**
 * 应用全局状态
 * 暗色模式、侧边栏折叠等 UI 状态
 */
import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    /** 是否暗色模式 */
    darkMode: false,
    /** 侧边栏是否折叠 */
    sidebarCollapsed: false,
  }),

  actions: {
    /** 切换暗色/亮色模式 */
    toggleDarkMode() {
      this.darkMode = !this.darkMode
      if (this.darkMode) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    },

    /** 切换侧边栏折叠 */
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },
  },

  persist: {
    key: 'wizzy-app',
    paths: ['darkMode', 'sidebarCollapsed'],
  },
})
