"""
分类 ORM 模型
备忘录、密码本、待办共用分类表，通过 module_type 区分
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Category(Base):
    """分类表"""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    module_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # memo / password / todo
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
