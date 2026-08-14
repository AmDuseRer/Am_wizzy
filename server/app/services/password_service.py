"""
密码本服务
AES 加密存储，脱敏展示，二次校验查看明文
"""

import json

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessException
from app.core.security import aes_decrypt, aes_encrypt, decode_view_session_token, mask_password, verify_password
from app.models.password_entry import PasswordEntry
from app.models.user import User
from app.schemas.password import PasswordCreateRequest, PasswordRevealRequest, PasswordResponse, PasswordUpdateRequest
from app.services.operation_log_service import log_operation


def to_password_response(entry: PasswordEntry, plain_password: str | None = None) -> PasswordResponse:
    """ORM 转脱敏响应"""
    masked = mask_password(plain_password) if plain_password else "****"
    return PasswordResponse(
        id=entry.id,
        user_id=entry.user_id,
        category_id=entry.category_id,
        site_name=entry.site_name,
        username=entry.username,
        password_masked=masked,
        url=entry.url,
        remark=entry.remark,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


async def list_passwords(
    db: AsyncSession,
    user: User,
    keyword: str | None = None,
    category_id: int | None = None,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[PasswordResponse], int]:
    """分页查询密码条目（脱敏）"""
    query = select(PasswordEntry).where(PasswordEntry.user_id == user.id)
    count_query = select(func.count(PasswordEntry.id)).where(PasswordEntry.user_id == user.id)

    if keyword:
        kw_filter = or_(
            PasswordEntry.site_name.contains(keyword),
            PasswordEntry.username.contains(keyword),
        )
        query = query.where(kw_filter)
        count_query = count_query.where(kw_filter)

    if category_id is not None:
        query = query.where(PasswordEntry.category_id == category_id)
        count_query = count_query.where(PasswordEntry.category_id == category_id)

    total = (await db.execute(count_query)).scalar() or 0
    query = query.order_by(PasswordEntry.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    entries = list(result.scalars().all())
    return [to_password_response(e) for e in entries], total


async def get_password_entry(db: AsyncSession, user: User, entry_id: int) -> PasswordEntry:
    """获取单条密码条目"""
    result = await db.execute(
        select(PasswordEntry).where(PasswordEntry.id == entry_id, PasswordEntry.user_id == user.id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise BusinessException("密码条目不存在", code=404)
    return entry


async def create_password(db: AsyncSession, user: User, req: PasswordCreateRequest) -> PasswordResponse:
    """创建密码条目"""
    entry = PasswordEntry(
        user_id=user.id,
        site_name=req.site_name,
        username=req.username,
        password_enc=aes_encrypt(req.password),
        url=req.url,
        remark=req.remark,
        category_id=req.category_id,
    )
    db.add(entry)
    await db.flush()
    return to_password_response(entry)


async def update_password(
    db: AsyncSession, user: User, entry_id: int, req: PasswordUpdateRequest
) -> PasswordResponse:
    """更新密码条目"""
    entry = await get_password_entry(db, user, entry_id)
    if req.site_name is not None:
        entry.site_name = req.site_name
    if req.username is not None:
        entry.username = req.username
    if req.password is not None:
        entry.password_enc = aes_encrypt(req.password)
    if req.url is not None:
        entry.url = req.url
    if req.remark is not None:
        entry.remark = req.remark
    if req.category_id is not None:
        entry.category_id = req.category_id
    return to_password_response(entry)


async def delete_password(db: AsyncSession, user: User, entry_id: int, ip: str) -> None:
    """删除密码条目"""
    entry = await get_password_entry(db, user, entry_id)
    await log_operation(db, user, "delete", "password", f"删除密码条目 {entry.site_name}", ip)
    await db.delete(entry)


async def reveal_password(
    db: AsyncSession, user: User, entry_id: int, req: PasswordRevealRequest, ip: str
) -> str:
    """二次校验查看专用密码或查看会话后返回明文"""
    if not user.view_password_hash:
        raise BusinessException("尚未设置查看专用密码", code=400)

    verified = False
    if req.view_session:
        session_user_id = decode_view_session_token(req.view_session)
        if session_user_id == user.id:
            verified = True

    if not verified:
        if not req.view_password:
            raise BusinessException("请输入查看专用密码或提供有效查看会话", code=403)
        if not verify_password(req.view_password, user.view_password_hash):
            raise BusinessException("查看专用密码验证失败", code=403)

    entry = await get_password_entry(db, user, entry_id)
    plain = aes_decrypt(entry.password_enc)
    await log_operation(db, user, "view_password", "password", f"查看密码 {entry.site_name}", ip)
    return plain


async def export_backup(db: AsyncSession, user: User, ip: str) -> str:
    """导出加密备份 JSON"""
    result = await db.execute(select(PasswordEntry).where(PasswordEntry.user_id == user.id))
    entries = list(result.scalars().all())
    data = [
        {
            "site_name": e.site_name,
            "username": e.username,
            "password_enc": e.password_enc,
            "url": e.url,
            "remark": e.remark,
        }
        for e in entries
    ]
    await log_operation(db, user, "export", "password", f"导出 {len(entries)} 条密码备份", ip)
    return json.dumps(data, ensure_ascii=False, indent=2)
