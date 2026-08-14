/**
 * 时间格式化工具
 * 基于 Dayjs 提供统一的时间展示格式
 */
import dayjs from 'dayjs'

/** 格式化为 YYYY-MM-DD HH:mm:ss */
export function formatDateTime(date) {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

/** 格式化为 YYYY-MM-DD */
export function formatDate(date) {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD')
}

/** 格式化为相对时间 */
export function formatRelative(date) {
  if (!date) return '-'
  const d = dayjs(date)
  const now = dayjs()
  const diffMin = now.diff(d, 'minute')
  if (diffMin < 1) return '刚刚'
  if (diffMin < 60) return `${diffMin} 分钟前`
  if (diffMin < 1440) return `${Math.floor(diffMin / 60)} 小时前`
  return d.format('YYYY-MM-DD')
}

export default dayjs
