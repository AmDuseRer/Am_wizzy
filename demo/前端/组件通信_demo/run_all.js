/**
 * 一键运行练习 1~4 的全部自动测试
 *
 * 运行方式：
 *   cd demo\前端\组件通信_demo
 *   node run_all.js
 *
 * 或：npm test
 */

const { spawnSync } = require('node:child_process')
const path = require('node:path')

const scripts = [
  'exercise1-v-model-input.js',
  'exercise2-v-model-dialog.js',
  'exercise3-v-model-select.js',
  'exercise4-define-expose.js',
]

console.log('========================================')
console.log('  Vue 组件通信 Demo：运行全部练习')
console.log('========================================')

let totalFailed = 0

for (const script of scripts) {
  console.log('')
  const result = spawnSync(process.execPath, [path.join(__dirname, script)], {
    encoding: 'utf8',
    stdio: 'inherit',
  })
  if (result.status !== 0) {
    totalFailed += 1
  }
  console.log('')
}

console.log('========================================')
if (totalFailed > 0) {
  console.log(`有 ${totalFailed} 个练习未通过，请查看上方 [FAIL] 输出。`)
  process.exit(1)
}
console.log('练习 1~4 全部通过。')
console.log('建议再用浏览器打开 exercise1~4 的 .html 文件亲手操作一遍。')
console.log('========================================')
