/**
 * 操作日志 API
 */
import request from '@/utils/request'

export function listLogs(params) {
  return request.get('/logs', { params })
}
