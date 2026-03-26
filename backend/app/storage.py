"""
云存储抽象层 - 支持阿里云OSS / 腾讯云COS / 七牛云
"""
import uuid
import os
from abc import ABC, abstractmethod
from app.config import settings


class StorageBackend(ABC):
    @abstractmethod
    def upload(self, file_data: bytes, key: str, content_type: str = "") -> str:
        """上传文件, 返回访问URL"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        pass

    @abstractmethod
    def get_url(self, key: str) -> str:
        pass


class AliyunOSSBackend(StorageBackend):
    def __init__(self):
        import oss2
        auth = oss2.Auth(settings.ALIYUN_ACCESS_KEY_ID, settings.ALIYUN_ACCESS_KEY_SECRET)
        self.bucket = oss2.Bucket(auth, settings.ALIYUN_OSS_ENDPOINT, settings.ALIYUN_OSS_BUCKET)

    def upload(self, file_data: bytes, key: str, content_type: str = "") -> str:
        headers = {"Content-Type": content_type} if content_type else {}
        self.bucket.put_object(key, file_data, headers=headers)
        return self.get_url(key)

    def delete(self, key: str) -> bool:
        self.bucket.delete_object(key)
        return True

    def get_url(self, key: str) -> str:
        return f"https://{settings.ALIYUN_OSS_BUCKET}.{settings.ALIYUN_OSS_ENDPOINT}/{key}"


class TencentCOSBackend(StorageBackend):
    def __init__(self):
        from qcloud_cos import CosConfig, CosS3Client
        config = CosConfig(
            Region=settings.TENCENT_COS_REGION,
            SecretId=settings.TENCENT_SECRET_ID,
            SecretKey=settings.TENCENT_SECRET_KEY,
        )
        self.client = CosS3Client(config)
        self.bucket = settings.TENCENT_COS_BUCKET

    def upload(self, file_data: bytes, key: str, content_type: str = "") -> str:
        self.client.put_object(Bucket=self.bucket, Body=file_data, Key=key, ContentType=content_type)
        return self.get_url(key)

    def delete(self, key: str) -> bool:
        self.client.delete_object(Bucket=self.bucket, Key=key)
        return True

    def get_url(self, key: str) -> str:
        return f"https://{self.bucket}.cos.{settings.TENCENT_COS_REGION}.myqcloud.com/{key}"


class QiniuBackend(StorageBackend):
    def __init__(self):
        import qiniu
        self.auth = qiniu.Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
        self.bucket = settings.QINIU_BUCKET
        self.domain = settings.QINIU_DOMAIN

    def upload(self, file_data: bytes, key: str, content_type: str = "") -> str:
        import qiniu
        token = self.auth.upload_token(self.bucket, key)
        ret, info = qiniu.put_data(token, key, file_data)
        if info.status_code != 200:
            raise Exception(f"七牛云上传失败: {info}")
        return self.get_url(key)

    def delete(self, key: str) -> bool:
        import qiniu
        bucket_manager = qiniu.BucketManager(self.auth)
        ret, info = bucket_manager.delete(self.bucket, key)
        return info.status_code == 200

    def get_url(self, key: str) -> str:
        return f"https://{self.domain}/{key}"


class LocalStorageBackend(StorageBackend):
    """本地存储 - 开发/测试用"""
    def __init__(self):
        self.base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
        os.makedirs(self.base_dir, exist_ok=True)

    def upload(self, file_data: bytes, key: str, content_type: str = "") -> str:
        file_path = os.path.join(self.base_dir, key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file_data)
        return self.get_url(key)

    def delete(self, key: str) -> bool:
        file_path = os.path.join(self.base_dir, key)
        if os.path.exists(file_path):
            os.remove(file_path)
        return True

    def get_url(self, key: str) -> str:
        return f"/uploads/{key}"


def get_storage() -> StorageBackend:
    provider = settings.STORAGE_PROVIDER.lower()
    if provider == "aliyun":
        return AliyunOSSBackend()
    elif provider == "tencent":
        return TencentCOSBackend()
    elif provider == "qiniu":
        return QiniuBackend()
    else:
        return LocalStorageBackend()


def generate_storage_key(filename: str, prefix: str = "docs") -> str:
    ext = os.path.splitext(filename)[1] if "." in filename else ""
    unique_name = f"{uuid.uuid4().hex}{ext}"
    return f"{prefix}/{unique_name}"
