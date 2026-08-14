/**
 * 备忘录 TXT 导出工具
 * 使用 UTF-8 BOM 编码，确保 Windows 记事本正确显示中文
 */
import { formatDateTime } from './date'

function downloadTxt(filename, content) {
  const blob = new Blob(['\uFEFF' + content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

function resolveCategoryName(categoryId, getCategoryName) {
  if (typeof getCategoryName === 'function') {
    return getCategoryName(categoryId)
  }
  return categoryId ? String(categoryId) : '未分类'
}

function formatMemoText(memo, getCategoryName) {
  const lines = [
    `标题：${memo.title || ''}`,
    `分类：${resolveCategoryName(memo.category_id, getCategoryName)}`,
    `创建时间：${formatDateTime(memo.created_at)}`,
    `更新时间：${formatDateTime(memo.updated_at)}`,
  ]
  if (memo.is_pinned) {
    lines.push('置顶：是')
  }
  lines.push('', '内容：', memo.content || '')
  return lines.join('\n')
}

/**
 * 导出单条备忘录为 TXT
 * @param {object} memo - 备忘录对象
 * @param {Function} getCategoryName - 根据 category_id 返回分类名称
 */
export function exportMemoTxt(memo, getCategoryName) {
  downloadTxt(`memo_${memo.id}.txt`, formatMemoText(memo, getCategoryName))
}

/**
 * 批量导出备忘录 TXT
 * @param {Array} memos - 备忘录列表
 * @param {Function} getCategoryName - 根据 category_id 返回分类名称
 */
export function exportMemosTxt(memos, getCategoryName) {
  const parts = memos.map((memo, index) => {
    const header = `${'='.repeat(20)} 备忘录 ${index + 1}/${memos.length} ${'='.repeat(20)}`
    return `${header}\n${formatMemoText(memo, getCategoryName)}`
  })
  downloadTxt('memos_export.txt', parts.join('\n\n'))
}
