import os
from pathlib import Path


class Config:
    """
    Base configuration tuned for SQLite + Cloudflare R2.
    """

    def __init__(self, instance_path: str):
        base_dir = Path(__file__).resolve().parent.parent
        default_db_path = Path(instance_path) / "talkonpaper.db"

        self.SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
        self.SQLALCHEMY_DATABASE_URI = os.environ.get(
            "DATABASE_URL", f"sqlite:///{default_db_path}"
        )
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.SQLALCHEMY_ENGINE_OPTIONS = {
            "connect_args": {"timeout": 5, "check_same_thread": False}
        }
        self.JSON_SORT_KEYS = False
        self.TEMPLATES_AUTO_RELOAD = True

        # Cloudflare R2 (S3-compatible) settings.
        self.R2_ENDPOINT_URL = os.environ.get("R2_ENDPOINT_URL", "https://api.cloudflare.com")
        self.R2_ACCESS_KEY_ID = os.environ.get("R2_ACCESS_KEY_ID", "")
        self.R2_SECRET_ACCESS_KEY = os.environ.get("R2_SECRET_ACCESS_KEY", "")
        self.R2_BUCKET_NAME = os.environ.get("R2_BUCKET_NAME", "talkonpaper-media")
        self.SIGNED_URL_EXPIRATION = int(os.environ.get("SIGNED_URL_EXPIRATION", "900"))

        # SEO defaults.
        self.DEFAULT_CANONICAL_HOST = os.environ.get(
            "CANONICAL_HOST", "https://talkonpaper.example"
        )
        self.ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*")

        # Feature flags.
        self.ENABLE_AUTODUB_STUB = os.environ.get("ENABLE_AUTODUB_STUB", "1") == "1"
        self.ENABLE_SAMPLE_DATA = os.environ.get("ENABLE_SAMPLE_DATA", "1") == "1"
