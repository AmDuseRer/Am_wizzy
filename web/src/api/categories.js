/**
 * 分类 API
 */
import request from '@/utils/request'

export function listCategories(moduleType) {
  return request.get('/categories', { params: { module_type: moduleType } })
}

export function createCategory(data) {
  return request.post('/categories', data)
}

export function updateCategory(id, data) {
  return request.put(`/categories/${id}`, data)
}

export function deleteCategory(id) {
  return request.delete(`/categories/${id}`)
}
