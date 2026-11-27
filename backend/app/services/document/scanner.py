import os
import re
import struct
import socket
import hashlib
from abc import ABC, abstractmethod
from typing import Tuple, Optional
from app.core.config import settings


class MalwareScanner(ABC):
    """Abstract interface for malware scanning backends."""

    @abstractmethod
    def scan(self, content: bytes, filename: str) -> Tuple[bool, Optional[str]]:
        """Return (is_clean, threat_reason)."""
        raise NotImplementedError


class ClamAVScanner(MalwareScanner):
    """ClamAV clamd scanner using the INSTREAM protocol over TCP or Unix socket. Fails closed."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 3310,
        unix_socket: Optional[str] = None,
        timeout: float = 5.0,
    ) -> None:
        self.host = host
        self.port = port
        self.unix_socket = unix_socket
        self.timeout = timeout

    def scan(self, content: bytes, filename: str) -> Tuple[bool, Optional[str]]:
        try:
            if self.unix_socket and hasattr(socket, "AF_UNIX"):
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                sock.connect(self.unix_socket)
            else:
                sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
                sock.settimeout(self.timeout)

            with sock:
                sock.sendall(b"zINSTREAM\0")
                chunk_size = 8192
                for i in range(0, len(content), chunk_size):
                    chunk = content[i : i + chunk_size]
                    sock.sendall(struct.pack("!I", len(chunk)) + chunk)
                sock.sendall(struct.pack("!I", 0))

                response = b""
                while True:
                    data = sock.recv(4096)
                    if not data:
                        break
                    response += data
                    if b"\0" in response or b"\n" in response:
                        break

            decoded = response.decode("utf-8", errors="replace").strip("\x00\r\n ")
            if decoded.endswith("OK"):
                return True, None
            if "FOUND" in decoded:
                return False, f"ClamAV threat detected: {decoded}"
            return False, f"ClamAV unexpected response (fail-closed): {decoded}"
        except Exception as exc:
            # Fail closed: unreachable scanner quarantines the upload
            return False, f"Malware scanner unreachable (fail-closed quarantine): {type(exc).__name__}"


class DocumentScanner:
    """
    Multi-layer Security Scanner for Customer Uploaded Files:
    1. Magic-byte verification
    2. Extension & MIME consistency
    3. Path traversal neutralization
    4. Full-file heuristic pre-filter (EICAR, executables, XSS, PDF active JS/Launch/EmbeddedFile)
    5. ClamAV clamd scanning behind MalwareScanner interface (fail-closed in staging/production)
    """

    ALLOWED_MIME_TYPES = {
        "application/pdf": [".pdf"],
        "image/png": [".png"],
        "image/jpeg": [".jpg", ".jpeg"],
        "image/webp": [".webp"],
    }

    MAGIC_BYTE_SIGNATURES = [
        (b"%PDF-", "application/pdf"),
        (b"\x89PNG\r\n\x1a\n", "image/png"),
        (b"\xff\xd8\xff", "image/jpeg"),
    ]

    EICAR_SIGNATURE = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    PDF_DANGEROUS_OBJECTS = re.compile(rb"/(JavaScript|JS|Launch|EmbeddedFile)\b", re.IGNORECASE)

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        base = os.path.basename(filename.replace("\\", "/"))
        cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", base)
        safe_name = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", cleaned)
        while ".." in safe_name:
            safe_name = safe_name.replace("..", ".")
        safe_name = safe_name.strip("._")
        return safe_name if safe_name else "uploaded_document"

    @classmethod
    def validate_magic_bytes(cls, content: bytes, filename: str) -> Tuple[bool, Optional[str], Optional[str]]:
        if not content:
            return False, None, "File content is empty."

        detected_mime = None
        for magic, mime in cls.MAGIC_BYTE_SIGNATURES:
            if content.startswith(magic):
                detected_mime = mime
                break

        if not detected_mime and len(content) >= 12:
            if content[0:4] == b"RIFF" and content[8:12] == b"WEBP":
                detected_mime = "image/webp"

        if not detected_mime:
            return False, None, "File signature does not match any approved format (PDF, PNG, JPG, WebP)."

        ext = os.path.splitext(filename.lower())[1]
        valid_exts = cls.ALLOWED_MIME_TYPES.get(detected_mime, [])
        if ext not in valid_exts:
            return (
                False,
                None,
                f"File extension '{ext}' does not match its detected content format '{detected_mime}'. Extension spoofing detected.",
            )

        return True, detected_mime, None

    @classmethod
    def get_scanner(cls) -> Optional[MalwareScanner]:
        if settings.CLAMAV_ENABLED or settings.ENVIRONMENT in ("staging", "production"):
            return ClamAVScanner(
                host=settings.CLAMAV_HOST,
                port=settings.CLAMAV_PORT,
                unix_socket=settings.CLAMAV_SOCKET,
            )
        return None

    @classmethod
    def scan_for_malware(
        cls,
        content: bytes,
        filename: str,
        scanner: Optional[MalwareScanner] = None,
    ) -> Tuple[bool, Optional[str]]:
        # 1. EICAR Standard Antivirus Test Signature (full file)
        if cls.EICAR_SIGNATURE in content:
            return False, "EICAR antivirus test file detected. Quarantined."

        # 2. Executable / binary headers disguised as documents
        if content.startswith(b"MZ"):
            return False, "Disguised Windows executable binary detected (MZ header)."
        if content.startswith(b"\x7fELF"):
            return False, "Disguised Linux executable binary detected (ELF header)."
        if content.startswith(b"\xca\xfe\xba\xbe") or content.startswith(b"\xfe\xed\xfa"):
            return False, "Disguised executable binary detected (Mach-O header)."

        # 3. Full-file embedded script / XSS scan
        lower_content = content.lower()
        if b"<script" in lower_content or b"javascript:" in lower_content:
            return False, "Embedded cross-site script vector detected."

        # 4. Full-file PDF active object check (/JavaScript, /JS, /Launch, /EmbeddedFile)
        if content.startswith(b"%PDF-") or filename.lower().endswith(".pdf"):
            match = cls.PDF_DANGEROUS_OBJECTS.search(content)
            if match:
                obj_name = match.group(0).decode("ascii", errors="replace")
                return False, f"Active PDF object '{obj_name}' detected. Quarantined."

        # 5. External ClamAV MalwareScanner backend (fail-closed)
        active_scanner = scanner or cls.get_scanner()
        if active_scanner is not None:
            return active_scanner.scan(content, filename)

        return True, None

    @classmethod
    def compute_sha256(cls, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()
