"""为 users 表添加 view_password_hash 字段（幂等）"""

import asyncio

from sqlalchemy import text

from app.core.database import engine


async def migrate() -> None:
    async with engine.begin() as conn:
        result = await conn.execute(
            text(
                "SELECT COUNT(*) FROM information_schema.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'users' "
                "AND COLUMN_NAME = 'view_password_hash'"
            )
        )
        if result.scalar():
            print("Column view_password_hash already exists")
            return

        await conn.execute(
            text(
                "ALTER TABLE users ADD COLUMN view_password_hash VARCHAR(255) NULL AFTER is_active"
            )
        )
        print("Column view_password_hash added successfully")


if __name__ == "__main__":
    asyncio.run(migrate())
