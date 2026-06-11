"""Supabase Storage service (service role) with in-memory fallback for tests."""

from __future__ import annotations

import json
from typing import Any

import httpx
from rpg_platform.config import get_settings

_memory_store: dict[str, dict[str, bytes]] = {}


class StorageService:
    def __init__(self, *, use_memory: bool = False) -> None:
        self._use_memory = use_memory
        self._settings = get_settings()

    def _bucket_key(self, bucket: str, path: str) -> str:
        return f"{bucket}:{path}"

    async def put_json(
        self,
        bucket: str,
        path: str,
        data: dict[str, Any],
        *,
        content_type: str = "application/json",
    ) -> bytes:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        await self.put_bytes(bucket, path, payload, content_type=content_type)
        return payload

    async def put_bytes(
        self,
        bucket: str,
        path: str,
        data: bytes,
        *,
        content_type: str = "application/octet-stream",
    ) -> None:
        if self._use_memory:
            _memory_store.setdefault(bucket, {})[path] = data
            return

        url = f"{self._settings.supabase_url}/storage/v1/object/{bucket}/{path}"
        headers = {
            "Authorization": f"Bearer {self._settings.supabase_service_role_key}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, content=data, headers=headers)
            if response.status_code >= 400:
                raise RuntimeError(f"Storage upload failed: {response.status_code} {response.text}")

    async def get_bytes(self, bucket: str, path: str) -> bytes:
        if self._use_memory:
            bucket_data = _memory_store.get(bucket, {})
            if path not in bucket_data:
                raise FileNotFoundError(path)
            return bucket_data[path]

        url = f"{self._settings.supabase_url}/storage/v1/object/{bucket}/{path}"
        headers = {"Authorization": f"Bearer {self._settings.supabase_service_role_key}"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 404:
                raise FileNotFoundError(path)
            response.raise_for_status()
            return response.content

    async def get_json(self, bucket: str, path: str) -> dict[str, Any]:
        raw = await self.get_bytes(bucket, path)
        return json.loads(raw.decode("utf-8"))

    async def delete(self, bucket: str, path: str) -> None:
        if self._use_memory:
            _memory_store.get(bucket, {}).pop(path, None)
            return

        url = f"{self._settings.supabase_url}/storage/v1/object/{bucket}/{path}"
        headers = {"Authorization": f"Bearer {self._settings.supabase_service_role_key}"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            await client.delete(url, headers=headers)

    async def create_signed_url(self, bucket: str, path: str, expires_in: int = 3600) -> str:
        if self._use_memory:
            return f"memory://{bucket}/{path}?expires={expires_in}"

        url = f"{self._settings.supabase_url}/storage/v1/object/sign/{bucket}/{path}"
        headers = {
            "Authorization": f"Bearer {self._settings.supabase_service_role_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json={"expiresIn": expires_in})
            response.raise_for_status()
            data = response.json()
            return data.get("signedURL") or data.get("signedUrl", "")


def clear_memory_storage() -> None:
    _memory_store.clear()
