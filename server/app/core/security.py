"""
安全工具模块
提供 Bcrypt 密码哈希、JWT 签发/解析、AES 加解密功能
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import BusinessException

# Bcrypt 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """使用 Bcrypt 对明文密码进行不可逆哈希"""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, username: str, role: str) -> tuple[str, str, datetime]:
    """
    创建 JWT 访问令牌
    返回: (token字符串, jti唯一标识, 过期时间)
    """
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "jti": jti,
        "exp": expire,
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token, jti, expire


def decode_access_token(token: str) -> dict:
    """解析 JWT 令牌，失败时抛出 BusinessException"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise BusinessException("令牌无效或已过期", code=401)


def create_view_session_token(user_id: int) -> str:
    """创建查看密码专用会话令牌，有效期 24 小时"""
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {
        "sub": str(user_id),
        "type": "view_session",
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_view_session_token(token: str) -> int:
    """解析查看密码会话令牌，返回 user_id"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "view_session":
            raise BusinessException("查看会话无效", code=401)
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise BusinessException("查看会话无效或已过期", code=401)


def get_fernet() -> Fernet:
    """获取 Fernet AES 加密实例"""
    if not settings.AES_KEY:
        raise BusinessException("AES 密钥未配置", code=500)
    return Fernet(settings.AES_KEY.encode() if isinstance(settings.AES_KEY, str) else settings.AES_KEY)


def aes_encrypt(plain_text: str) -> str:
    """AES 对称加密，返回 base64 编码字符串"""
    f = get_fernet()
    return f.encrypt(plain_text.encode("utf-8")).decode("utf-8")


def aes_decrypt(cipher_text: str) -> str:
    """AES 对称解密"""
    f = get_fernet()
    try:
        return f.decrypt(cipher_text.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        raise BusinessException("解密失败，数据可能已损坏", code=500)


def mask_password(password: str) -> str:
    """密码脱敏展示，仅保留首尾各一位"""
    if len(password) <= 2:
        return "****"
    return password[0] + "****" + password[-1]
