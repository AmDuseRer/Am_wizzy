/**
 * 认证 API
 */
import request from '@/utils/request'

/** 登录 */
export function login(data) {
  return request.post('/auth/login', data)
}

/** 登出 */
export function logout() {
  return request.post('/auth/logout')
}

/** 获取当前用户 */
export function getMe() {
  return request.get('/auth/me')
}

/** 修改密码 */
export function changePassword(data) {
  return request.post('/auth/change-password', data)
}

/** 查看专用密码是否已设置 */
export function getViewPasswordStatus() {
  return request.get('/auth/view-password/status')
}

/** 设置/修改查看专用密码 */
export function setViewPassword(data) {
  return request.post('/auth/view-password', data)
}

/** 验证查看专用密码，获取 24 小时查看会话 */
export function verifyViewPassword(viewPassword) {
  return request.post('/auth/view-password/verify', { view_password: viewPassword })
}
