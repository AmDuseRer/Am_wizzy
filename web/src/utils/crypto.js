/**
 * 加密脱敏工具
 * 使用 CryptoJS 辅助前端密码脱敏展示（不含真实解密逻辑）
 */
import CryptoJS from 'crypto-js'

/**
 * 密码脱敏：保留首尾各一位，中间用 * 替代
 * @param {string} password - 明文密码
 * @returns {string} 脱敏后的字符串
 */
export function maskPassword(password) {
  if (!password || password.length <= 2) return '****'
  return password[0] + '****' + password[password.length - 1]
}

/**
 * 简单哈希（用于本地草稿 key 等非安全场景）
 * @param {string} text - 输入文本
 * @returns {string} MD5 哈希
 */
export function simpleHash(text) {
  return CryptoJS.MD5(text).toString()
}
