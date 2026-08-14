/**
 * 备忘录 API
 */
import request from '@/utils/request'

export function listMemos(params) {
  return request.get('/memos', { params })
}

export function getMemo(id) {
  return request.get(`/memos/${id}`)
}

export function createMemo(data) {
  return request.post('/memos', data)
}

export function updateMemo(id, data) {
  return request.put(`/memos/${id}`, data)
}

export function deleteMemo(id) {
  return request.delete(`/memos/${id}`)
}

/** 后端 TXT 导出 */
export function exportMemoTxt(id) {
  return request.get(`/memos/${id}/export-txt`, { responseType: 'blob' })
}

export function exportAllMemosTxt() {
  return request.get('/memos/export/all-txt', { responseType: 'blob' })
}
