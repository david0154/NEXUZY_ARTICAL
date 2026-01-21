"""Local image storage helper."""

import os
import shutil
import uuid
from pathlib import Path


def save_local_copy(src_path: str, images_dir: Path) -> str:
    """Copy src image to images_dir with unique name; return new absolute path."""
    images_dir.mkdir(parents=True, exist_ok=True)

    ext = os.path.splitext(src_path)[1].lower() or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    dst = images_dir / filename
    shutil.copy2(src_path, dst)
    return str(dst)
