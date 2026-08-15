#!/bin/bash
# ============================================================
# 小智工具箱（wizzy）一键更新上线脚本
# 适用环境：Ubuntu 云服务器 + GitHub(SSH) + Nginx + Systemd
# 域名示例：webix.top
# 配置文件：/etc/nginx/sites-available/webix.top
#
# 使用方法（在服务器上）：
#   sudo bash /var/www/wizzy/deploy/update.sh
#
# 底层逻辑（务必理解）：
#   【磁盘文件更新】git pull 只把 GitHub 最新源码拉到硬盘
#   【程序真正生效】后端进程驻留内存 → 必须 systemctl restart
#                   前端浏览器访问的是打包结果 → 必须 npm run build
# ============================================================

set -euo pipefail

# ------------------------------------------------------------
# 【可自行修改的配置区】路径 / 分支 / 服务名 都在这里改
# ------------------------------------------------------------
APP_DIR="/var/www/wizzy"                 # 服务器上整仓 Git 目录（含 server/、web/）
GIT_BRANCH="master"                      # 远程分支名
GIT_REMOTE="origin"                      # 远程名，一般不用改
BACKEND_DIR="${APP_DIR}/server"          # FastAPI 后端目录
FRONTEND_DIR="${APP_DIR}/web"            # Vue3 + Vite 前端目录
VENV_BIN="${BACKEND_DIR}/.venv/bin"      # 后端虚拟环境 bin
SERVICE_NAME="wizzy-api"                 # Systemd 服务名（对应 /etc/systemd/system/wizzy-api.service）
# 前端构建产物目录（Vite 默认 dist）。请确认 Nginx root 指向此处，例如：
#   root /var/www/wizzy/web/dist;
FRONTEND_DIST="${FRONTEND_DIR}/dist"

# 默认 false：日常用安全的 git pull
# 改为 true：强制对齐远程（git reset --hard），会丢弃服务器本地未推送改动，有风险！
FORCE_RESET=false

# ------------------------------------------------------------
# 工具函数
# ------------------------------------------------------------
log() {
  echo ""
  echo "========== $* =========="
}

die() {
  echo "【错误】$*" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "未找到命令：$1，请先安装后再运行本脚本"
}

# ------------------------------------------------------------
# 前置检查
# ------------------------------------------------------------
log "[0/6] 前置检查"
[[ "$(id -u)" -eq 0 ]] || die "请使用 root 或 sudo 运行本脚本（Systemd / Nginx 需要权限）"
require_cmd git
require_cmd npm
require_cmd systemctl
require_cmd nginx
[[ -d "${APP_DIR}/.git" ]] || die "目录不是 Git 仓库：${APP_DIR}"
[[ -d "${BACKEND_DIR}" ]] || die "后端目录不存在：${BACKEND_DIR}"
[[ -d "${FRONTEND_DIR}" ]] || die "前端目录不存在：${FRONTEND_DIR}"
[[ -x "${VENV_BIN}/pip" ]] || die "未找到虚拟环境 pip：${VENV_BIN}/pip（请确认 .venv 已创建）"
[[ -x "${VENV_BIN}/uvicorn" ]] || die "未找到 uvicorn：${VENV_BIN}/uvicorn"

# ------------------------------------------------------------
# 1. 进入项目目录
# ------------------------------------------------------------
log "[1/6] 进入项目目录：${APP_DIR}"
cd "${APP_DIR}"

# ------------------------------------------------------------
# 2. Git 同步远程代码（默认 pull；可选强制对齐）
# ------------------------------------------------------------
log "[2/6] 同步 GitHub 最新代码（分支：${GIT_BRANCH}）"
# 备选强制对齐命令（有风险，默认不启用）：
#   git fetch "${GIT_REMOTE}"
#   git reset --hard "${GIT_REMOTE}/${GIT_BRANCH}"
# 风险说明：会丢弃服务器工作区与暂存区的本地修改，且无法靠本仓库轻松找回。
# 规范：禁止在服务器上手改业务源码；只在本地改 → git push → 本脚本更新。
if [[ "${FORCE_RESET}" == "true" ]]; then
  echo "【警告】已启用 FORCE_RESET=true，将强制对齐远程，本地未提交改动会丢失！"
  git fetch "${GIT_REMOTE}"
  git reset --hard "${GIT_REMOTE}/${GIT_BRANCH}"
else
  echo "使用安全方案：git pull"
  git pull "${GIT_REMOTE}" "${GIT_BRANCH}"
fi
echo "当前提交：$(git rev-parse --short HEAD) - $(git log -1 --pretty=%s)"

# ------------------------------------------------------------
# 3. 更新后端 Python 依赖
# ------------------------------------------------------------
log "[3/6] 更新后端依赖（requirements.txt）"
cd "${BACKEND_DIR}"
"${VENV_BIN}/pip" install -r requirements.txt

# ------------------------------------------------------------
# 4. 重启后端（加载新代码）
# ------------------------------------------------------------
log "[4/6] 重启后端服务：${SERVICE_NAME}"
# 仅拉取源码不会生效：uvicorn 进程仍在内存中运行旧代码
systemctl restart "${SERVICE_NAME}"
# 短暂等待后检查是否在跑
sleep 1
if systemctl is-active --quiet "${SERVICE_NAME}"; then
  echo "后端服务状态：active (running)"
else
  echo "【错误】后端服务未成功启动，最近日志如下："
  journalctl -u "${SERVICE_NAME}" -n 40 --no-pager || true
  die "请根据日志排查后重试"
fi

# ------------------------------------------------------------
# 5. 前端安装依赖并打包
# ------------------------------------------------------------
log "[5/6] 前端依赖安装 + 生产打包（Vue3 + Vite）"
cd "${FRONTEND_DIR}"
if [[ -f package-lock.json ]]; then
  echo "检测到 package-lock.json，使用 npm ci（更可复现）"
  npm ci
else
  echo "未检测到 package-lock.json，使用 npm install"
  npm install
fi
npm run build
[[ -d "${FRONTEND_DIST}" ]] || die "构建后未找到产物目录：${FRONTEND_DIST}"
echo "前端产物目录：${FRONTEND_DIST}"

# ------------------------------------------------------------
# 6. 校验并重载 Nginx
# ------------------------------------------------------------
log "[6/6] 校验 Nginx 配置并重载"
# 先 nginx -t，避免坏配置 reload 后站点直接挂掉
nginx -t
systemctl reload nginx
echo "Nginx 已重载"

# ------------------------------------------------------------
# 完成
# ------------------------------------------------------------
log "更新完成"
echo "项目目录：${APP_DIR}"
echo "Git 分支：${GIT_BRANCH} @ $(git -C "${APP_DIR}" rev-parse --short HEAD)"
echo "后端服务：systemctl status ${SERVICE_NAME}"
echo "前端产物：${FRONTEND_DIST}"
echo ""
echo "请用浏览器访问站点（如 https://webix.top）。若页面仍像旧版，请 Ctrl+F5 强刷或清除站点缓存。"
echo "查看后端日志：journalctl -u ${SERVICE_NAME} -n 50 --no-pager"
echo ""
echo "【强制对齐远程】如确需丢弃服务器本地改动，将脚本顶部 FORCE_RESET 改为 true 后再运行（有风险）。"
)
