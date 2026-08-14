/**
 * 密码本 API
 */
import request from '@/utils/request'

export function listPasswords(params) {
  return request.get('/passwords', { params })
}

export function createPassword(data) {
  return request.post('/passwords', data)
}

export function updatePassword(id, data) {
  return request.put(`/passwords/${id}`, data)
}

export function deletePassword(id) {
  return request.delete(`/passwords/${id}`)
}

/** 二次校验查看明文 */
export function revealPassword(id, data) {
  return request.post(`/passwords/${id}/reveal`, data)
}

/** 导出加密备份 */
export function exportBackup() {
  return request.get('/passwords/export/backup', { responseType: 'blob' })
}
