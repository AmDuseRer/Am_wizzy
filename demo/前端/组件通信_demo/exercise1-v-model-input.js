/**
 * 练习 1：输入框和文字「绑在一起」（v-model 基础）
 *
 * 要练会什么：
 *   v-model = 界面上的值 和 变量 自动同步，改一边另一边跟着变。
 *
 * 运行方式（在仓库根目录 wizzy 下）：
 *   cd demo\前端\组件通信_demo
 *   node exercise1-v-model-input.js
 *
 * 或：npm run exercise1
 *
 * 无需 npm install（零依赖，纯 Node.js）
 * 无需浏览器、后端或 wizzy 主项目
 *
 * 对照项目文件：
 *   web/src/views/LoginView.vue  （表单 v-model）
 */

// ---------------------------------------------------------------------------
// 模拟 Vue 的 ref：一个会变的盒子
// ---------------------------------------------------------------------------
function createRef(initial) {
  let value = initial
  return {
    get() {
      return value
    },
    set(v) {
      value = v
    },
  }
}

/**
 * 模拟 <input v-model="message" />
 * 在 Vue 里：输入框的值 和 message 始终一致
 */
function createInputVModel(messageRef) {
  return {
    /** 用户在输入框里打字 */
    type(text) {
      messageRef.set(text)
    },
    /** 页面上显示的文字（和输入框内容相同） */
    displayText() {
      return messageRef.get()
    },
    /** 字符数 */
    length() {
      return messageRef.get().length
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
console.log('=== 练习 1：v-model 基础（输入框与文字同步）===\n')

const message = createRef('')
const input = createInputVModel(message)

// 初始状态
assert('初始 message 为空', message.get() === '', `message="${message.get()}"`)
assert('初始字符数为 0', input.length() === 0)

// 模拟用户输入 hello
input.type('hello')
assert('输入 hello 后 display 同步', input.displayText() === 'hello', `display="${input.displayText()}"`)
assert('输入 hello 后字符数为 5', input.length() === 5)

// 模拟用户清空
input.type('')
assert('清空后 display 为空', input.displayText() === '')
assert('清空后字符数为 0', input.length() === 0)

// 模拟输入中文
input.type('你好')
assert('输入中文后 display 同步', input.displayText() === '你好')
assert('输入中文后字符数为 2', input.length() === 2)

// ---------------------------------------------------------------------------
// 汇总
// ---------------------------------------------------------------------------
console.log('')
console.log(`结果：${passed} 通过，${failed} 失败`)
if (failed > 0) {
  process.exit(1)
}
console.log('全部通过。浏览器版请打开 exercise1-v-model-input.html 亲手输入试试。')
