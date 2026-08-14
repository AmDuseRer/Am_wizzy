/**
 * 待办 API
 */
import request from '@/utils/request'

export function listTodos(params) {
  return request.get('/todos', { params })
}

export function createTodo(data) {
  return request.post('/todos', data)
}

export function updateTodo(id, data) {
  return request.put(`/todos/${id}`, data)
}

export function deleteTodo(id) {
  return request.delete(`/todos/${id}`)
}

export function batchUpdateTodos(data) {
  return request.post('/todos/batch-update', data)
}
