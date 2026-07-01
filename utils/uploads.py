import os
import uuid
from pathlib import Path

from flask import current_app
from werkzeug.utils import secure_filename

from constants import ALLOWED_IMAGE_EXTENSIONS, MAX_IMAGE_SIZE_MB


def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_IMAGE_EXTENSIONS


def save_project_images(project_id: str, files: list) -> tuple[list[str], list[str]]:
    """Sauvegarde les images uploadées. Retourne (filenames_ok, errors)."""
    upload_root = Path(current_app.instance_path) / "uploads" / project_id
    upload_root.mkdir(parents=True, exist_ok=True)

    saved = []
    errors = []
    max_bytes = MAX_IMAGE_SIZE_MB * 1024 * 1024

    for idx, file in enumerate(files):
        if not file or not file.filename:
            continue
        if not allowed_file(file.filename):
            errors.append(f"Format non supporté : {file.filename}")
            continue
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        if size > max_bytes:
            errors.append(f"{file.filename} dépasse {MAX_IMAGE_SIZE_MB} Mo.")
            continue

        ext = Path(file.filename).suffix.lower()
        filename = f"{uuid.uuid4().hex}{ext}"
        file.save(upload_root / filename)
        saved.append((filename, idx))

    return saved, errors


def delete_project_images(project_id: str) -> None:
    folder = Path(current_app.instance_path) / "uploads" / project_id
    if folder.exists():
        for f in folder.iterdir():
            f.unlink(missing_ok=True)
        folder.rmdir()
