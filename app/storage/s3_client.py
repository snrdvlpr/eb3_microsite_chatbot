"""
S3 (or compatible) storage: upload, delete, signed URL.
Local dev: set USE_LOCAL_STORAGE=true to skip S3 and store under ./local_storage.
"""
from pathlib import Path
from typing import Optional

from app.core.config import get_settings


async def upload_file(
    bucket: str,
    key: str,
    body: bytes,
    content_type: Optional[str] = None,
) -> str:
    """Upload bytes to S3 or local storage; returns key (path)."""
    settings = get_settings()
    if settings.use_local_storage:
        return await _upload_local(key, body)
    return await _upload_s3(bucket, key, body, content_type)


async def _upload_local(key: str, body: bytes) -> str:
    base = Path("local_storage")
    path = base / key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    return key


async def _upload_s3(
    bucket: str,
    key: str,
    body: bytes,
    content_type: Optional[str] = None,
) -> str:
    import boto3
    from botocore.config import Config

    settings = get_settings()
    kwargs = {
        "region_name": settings.s3_region,
        "config": Config(signature_version="s3v4"),
    }
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        kwargs["aws_access_key_id"] = settings.aws_access_key_id
        kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
    if settings.s3_endpoint_url:
        kwargs["endpoint_url"] = settings.s3_endpoint_url
    client = boto3.client("s3", **kwargs)
    extra = {}
    if content_type:
        extra["ContentType"] = content_type
    client.put_object(Bucket=bucket, Key=key, Body=body, **extra)
    return key


async def delete_file(bucket: str, key: str) -> None:
    """Delete object from S3 or local storage."""
    settings = get_settings()
    if settings.use_local_storage:
        path = Path("local_storage") / key
        if path.exists():
            path.unlink()
        return
    import boto3
    from botocore.config import Config

    settings = get_settings()
    kwargs = {"region_name": settings.s3_region}
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        kwargs["aws_access_key_id"] = settings.aws_access_key_id
        kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
    if settings.s3_endpoint_url:
        kwargs["endpoint_url"] = settings.s3_endpoint_url
    client = boto3.client("s3", **kwargs)
    client.delete_object(Bucket=bucket, Key=key)


def get_signed_url(bucket: str, key: str, expires_in: int = 3600) -> str:
    """Generate a presigned GET URL (S3 only). For local storage returns a file path."""
    settings = get_settings()
    if settings.use_local_storage:
        return str(Path("local_storage") / key)
    import boto3
    from botocore.config import Config

    settings = get_settings()
    kwargs = {"region_name": settings.s3_region}
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        kwargs["aws_access_key_id"] = settings.aws_access_key_id
        kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
    if settings.s3_endpoint_url:
        kwargs["endpoint_url"] = settings.s3_endpoint_url
    client = boto3.client("s3", **kwargs)
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires_in,
    )
