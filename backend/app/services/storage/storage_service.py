from pathlib import Path
from typing import Tuple


class StorageService:
    """Tenant-isolated local/object storage helper."""

    BASE_DIR = Path(__file__).resolve().parents[2] / "storage_data"

    @classmethod
    def _safe_path(cls, tenant_id: str, key: str) -> Path:
        root = (cls.BASE_DIR / tenant_id).resolve()
        target = (root / key).resolve()
        if not str(target).startswith(str(root)):
            raise ValueError("Path traversal detected")
        return target

    @classmethod
    def save_bytes(cls, tenant_id: str, key: str, content: bytes) -> str:
        path = cls._safe_path(tenant_id, key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return str(path)

    @classmethod
    def read_bytes(cls, tenant_id: str, key: str) -> bytes:
        path = cls._safe_path(tenant_id, key)
        return path.read_bytes()

    @classmethod
    def build_key(cls, document_id: str, filename: str) -> str:
        safe_name = Path(filename).name
        return f"documents/{document_id}/{safe_name}"

    @classmethod
    def store_file(cls, tenant_id: str, document_id: str, filename: str, content: bytes) -> Tuple[str, str]:
        key = cls.build_key(document_id, filename)
        saved = cls.save_bytes(tenant_id, key, content)
        return key, saved
