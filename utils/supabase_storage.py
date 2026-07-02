"""Persistance des images sur Supabase Storage.

Utilisé quand SUPABASE_URL + SUPABASE_SERVICE_KEY sont définis (production).
Sinon, l'app retombe sur le disque local (voir utils/uploads.py) — éphémère
sur Scalingo, à réserver au dev.

On tape directement l'API REST Storage (urllib) : pas de dépendance
supplémentaire et un comportement identique à ce qui a été validé côté API.
"""

import json
import urllib.error
import urllib.request

from flask import current_app


def _config() -> tuple[str, str, str]:
    return (
        current_app.config.get("SUPABASE_URL", "").rstrip("/"),
        current_app.config.get("SUPABASE_SERVICE_KEY", ""),
        current_app.config.get("SUPABASE_STORAGE_BUCKET", ""),
    )


def storage_enabled() -> bool:
    url, key, bucket = _config()
    return bool(url and key and bucket)


def _headers(key: str, extra: dict | None = None) -> dict:
    headers = {"Authorization": f"Bearer {key}", "apikey": key}
    if extra:
        headers.update(extra)
    return headers


def public_url(path: str) -> str:
    url, _, bucket = _config()
    return f"{url}/storage/v1/object/public/{bucket}/{path}"


def upload_bytes(path: str, data: bytes, content_type: str) -> None:
    """Envoie un objet dans le bucket (upsert). Lève en cas d'échec."""
    url, key, bucket = _config()
    req = urllib.request.Request(
        f"{url}/storage/v1/object/{bucket}/{path}",
        data=data,
        method="POST",
        headers=_headers(key, {"Content-Type": content_type, "x-upsert": "true"}),
    )
    urllib.request.urlopen(req, timeout=30)


def _list(project_id: str) -> list[dict]:
    url, key, bucket = _config()
    req = urllib.request.Request(
        f"{url}/storage/v1/object/list/{bucket}",
        data=json.dumps({"prefix": f"{project_id}/", "limit": 1000}).encode(),
        method="POST",
        headers=_headers(key, {"Content-Type": "application/json"}),
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def remove_project(project_id: str) -> None:
    """Supprime tous les objets d'un projet. No-op si aucun."""
    url, key, bucket = _config()
    paths = [f"{project_id}/{obj['name']}" for obj in _list(project_id) if obj.get("name")]
    if not paths:
        return
    req = urllib.request.Request(
        f"{url}/storage/v1/object/{bucket}",
        data=json.dumps({"prefixes": paths}).encode(),
        method="DELETE",
        headers=_headers(key, {"Content-Type": "application/json"}),
    )
    urllib.request.urlopen(req, timeout=30)
