/**
 * 练习 2：父组件控制子弹窗「开 / 关」（父子 v-model）
 *
 * 要练会什么：
 *   父组件用 v-model 绑定一个变量；子组件（弹窗）通过
 *   props.modelValue + emit('update:modelValue') 和父组件同步。
 *
 * 运行方式：
 *   cd demo\前端\组件通信_demo
 *   node exercise2-v-model-dialog.js
 *
 * 对照项目文件：
 *   web/src/layouts/MainLayout.vue
 *   web/src/components/ChangePasswordDialog.vue
 */

// ---------------------------------------------------------------------------
// 模拟父组件
// ---------------------------------------------------------------------------
function createParent() {
  let visible = false
  return {
    get visible() {
      return visible
    },
    openDialog() {
      visible = true
    },
    /** 父组件收到子组件 emit('update:modelValue', v) 时调用 */
    onUpdateModelValue(v) {
      visible = v
    },
  }
}

// ---------------------------------------------------------------------------
// 模拟子组件 MyDialog（对照 ChangePasswordDialog.vue 里的 computed visible）
// ---------------------------------------------------------------------------
function createMyDialog(parent) {
  return {
    /** 子组件读取 props.modelValue */
    isOpen() {
      return parent.visible
    },
    /** 子组件内点「关闭」：emit('update:modelValue', false) */
    close() {
      parent.onUpdateModelValue(false)
    },
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

// ---------------------------------------------------------------------------
// 测试用例
// ---------------------------------------------------------------------------
console.log('=== 练习 2：父子 v-model（弹窗开关）===\n')

const parent = createParent()
const dialog = createMyDialog(parent)

assert('初始弹窗关闭', !parent.visible && !dialog.isOpen())

parent.openDialog()
assert('父组件点打开后弹窗显示', parent.visible && dialog.isOpen())

dialog.close()
assert('子组件点关闭后弹窗消失', !parent.visible && !dialog.isOpen())

// 负面测试：如果子组件「不 emit」，关不掉
console.log('')
console.log('--- 负面测试：子组件不通知父组件 ---')
const parent2 = createParent()
parent2.openDialog()
// 模拟删掉 emit 的情况：子组件自己以为关了，但父组件不知道
let childLocalVisible = false // 子组件内部错误地只改了自己
assert(
  '不 emit 时父组件 visible 仍为 true（弹窗关不掉）',
  parent2.visible === true && childLocalVisible === false,
  '这就是为什么要 emit("update:modelValue", false)',
)

// ---------------------------------------------------------------------------
// 汇总
// ---------------------------------------------------------------------------
console.log('')
console.log(`结果：${passed} 通过，${failed} 失败`)
if (failed > 0) {
  process.exit(1)
}
console.log('全部通过。浏览器版请打开 exercise2-v-model-dialog.html 点按钮体验。')
