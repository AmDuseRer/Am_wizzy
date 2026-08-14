/**
 * 练习 3：子组件下拉框把「选中值」传回父组件（v-model 传 id）
 *
 * 要练会什么：
 *   v-model 不只传 true/false，也可以传分类 id；父组件用 id 做筛选。
 *
 * 运行方式：
 *   cd demo\前端\组件通信_demo
 *   node exercise3-v-model-select.js
 *
 * 对照项目文件：
 *   web/src/components/CategorySelect.vue
 *   web/src/views/TodoListView.vue  （v-model="filters.category_id"）
 */

// ---------------------------------------------------------------------------
// 测试数据（和 HTML 版一致）
// ---------------------------------------------------------------------------
const ALL_ITEMS = [
  { id: 1, name: '写报告', category_id: 1 },
  { id: 2, name: '买菜', category_id: 2 },
  { id: 3, name: '背单词', category_id: 3 },
  { id: 4, name: '开会', category_id: 1 },
]

const CATEGORY_LABEL = {
  1: '工作',
  2: '生活',
  3: '学习',
}

// ---------------------------------------------------------------------------
// 模拟 CategoryPicker 子组件
// ---------------------------------------------------------------------------
function createCategoryPicker(onUpdate) {
  return {
    /** 用户在下拉里选了某个 id（emit update:modelValue） */
    select(categoryId) {
      onUpdate(categoryId)
    },
  }
}

// ---------------------------------------------------------------------------
// 模拟父组件
// ---------------------------------------------------------------------------
function createParent() {
  let categoryId = null

  function filterItems() {
    if (categoryId == null) return []
    return ALL_ITEMS.filter((item) => item.category_id === categoryId).map((item) => item.name)
  }

  const picker = createCategoryPicker((id) => {
    categoryId = id
  })

  return {
    get categoryId() {
      return categoryId
    },
    filterItems,
    picker,
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
console.log('=== 练习 3：v-model 传选中值（分类筛选）===\n')

const parent = createParent()

assert('初始未选分类', parent.categoryId === null)
assertEqual('初始筛选结果为空', parent.filterItems(), [])

parent.picker.select(1)
assert('选「工作」后 categoryId=1', parent.categoryId === 1)
assertEqual('选「工作」筛选结果', parent.filterItems(), ['写报告', '开会'])

parent.picker.select(2)
assertEqual('选「生活」筛选结果', parent.filterItems(), ['买菜'])

parent.picker.select(3)
assertEqual('选「学习」筛选结果', parent.filterItems(), ['背单词'])

parent.picker.select(null)
assert('选「请选择」后 categoryId=null', parent.categoryId === null)
assertEqual('选「请选择」筛选结果为空', parent.filterItems(), [])

// 打印一份可读摘要
console.log('')
console.log('--- 筛选摘要 ---')
for (const [id, label] of Object.entries(CATEGORY_LABEL)) {
  const names = ALL_ITEMS.filter((i) => i.category_id === Number(id)).map((i) => i.name)
  console.log(`  分类 ${label}(id=${id}): ${names.join('、')}`)
}

// ---------------------------------------------------------------------------
// 汇总
// ---------------------------------------------------------------------------
console.log('')
console.log(`结果：${passed} 通过，${failed} 失败`)
if (failed > 0) {
  process.exit(1)
}
console.log('全部通过。浏览器版请打开 exercise3-v-model-select.html 切换下拉框。')
