"""
应用核心配置模块
从 .env 文件读取数据库、JWT、AES 等配置项
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置类，映射环境变量"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # 数据库
    DATABASE_URL: str = "mysql+aiomysql://wizzy:wizzy123@127.0.0.1:3306/wizzy_db"

    # JWT
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080  # 7 天

    # AES 对称加密
    AES_KEY: str = ""

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # 应用
    APP_NAME: str = "小智工具箱"
    DEBUG: bool = True

    @property
    def cors_origin_list(self) -> list[str]:
        """解析 CORS 来源为列表"""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
