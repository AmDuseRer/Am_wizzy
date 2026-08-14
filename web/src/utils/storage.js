/**
 * 本地存储工具
 * 备忘录草稿临时存储，key 含 userId 避免跨用户污染
 */

const DRAFT_PREFIX = 'wizzy_memo_draft_'

/**
 * 保存备忘录草稿到 LocalStorage
 * @param {number} userId - 用户 ID
 * @param {object} draft - 草稿内容 { title, content, category_id }
 */
export function saveMemoDraft(userId, draft) {
  const key = `${DRAFT_PREFIX}${userId}`
  localStorage.setItem(key, JSON.stringify({ ...draft, savedAt: Date.now() }))
}

/**
 * 读取备忘录草稿
 * @param {number} userId - 用户 ID
 * @returns {object|null} 草稿对象或 null
 */
export function loadMemoDraft(userId) {
  const key = `${DRAFT_PREFIX}${userId}`
  const raw = localStorage.getItem(key)
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

/**
 * 清除备忘录草稿
 * @param {number} userId - 用户 ID
 */
export function clearMemoDraft(userId) {
  const key = `${DRAFT_PREFIX}${userId}`
  localStorage.removeItem(key)
}

const VIEW_SESSION_PREFIX = 'wizzy_view_session_'

/** 保存查看专用密码会话（24 小时有效，由服务端 JWT 控制） */
export function saveViewSession(userId, token) {
  localStorage.setItem(`${VIEW_SESSION_PREFIX}${userId}`, token)
}

/** 读取查看专用密码会话 */
export function getViewSession(userId) {
  return localStorage.getItem(`${VIEW_SESSION_PREFIX}${userId}`)
}

/** 清除查看专用密码会话 */
export function clearViewSession(userId) {
  localStorage.removeItem(`${VIEW_SESSION_PREFIX}${userId}`)
}
