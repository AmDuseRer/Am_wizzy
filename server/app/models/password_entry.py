"""
密码本 ORM 模型
敏感字段 password_enc 使用 AES 加密存储
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, TIMESTAMP, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PasswordEntry(Base):
    """密码本条目表"""

    __tablename__ = "password_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    site_name: Mapped[str] = mapped_column(String(200), nullable=False)
    username: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    password_enc: Mapped[str] = mapped_column(Text, nullable=False)  # AES 加密后的密码
    url: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    remark: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), onupdate=func.now(), nullable=False
    )
