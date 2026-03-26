from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 数据库
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "company_sys"

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # 存储
    STORAGE_PROVIDER: str = "aliyun"  # aliyun / tencent / qiniu

    # 阿里云OSS
    ALIYUN_ACCESS_KEY_ID: str = ""
    ALIYUN_ACCESS_KEY_SECRET: str = ""
    ALIYUN_OSS_BUCKET: str = ""
    ALIYUN_OSS_ENDPOINT: str = ""

    # 腾讯云COS
    TENCENT_SECRET_ID: str = ""
    TENCENT_SECRET_KEY: str = ""
    TENCENT_COS_BUCKET: str = ""
    TENCENT_COS_REGION: str = ""

    # 七牛云
    QINIU_ACCESS_KEY: str = ""
    QINIU_SECRET_KEY: str = ""
    QINIU_BUCKET: str = ""
    QINIU_DOMAIN: str = ""

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    class Config:
        env_file = ".env"


settings = Settings()
