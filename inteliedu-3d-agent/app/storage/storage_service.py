"""Object storage abstraction for educational videos, thumbnails, and subtitles."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Protocol

import httpx

from app.config import Settings, get_settings
from app.utils.error_handler import DependencyUnavailableError


@dataclass
class StoredAsset:
    """Result of uploading an asset to object storage."""

    provider: str
    object_key: str
    url: str
    local_path: Optional[str] = None


class StorageBackend(Protocol):
    async def upload_file(self, local_path: Path, object_key: str, content_type: str) -> StoredAsset:
        ...

    async def delete_object(self, object_key: str) -> None:
        ...


class LocalStorageBackend:
    """Local filesystem storage serving assets through the FastAPI asset endpoint."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.root = settings.resolved_generated_dir / "storage"
        self.root.mkdir(parents=True, exist_ok=True)

    async def upload_file(self, local_path: Path, object_key: str, content_type: str) -> StoredAsset:
        dest = (self.root / object_key).resolve()
        if not str(dest).startswith(str(self.root.resolve())):
            raise ValueError("Invalid storage object key")
        dest.parent.mkdir(parents=True, exist_ok=True)
        if local_path.resolve() != dest:
            shutil.copy2(local_path, dest)
        url = f"{self.settings.agent_api_prefix.rstrip('/')}/assets/{object_key.lstrip('/')}"
        return StoredAsset(
            provider="local",
            object_key=object_key,
            url=url,
            local_path=str(dest),
        )

    async def delete_object(self, object_key: str) -> None:
        target = (self.root / object_key).resolve()
        if target.is_file() and str(target).startswith(str(self.root.resolve())):
            target.unlink()


class SupabaseStorageBackend:
    """Supabase Storage REST uploader using SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        if not settings.supabase_url or not settings.supabase_service_role_key:
            raise DependencyUnavailableError(
                "Supabase storage selected, but SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY is missing.",
                missing_dependencies=["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"],
            )
        self.base_url = settings.supabase_url.rstrip("/")
        self.bucket = settings.storage_bucket
        self.service_key = settings.supabase_service_role_key

    async def upload_file(self, local_path: Path, object_key: str, content_type: str) -> StoredAsset:
        upload_url = f"{self.base_url}/storage/v1/object/{self.bucket}/{object_key.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.service_key}",
            "apikey": self.service_key,
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        data = local_path.read_bytes()
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(upload_url, headers=headers, content=data)
            resp.raise_for_status()
        public_url = f"{self.base_url}/storage/v1/object/public/{self.bucket}/{object_key.lstrip('/')}"
        return StoredAsset(
            provider="supabase",
            object_key=object_key,
            url=public_url,
            local_path=str(local_path),
        )

    async def delete_object(self, object_key: str) -> None:
        delete_url = f"{self.base_url}/storage/v1/object/{self.bucket}/{object_key.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.service_key}",
            "apikey": self.service_key,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.delete(delete_url, headers=headers)
            if resp.status_code not in (200, 204, 404):
                resp.raise_for_status()


class UnconfiguredCloudStorageBackend:
    """Adapter placeholder for GCS / S3-compatible providers until credentials/SDKs are configured."""

    def __init__(self, provider_name: str, missing: list[str]) -> None:
        self.provider_name = provider_name
        self.missing = missing

    async def upload_file(self, local_path: Path, object_key: str, content_type: str) -> StoredAsset:
        raise DependencyUnavailableError(
            f"{self.provider_name} storage provider selected but required configuration is missing.",
            missing_dependencies=self.missing,
        )

    async def delete_object(self, object_key: str) -> None:
        raise DependencyUnavailableError(
            f"{self.provider_name} storage provider selected but required configuration is missing.",
            missing_dependencies=self.missing,
        )


def build_storage_backend(settings: Optional[Settings] = None) -> StorageBackend:
    cfg = settings or get_settings()
    provider = (cfg.storage_provider or "local").lower()
    if provider == "supabase":
        return SupabaseStorageBackend(cfg)
    if provider == "gcs":
        return UnconfiguredCloudStorageBackend("Google Cloud Storage", ["GCS_BUCKET_NAME", "google-cloud-storage"])
    if provider == "s3":
        return UnconfiguredCloudStorageBackend(
            "S3-Compatible Storage", ["S3_ENDPOINT_URL", "S3_ACCESS_KEY_ID", "S3_SECRET_ACCESS_KEY"]
        )
    return LocalStorageBackend(cfg)

