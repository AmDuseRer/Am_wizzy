/**
 * 练习 4：前端响应拦截器（模拟 request.js 核心逻辑）
 *
 * 要练会什么：
 *   - 所有接口回话结构相同，前端只判断 res.code !== 0
 *   - code === 401 时额外跳转登录页
 *
 * 运行方式（Windows PowerShell）：
 *   cd demo\统一响应与异常_demo
 *   node exercise4.js
 *
 * 依赖：Node.js（https://nodejs.org/）
 *
 * 预期输出（大致）：
 *   [PASS] code=0 -> 返回 data
 *   [PASS] code=404 -> 弹窗 + reject
 *   [PASS] code=401 -> 弹窗 + 跳转 + reject
 *   ---
 *   --- 测试 1 ---
 *   页面拿到: { title: '买菜' }
 *   --- 测试 2 ---
 *   [弹窗] 备忘录不存在
 *   页面收到 reject: 备忘录不存在
 *   --- 测试 3 ---
 *   [弹窗] 请先登录
 *   [跳转] /login
 *   页面收到 reject: 请先登录
 */

// 模拟后端 3 种回话
const responses = [
  { code: 0, message: "success", data: { title: "买菜" } },
  { code: 404, message: "备忘录不存在", data: null },
  { code: 401, message: "请先登录", data: null },
];

function showError(msg) {
  console.log("[弹窗]", msg);
}

function handleResponse(res) {
  if (res.code !== 0) {
    showError(res.message || "请求失败");
    if (res.code === 401) {
      console.log("[跳转] /login");
    }
    throw new Error(res.message || "请求失败");
  }
  return res;
}

// ---------- 自动测试 ----------

function runTest(index, res) {
  console.log(`--- 测试 ${index + 1} ---`);
  try {
    const result = handleResponse(res);
    console.log("页面拿到:", result.data);
    return { ok: true, rejected: false };
  } catch (e) {
    console.log("页面收到 reject:", e.message);
    return { ok: false, rejected: true, message: e.message };
  }
}

function assertPass(label, condition) {
  const status = condition ? "PASS" : "FAIL";
  console.log(`[${status}] ${label}`);
  if (!condition) process.exit(1);
}

function main() {
  const r0 = runTest(0, responses[0]);
  const r1 = runTest(1, responses[1]);
  const r2 = runTest(2, responses[2]);

  console.log("---");

  assertPass("code=0 -> 返回 data", r0.ok && !r0.rejected);
  assertPass("code=404 -> 弹窗 + reject", r1.rejected && r1.message === "备忘录不存在");
  assertPass("code=401 -> 弹窗 + 跳转 + reject", r2.rejected && r2.message === "请先登录");
}

main();
