#!/bin/bash
# 小智工具箱一键部署脚本（Ubuntu 22.04）
# 用法: sudo bash install.sh

set -e

APP_DIR="/opt/wizzy"
WEB_DIR="/var/www/wizzy"
DB_NAME="wizzy_db"
DB_USER="wizzy"
DB_PASS="wizzy123"
SERVICE_NAME="wizzy-api"

echo "=== 小智工具箱部署开始 ==="

# 1. 安装系统依赖
echo "[1/7] 安装系统依赖..."
apt-get update
apt-get install -y python3 python3-venv python3-pip nodejs npm nginx mysql-server

# 2. 配置 MySQL
echo "[2/7] 配置 MySQL..."
mysql -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME} DEFAULT CHARACTER SET utf8mb4;"
mysql -e "CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';"
mysql -e "GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"

# 3. 部署后端
echo "[3/7] 部署后端..."
mkdir -p ${APP_DIR}
cp -r ../server/* ${APP_DIR}/
cd ${APP_DIR}
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 生成 AES 密钥
AES_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")

cat > .env << EOF
DATABASE_URL=mysql+aiomysql://${DB_USER}:${DB_PASS}@127.0.0.1:3306/${DB_NAME}
JWT_SECRET=${JWT_SECRET}
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
AES_KEY=${AES_KEY}
CORS_ORIGINS=http://localhost
APP_NAME=小智工具箱
DEBUG=false
EOF

# 初始化数据库
mysql ${DB_NAME} < scripts/init_db.sql
python scripts/seed_data.py

# 4. 配置 systemd 服务
echo "[4/7] 配置 systemd 服务..."
cp ../deploy/systemd/wizzy-api.service /etc/systemd/system/${SERVICE_NAME}.service
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
systemctl start ${SERVICE_NAME}

# 5. 构建前端
echo "[5/7] 构建前端..."
cd ../web
npm ci
npm run build
mkdir -p ${WEB_DIR}
cp -r dist/* ${WEB_DIR}/

# 6. 配置 Nginx
echo "[6/7] 配置 Nginx..."
cp ../deploy/nginx.conf /etc/nginx/sites-available/wizzy
ln -sf /etc/nginx/sites-available/wizzy /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# 7. 完成
echo "[7/7] 部署完成！"
echo "访问地址: http://服务器IP"
echo "预置账号: admin / Admin@123"
echo "API 文档: http://服务器IP/api/docs"
