/**
 * 认证状态管理
 * 存储 JWT 令牌与用户基础信息，持久化到 LocalStorage
 * 敏感明文禁止本地持久化
 */
import { defineStore } from 'pinia'
import { login as loginApi, logout as logoutApi, getMe, changePassword as changePasswordApi } from '@/api/auth'
import { clearViewSession } from '@/utils/storage'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    /** JWT 访问令牌 */
    token: '',
    /** 用户基础信息（不含密码等敏感数据） */
    userInfo: null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.userInfo?.role === 'admin',
    username: (state) => state.userInfo?.username || '',
  },

  actions: {
    /** 用户登录 */
    async login(credentials) {
      const res = await loginApi(credentials)
      this.token = res.data.access_token
      this.userInfo = res.data.user
      return res
    },

    /** 用户登出 */
    async logout() {
      try {
        if (this.token) await logoutApi()
      } catch {
        // 忽略登出 API 错误
      }
      if (this.userInfo?.id) clearViewSession(this.userInfo.id)
      this.token = ''
      this.userInfo = null
    },

    /** 刷新当前用户信息 */
    async fetchUserInfo() {
      const res = await getMe()
      this.userInfo = res.data
    },

    /** 修改密码 */
    async changePassword(data) {
      const userId = this.userInfo?.id
      await changePasswordApi(data)
      if (userId) clearViewSession(userId)
      this.token = ''
      this.userInfo = null
    },
  },

  persist: {
    key: 'wizzy-auth',
    paths: ['token', 'userInfo'],
  },
})
