/**
 * 练习 1：地址和页面的对应关系
 *
 * 要练会什么：
 *   理解 Vue Router 的核心 —— 地址(path) 决定显示哪一页。
 *
 * 运行方式（在仓库根目录 wizzy 下）：
 *   cd demo/前端/路由守卫_demo
 *   node lesson1-route-map.js
 *
 * 或：npm test
 *
 * 无需 npm install（零依赖，纯 Node.js）
 * 无需启动 wizzy 主项目
 */

// ---------------------------------------------------------------------------
// 迷你「路由表」：地址 -> 页面名（对照 web/src/router/index.js 里的 routes）
// ---------------------------------------------------------------------------
const routes = {
  '/login': '登录页',
  '/memos': '备忘录',
  '/passwords': '密码本',
  '/todos': 'TodoList 待办',
  '/users': '用户管理',
}

/**
 * 模拟一次「导航」：根据地址查找对应页面
 * @param {string} path - 例如 '/memos'
 * @returns {{ ok: boolean, page?: string, path?: string, msg?: string }}
 */
function go(path) {
  const page = routes[path]
  if (!page) {
    return { ok: false, msg: '404 找不到页面' }
  }
  return { ok: true, page, path }
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
console.log('=== 练习 1：地址 -> 页面映射 ===\n')

assertEqual(
  '访问 /memos 应显示备忘录',
  go('/memos'),
  { ok: true, page: '备忘录', path: '/memos' },
)

assertEqual(
  '访问 /users 应显示用户管理',
  go('/users'),
  { ok: true, page: '用户管理', path: '/users' },
)

assertEqual(
  '访问 /abc 应返回 404',
  go('/abc'),
  { ok: false, msg: '404 找不到页面' },
)

assertEqual(
  '访问 /login 应显示登录页',
  go('/login'),
  { ok: true, page: '登录页', path: '/login' },
)

// 小挑战：/todos 已在路由表中
assertEqual(
  '访问 /todos 应显示待办列表',
  go('/todos'),
  { ok: true, page: 'TodoList 待办', path: '/todos' },
)

// ---------------------------------------------------------------------------
// 汇总
// ---------------------------------------------------------------------------
console.log('')
console.log(`结果：${passed} 通过，${failed} 失败`)
if (failed > 0) {
  process.exit(1)
}
console.log('全部通过。你可以修改 routes 对象，再运行 node lesson1-route-map.js 观察变化。')
