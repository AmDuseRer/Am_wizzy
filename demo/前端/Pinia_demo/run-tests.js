/**
 * Pinia 练习 1~3：共用仓库 / 持久化 / defineStore 骨架
 *
 * 运行方式（在仓库根目录 wizzy 下）：
 *   cd demo/前端/Pinia_demo
 *   node run-tests.js
 *
 * 或：npm test
 *
 * 无需 npm install（零依赖，纯 Node.js）
 * 无需启动 wizzy 主项目
 */

// ---------------------------------------------------------------------------
// Node 里没有浏览器 localStorage，用内存版模拟（练习2 用）
// ---------------------------------------------------------------------------
const memoryStorage = new Map()

const localStorage = {
  setItem(key, value) {
    memoryStorage.set(key, String(value))
  },
  getItem(key) {
    return memoryStorage.has(key) ? memoryStorage.get(key) : null
  },
  removeItem(key) {
    memoryStorage.delete(key)
  },
  clear() {
    memoryStorage.clear()
  },
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

function section(title) {
  console.log('')
  console.log('========================================')
  console.log(`  ${title}`)
  console.log('========================================')
}

// ---------------------------------------------------------------------------
// 练习1：全站共用一本「记事本」（模拟 Pinia 仓库）
// 要练会：多个模块读同一份数据，改一处处处同步
// ---------------------------------------------------------------------------
function exercise1() {
  section('练习1：共用仓库（多个模块读同一份数据）')

  const authBox = {
    token: '',
    userInfo: null,
  }

  function loginPageLogin() {
    authBox.token = 'fake-token-abc'
    authBox.userInfo = { username: 'admin', role: 'admin' }
    console.log('  [登录页] 登录成功', JSON.stringify(authBox))
  }

  function requestModuleGetToken() {
    const token = authBox.token
    console.log('  [请求模块] 拿到的 token:', token || '(空)')
    return token
  }

  function sidebarCheckAdmin() {
    const isAdmin = authBox.userInfo?.role === 'admin'
    console.log('  [侧边栏] 是否管理员:', isAdmin)
    return isAdmin
  }

  loginPageLogin()
  const token = requestModuleGetToken()
  const isAdmin = sidebarCheckAdmin()

  assert(
    '1.1 登录后三处都能读到 token',
    token === 'fake-token-abc',
    `token=${token}`
  )
  assert(
    '1.2 登录后侧边栏识别为管理员',
    isAdmin === true,
    'isAdmin=true'
  )

  authBox.token = ''
  authBox.userInfo = null
  const tokenAfterClear = requestModuleGetToken()
  assert(
    '1.3 清空 token 后请求模块读到空（未登录）',
    tokenAfterClear === '',
    'token 为空字符串'
  )
}

// ---------------------------------------------------------------------------
// 练习2：持久化 = 刷新后从 localStorage 恢复
// 要练会：内存会丢，localStorage 里的可以恢复
// ---------------------------------------------------------------------------
function exercise2() {
  section('练习2：持久化（模拟刷新后恢复登录态）')

  const STORAGE_KEY = 'wizzy-auth-practice'

  localStorage.clear()

  const data = {
    token: 'persist-token-123',
    userInfo: { username: 'user' },
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
  console.log('  [写入] 已保存到 localStorage')

  let memory = null
  console.log('  [刷新] 模拟页面刷新，内存清空 ->', memory)

  const raw = localStorage.getItem(STORAGE_KEY)
  memory = raw ? JSON.parse(raw) : null
  console.log('  [恢复] 从 localStorage 读回 ->', JSON.stringify(memory))

  assert(
    '2.1 恢复后 token 正确',
    memory?.token === 'persist-token-123',
    `token=${memory?.token}`
  )
  assert(
    '2.2 恢复后用户名正确',
    memory?.userInfo?.username === 'user',
    `username=${memory?.userInfo?.username}`
  )

  localStorage.removeItem(STORAGE_KEY)
  const gone = localStorage.getItem(STORAGE_KEY)
  console.log('  [删除] 清除 localStorage 后 ->', gone)

  assert(
    '2.3 删除后无法恢复（相当于登出/清缓存）',
    gone === null,
    'getItem 返回 null'
  )
}

// ---------------------------------------------------------------------------
// 练习3：手写迷你 defineStore（state + getters + actions）
// 要练会：对应 stores/auth.js 的三块结构
// ---------------------------------------------------------------------------
function createMiniStore(initialState, getters, actions) {
  const state = { ...initialState }

  const store = {
    get state() {
      return state
    },
    ...Object.fromEntries(
      Object.entries(getters).map(([name, fn]) => [name, () => fn(state)])
    ),
    ...Object.fromEntries(
      Object.entries(actions).map(([name, fn]) => [name, (...args) => fn(state, ...args)])
    ),
  }

  return store
}

function exercise3() {
  section('练习3：迷你 defineStore（state / getters / actions）')

  const authStore = createMiniStore(
    { token: '', userInfo: null },
    {
      isLoggedIn: (s) => !!s.token,
      isAdmin: (s) => s.userInfo?.role === 'admin',
      username: (s) => s.userInfo?.username || '',
    },
    {
      login(state, user) {
        state.token = 'token-' + user.username
        state.userInfo = user
      },
      logout(state) {
        state.token = ''
        state.userInfo = null
      },
    }
  )

  console.log('  [初始] isLoggedIn:', authStore.isLoggedIn())

  assert(
    '3.1 初始未登录',
    authStore.isLoggedIn() === false,
    'isLoggedIn=false'
  )

  authStore.login({ username: 'admin', role: 'admin' })
  console.log('  [admin 登录] isLoggedIn:', authStore.isLoggedIn(), 'isAdmin:', authStore.isAdmin())

  assert(
    '3.2 admin 登录后 isLoggedIn 为 true',
    authStore.isLoggedIn() === true,
    'isLoggedIn=true'
  )
  assert(
    '3.3 admin 登录后 isAdmin 为 true',
    authStore.isAdmin() === true,
    'isAdmin=true'
  )

  authStore.logout()
  console.log('  [登出] isLoggedIn:', authStore.isLoggedIn())

  assert(
    '3.4 登出后 isLoggedIn 为 false',
    authStore.isLoggedIn() === false,
    'isLoggedIn=false'
  )

  authStore.login({ username: 'user', role: 'user' })
  console.log('  [user 登录] isLoggedIn:', authStore.isLoggedIn(), 'isAdmin:', authStore.isAdmin())

  assert(
    '3.5 user 登录后 isLoggedIn 为 true',
    authStore.isLoggedIn() === true,
    'isLoggedIn=true'
  )
  assert(
    '3.6 user 登录后 isAdmin 为 false',
    authStore.isAdmin() === false,
    'isAdmin=false'
  )
}

// ---------------------------------------------------------------------------
// 入口
// ---------------------------------------------------------------------------
function main() {
  console.log('========================================')
  console.log('  Pinia 练习 1~3 自动测试（Node 版）')
  console.log('========================================')

  exercise1()
  exercise2()
  exercise3()

  console.log('')
  console.log('========================================')
  console.log(`  测试结果：${passed} 通过，${failed} 失败`)
  console.log('========================================')
  console.log('')
  console.log('练完请对照主项目：')
  console.log('  web/src/stores/auth.js   <- 练习3 的 defineStore 真身')
  console.log('  web/src/main.js          <- persist 插件注册')
  console.log('  web/src/utils/request.js <- 练习1 请求模块读 token')

  if (failed > 0) {
    process.exit(1)
  }
}

main()
