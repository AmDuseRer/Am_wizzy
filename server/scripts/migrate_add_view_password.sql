-- 为已有数据库添加查看专用密码字段（若已存在可忽略报错）
USE wizzy_db;

ALTER TABLE users ADD COLUMN view_password_hash VARCHAR(255) NULL AFTER is_active;
