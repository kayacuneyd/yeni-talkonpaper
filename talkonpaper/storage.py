import logging
from typing import Any, Dict, Optional

import boto3
from botocore.client import Config
from botocore.exceptions import BotoCoreError, NoCredentialsError
from flask import current_app

logger = logging.getLogger(__name__)


def r2_client():
    """
    Lazily create an S3-compatible client for Cloudflare R2.
    """
    cfg = current_app.config
    return boto3.client(
        "s3",
        endpoint_url=cfg.get("R2_ENDPOINT_URL"),
        aws_access_key_id=cfg.get("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=cfg.get("R2_SECRET_ACCESS_KEY"),
        config=Config(signature_version="s3v4"),
    )


def signed_url(object_key: str, expires_in: Optional[int] = None) -> Optional[str]:
    """
    Generate a time-limited signed URL for secure media delivery.
    """
    if not object_key:
        return None

    cfg = current_app.config
    expiry = expires_in or cfg.get("SIGNED_URL_EXPIRATION", 900)

    try:
        client = r2_client()
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": cfg.get("R2_BUCKET_NAME"), "Key": object_key},
            ExpiresIn=expiry,
        )
    except (BotoCoreError, NoCredentialsError) as exc:
        logger.warning("Signed URL generation failed: %s", exc)
        return None


def media_meta(object_key: str) -> Dict[str, Any]:
    """
    Fetch object metadata for display; returns empty dict on failure.
    """
    if not object_key:
        return {}
    try:
        client = r2_client()
        head = client.head_object(Bucket=current_app.config["R2_BUCKET_NAME"], Key=object_key)
        return {
            "size": head.get("ContentLength"),
            "content_type": head.get("ContentType"),
            "last_modified": head.get("LastModified"),
        }
    except Exception as exc:  # noqa: BLE001
        logger.debug("Failed to fetch media metadata for %s: %s", object_key, exc)
        return {}
