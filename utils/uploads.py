import mimetypes
import os
import uuid
from pathlib import Path

from flask import current_app
from werkzeug.utils import secure_filename

from constants import ALLOWED_IMAGE_EXTENSIONS, MAX_IMAGE_SIZE_MB
from utils.supabase_storage import remove_project, storage_enabled, upload_bytes


def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_IMAGE_EXTENSIONS


def save_project_images(project_id: str, files: list) -> tuple[list[str], list[str]]:
    """Sauvegarde les images uploadées. Retourne (filenames_ok, errors).

    En production (Supabase Storage actif), les fichiers vont dans le bucket ;
    sinon sur le disque local (dev). Le nom de fichier stocké en base est
    identique dans les deux cas — les templates ne changent pas.
    """
    use_storage = storage_enabled()

    upload_root = None
    if not use_storage:
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

        if use_storage:
            content_type = (
                file.mimetype
                or mimetypes.guess_type(filename)[0]
                or "application/octet-stream"
            )
            try:
                upload_bytes(f"{project_id}/{filename}", file.read(), content_type)
            except Exception:
                errors.append(f"Échec de l'envoi : {file.filename}")
                continue
        else:
            file.save(upload_root / secure_filename(filename))

        saved.append((filename, idx))

    return saved, errors


def delete_project_images(project_id: str) -> None:
    if storage_enabled():
        try:
            remove_project(project_id)
        except Exception:
            pass

    folder = Path(current_app.instance_path) / "uploads" / project_id
    if folder.exists():
        for f in folder.iterdir():
            f.unlink(missing_ok=True)
        folder.rmdir()
