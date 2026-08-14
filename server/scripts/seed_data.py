"""
数据库种子数据脚本
创建预置用户（admin/user）及示例业务数据
运行方式: python scripts/seed_data.py
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 将 server 目录加入 path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from cryptography.fernet import Fernet
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from app.core.config import settings
from app.core.database import Base
from app.core.security import aes_encrypt, hash_password
from app.models.category import Category
from app.models.memo import Memo
from app.models.password_entry import PasswordEntry
from app.models.todo import Todo
from app.models.user import User

if not settings.AES_KEY:
    print("错误: 请先在 .env 中配置 AES_KEY")
    print('生成命令: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"')
    sys.exit(1)

try:
    Fernet(settings.AES_KEY.encode())
except ValueError:
    print("错误: AES_KEY 格式无效，必须是 Fernet 密钥（44 位 url-safe base64 字符串）")
    print('生成命令: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"')
    sys.exit(1)


async def seed():
    """执行种子数据写入"""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with Session() as db:
            # 检查是否已有数据
            result = await db.execute(select(User).where(User.username == "admin"))
            if result.scalar_one_or_none():
                print("种子数据已存在，跳过")
                return

            # 创建用户
            admin = User(username="admin", password_hash=hash_password("Admin@123"), role="admin")
            user = User(username="user", password_hash=hash_password("User@123"), role="user")
            db.add_all([admin, user])
            await db.flush()

            for u, prefix in [(admin, "admin"), (user, "user")]:
                # 分类
                memo_cat = Category(user_id=u.id, module_type="memo", name="默认分类")
                pwd_cat = Category(user_id=u.id, module_type="password", name="常用网站")
                todo_cat = Category(user_id=u.id, module_type="todo", name="工作")
                db.add_all([memo_cat, pwd_cat, todo_cat])
                await db.flush()

                # 备忘录
                memos = [
                    Memo(user_id=u.id, category_id=memo_cat.id, title=f"{prefix} 欢迎备忘录",
                         content=f"欢迎使用小智工具箱！这是 {prefix} 用户的示例备忘录。", is_pinned=True),
                    Memo(user_id=u.id, category_id=memo_cat.id, title="项目计划",
                         content="1. 完成前端开发\n2. 完成后端 API\n3. 部署上线"),
                    Memo(user_id=u.id, title="购物清单", content="牛奶、面包、鸡蛋"),
                ]
                db.add_all(memos)

                # 密码本
                passwords = [
                    PasswordEntry(user_id=u.id, category_id=pwd_cat.id, site_name="GitHub",
                                  username=f"{prefix}@example.com", password_enc=aes_encrypt("GitHubPass123"),
                                  url="https://github.com", remark="代码托管"),
                    PasswordEntry(user_id=u.id, category_id=pwd_cat.id, site_name="邮箱",
                                  username=f"{prefix}@mail.com", password_enc=aes_encrypt("MailPass456"),
                                  url="https://mail.example.com", remark="工作邮箱"),
                ]
                db.add_all(passwords)

                # 待办
                now = datetime.now()
                todos = [
                    Todo(user_id=u.id, category_id=todo_cat.id, title="完成项目文档",
                         description="编写 README 和 API 文档", priority="high", status="in_progress",
                         due_at=now + timedelta(days=3)),
                    Todo(user_id=u.id, category_id=todo_cat.id, title="代码审查",
                         description="审查 PR #42", priority="medium", status="pending",
                         due_at=now + timedelta(days=7)),
                    Todo(user_id=u.id, title="已逾期任务示例",
                         description="这是一个逾期示例", priority="high", status="pending",
                         due_at=now - timedelta(days=2)),
                    Todo(user_id=u.id, title="已完成任务",
                         description="学习 Vue3", priority="low", status="completed",
                         due_at=now - timedelta(days=5), completed_at=now - timedelta(days=1)),
                ]
                db.add_all(todos)

            await db.commit()
            print("种子数据写入成功！")
            print("预置账号: admin / Admin@123, user / User@123")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
