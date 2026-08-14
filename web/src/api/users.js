/**
 * 用户管理 API（admin）
 */
import request from '@/utils/request'

export function listUsers(params) {
  return request.get('/users', { params })
}

export function createUser(data) {
  return request.post('/users', data)
}

export function updateUser(id, data) {
  return request.put(`/users/${id}`, data)
}

export function deleteUser(id) {
  return request.delete(`/users/${id}`)
}

export function resetPassword(id, data) {
  return request.post(`/users/${id}/reset-password`, data)
}
