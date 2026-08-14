/**
 * 练习2：Axios 封装与拦截器
 *
 * 运行方式（在项目根目录 wizzy 下）：
 *   cd demo/前端/Axios_demo
 *   npm install
 *   node run-tests.js
 *
 * 或：npm test
 */

import axios from 'axios'

// ---------------------------------------------------------------------------
// 模拟登录态（对应项目里的 authStore.token）
// ---------------------------------------------------------------------------
let fakeToken = null

function setToken(token) {
  fakeToken = token
}

function clearToken() {
  fakeToken = null
}

// ---------------------------------------------------------------------------
// 假后端：返回与 wizzy 项目一致的 { code, data, message }
// ---------------------------------------------------------------------------
function fakeServer(method, url, config = {}) {
  const auth = config.headers?.Authorization || ''
  const hasToken = auth.startsWith('Bearer ')

  if (url === '/secret' && !hasToken) {
    return { code: 401, message: '未登录', data: null }
  }

  if (url === '/secret' && hasToken) {
    return { code: 0, message: 'ok', data: '机密数据' }
  }

  if (url === '/bad') {
    return { code: 500, message: '服务器开小差了', data: null }
  }

  if (method === 'get' && url === '/memos') {
    return {
      code: 0,
      message: 'ok',
      data: {
        items: [
          { id: 1, title: '买牛奶' },
          { id: 2, title: '学 Axios' },
        ],
        total: 2,
      },
    }
  }

  return { code: 404, message: '接口不存在', data: null }
}

// ---------------------------------------------------------------------------
// 第 1 层：封装 request（对应 web/src/utils/request.js）
// ---------------------------------------------------------------------------
const request = axios.create({
  baseURL: '/api',
  timeout: 5000,
})

request.interceptors.request.use((config) => {
  if (fakeToken) {
    config.headers.Authorization = `Bearer ${fakeToken}`
  }

  const tokenStatus = fakeToken ? '已带 token' : '未带 token'
  console.log(`  [请求拦截] ${config.method.toUpperCase()} ${config.baseURL}${config.url}，${tokenStatus}`)

  // 用 adapter 把请求转给假后端（真实项目中这里是发到 FastAPI 服务器）
  config.adapter = async (cfg) => {
    const body = fakeServer(cfg.method, cfg.url, cfg)
    return {
      data: body,
      status: 200,
      config: cfg,
      headers: {},
    }
  }

  return config
})

request.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code !== 0) {
      console.log(`  [响应拦截] 失败 code=${res.code}，message=${res.message}`)
      return Promise.reject(new Error(res.message))
    }
    console.log(`  [响应拦截] 成功，data=${JSON.stringify(res.data)}`)
    return res
  },
  (error) => {
    console.log(`  [响应拦截] 网络异常：${error.message}`)
    return Promise.reject(error)
  }
)

// ---------------------------------------------------------------------------
// 第 2 层：api 函数（对应 web/src/api/memos.js）
// ---------------------------------------------------------------------------
function listMemos() {
  return request.get('/memos')
}

function getSecret() {
  return request.get('/secret')
}

function getBad() {
  return request.get('/bad')
}

// ---------------------------------------------------------------------------
// 测试工具
// ---------------------------------------------------------------------------
let passed = 0
let failed = 0

async function runCase(name, fn, expectSuccess) {
  console.log('')
  console.log(`--- 用例：${name} ---`)
  try {
    const res = await fn()
    if (expectSuccess) {
      console.log(`[OK] ${name}`)
      if (res?.data !== undefined) {
        console.log(`     页面拿到的 data：${JSON.stringify(res.data)}`)
      }
      passed += 1
    } else {
      console.log(`[FAIL] ${name}：预期应失败，但请求成功了`)
      failed += 1
    }
  } catch (error) {
    if (!expectSuccess) {
      console.log(`[OK] ${name}（按预期失败）`)
      console.log(`     捕获错误：${error.message}`)
      passed += 1
    } else {
      console.log(`[FAIL] ${name}：预期应成功，但失败了`)
      console.log(`     错误：${error.message}`)
      failed += 1
    }
  }
}

async function main() {
  console.log('========================================')
  console.log('  Axios 练习2：封装 + 拦截器 自动测试')
  console.log('========================================')

  clearToken()

  await runCase(
    '1. GET /memos（无需登录，应成功）',
    async () => {
      const res = await listMemos()
      if (res.data.total !== 2) {
        throw new Error(`期望 total=2，实际 ${res.data.total}`)
      }
      if (res.data.items[0].title !== '买牛奶') {
        throw new Error('第一条标题不对')
      }
      return res
    },
    true
  )

  await runCase(
    '2. GET /secret（未登录，应失败）',
    () => getSecret(),
    false
  )

  setToken('abc123')

  await runCase(
    '3. GET /secret（已登录，应成功）',
    async () => {
      const res = await getSecret()
      if (res.data !== '机密数据') {
        throw new Error(`期望 data=机密数据，实际 ${res.data}`)
      }
      return res
    },
    true
  )

  await runCase(
    '4. GET /bad（业务 code=500，应失败）',
    () => getBad(),
    false
  )

  console.log('')
  console.log('========================================')
  console.log(`  测试结果：${passed} 通过，${failed} 失败`)
  console.log('========================================')

  if (failed > 0) {
    process.exit(1)
  }
}

main()
