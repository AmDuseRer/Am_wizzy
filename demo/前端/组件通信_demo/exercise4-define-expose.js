/**
 * 练习 4：父组件「按门铃」叫子组件刷新（defineExpose）
 *
 * 要练会什么：
 *   子组件用 defineExpose 暴露 refresh 方法；
 *   父组件通过 ref.value.refresh() 让子组件重新加载数据。
 *
 * 运行方式：
 *   cd demo\前端\组件通信_demo
 *   node exercise4-define-expose.js
 *
 * 对照项目文件：
 *   web/src/components/CategorySelect.vue  （defineExpose({ refresh })）
 *   web/src/views/TodoListView.vue         （filterCategorySelectRef.value?.refresh()）
 */

// ---------------------------------------------------------------------------
// 假装是后端数据库里的分类
// ---------------------------------------------------------------------------
let db = ['工作', '生活', '学习']

// ---------------------------------------------------------------------------
// 模拟子组件 CategoryList（有 defineExpose）
// ---------------------------------------------------------------------------
function createCategoryListWithExpose() {
  let list = [...db]

  function refresh() {
    list = [...db]
  }

  return {
    getList() {
      return [...list]
    },
    refresh, // 相当于 defineExpose({ refresh })
  }
}

// ---------------------------------------------------------------------------
// 模拟子组件（故意不 expose refresh）
// ---------------------------------------------------------------------------
function createCategoryListWithoutExpose() {
  let list = [...db]

  function refresh() {
    list = [...db]
  }

  return {
    getList() {
      return [...list]
    },
    // 没有 expose refresh
    _internalRefresh: refresh,
  }
}

// ---------------------------------------------------------------------------
// 测试工具
// ---------------------------------------------------------------------------
let passed = 0
let failed = 0

function assert(name, condition, detail = '') {
  if (condition) {
    console.log(`[OK] ${name}`)
    if (detail) console.log(`     ${detail}`)
    passed += 1
  } else {
    console.log(`[FAIL] ${name}`)
    if (detail) console.log(`     ${detail}`)
    failed += 1
  }
}

function assertEqual(name, actual, expected) {
  const a = JSON.stringify(actual)
  const e = JSON.stringify(expected)
  assert(name, a === e, a !== e ? `期望 ${e}，实际 ${a}` : '')
}

// ---------------------------------------------------------------------------
// 测试用例
// ---------------------------------------------------------------------------
console.log('=== 练习 4：defineExpose（父组件叫子组件刷新）===\n')

// 每个测试前重置 db
function resetDb() {
  db = ['工作', '生活', '学习']
}

resetDb()
const child = createCategoryListWithExpose()

assertEqual('初始列表 3 项', child.getList(), ['工作', '生活', '学习'])

// 模拟：在别处新增了分类，但子组件还不知道
db.push('运动')
assertEqual('db 已新增「运动」，但子组件列表未变', child.getList(), ['工作', '生活', '学习'])

child.refresh()
assertEqual('父组件调用 refresh 后列表更新', child.getList(), ['工作', '生活', '学习', '运动'])

console.log('')
console.log('--- 对比：没有 defineExpose 时 ---')
resetDb()
const childNoExpose = createCategoryListWithoutExpose()
db.push('运动')

assertEqual('无 expose：db 变了但子组件列表仍是旧的', childNoExpose.getList(), ['工作', '生活', '学习'])

const canCallRefresh = typeof childNoExpose.refresh === 'function'
assert('无 expose：父组件调不到 refresh', !canCallRefresh, 'childNoExpose.refresh 是 undefined')

// 父组件只能「手动」碰内部（不推荐，真实 Vue 里做不到）
childNoExpose._internalRefresh()
assertEqual('强行刷新后列表才更新', childNoExpose.getList(), ['工作', '生活', '学习', '运动'])

// 模拟 TodoListView 里两个下拉都要刷新的场景
console.log('')
console.log('--- 综合：两个 CategorySelect 都要 refresh ---')
resetDb()
const filterRef = createCategoryListWithExpose()
const dialogRef = createCategoryListWithExpose()

db.push('运动')
assert('新增后两个下拉都还是旧数据', filterRef.getList().length === 3 && dialogRef.getList().length === 3)

filterRef.refresh()
dialogRef.refresh()
assert('分别 refresh 后两个下拉都是 4 项', filterRef.getList().length === 4 && dialogRef.getList().length === 4)

// ---------------------------------------------------------------------------
// 汇总
// ---------------------------------------------------------------------------
console.log('')
console.log(`结果：${passed} 通过，${failed} 失败`)
if (failed > 0) {
  process.exit(1)
}
console.log('全部通过。浏览器版请打开 exercise4-define-expose.html 点按钮对比。')
