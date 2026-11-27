import base64
import hashlib
import hmac
import json
import time
from typing import Dict, Any, Optional
from datetime import timedelta
from app.core.config import settings


def hash_password(password: str) -> str:
    salt = hashlib.sha256(settings.SECRET_KEY.encode()).hexdigest()[:16]
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"{salt}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt, expected_hex = hashed_password.split("$", 1)
        key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000)
        return hmac.compare_digest(key.hex(), expected_hex)
    except Exception:
        return False


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _base64url_decode(data: str) -> bytes:
    padding = "=" * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(
    subject: str,
    tenant_id: str,
    role: str,
    email: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    now = int(time.time())
    if expires_delta:
        exp = now + int(expires_delta.total_seconds())
    else:
        exp = now + (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    header = {"alg": settings.ALGORITHM, "typ": "JWT"}
    payload = {
        "sub": subject,
        "tenant_id": tenant_id,
        "role": role,
        "email": email,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": now,
        "exp": exp,
    }

    header_bytes = json.dumps(header, separators=(",", ":")).encode("utf-8")
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")

    encoded_header = _base64url_encode(header_bytes)
    encoded_payload = _base64url_encode(payload_bytes)

    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    signature = hmac.new(settings.SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    encoded_signature = _base64url_encode(signature)

    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        if settings.ENVIRONMENT in ("production", "staging") or not settings.ALLOW_DEV_STATIC_JWT_SECRET:
            # Production/staging must validate RS256 tokens against Keycloak JWKS (never static shared secret)
            return None

        parts = token.split(".")
        if len(parts) != 3:
            return None

        encoded_header, encoded_payload, encoded_signature = parts
        if not encoded_signature:
            return None

        header = json.loads(_base64url_decode(encoded_header).decode("utf-8"))
        alg = header.get("alg")
        if not alg or str(alg).lower() == "none" or alg != settings.ALGORITHM:
            return None
        if header.get("typ") != "JWT":
            return None

        signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
        expected_sig = hmac.new(settings.SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
        actual_sig = _base64url_decode(encoded_signature)

        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        payload_bytes = _base64url_decode(encoded_payload)
        payload = json.loads(payload_bytes.decode("utf-8"))

        # Verify expiration, issuer, and audience
        if payload.get("exp", 0) < int(time.time()):
            return None
        if payload.get("iss") != settings.JWT_ISSUER:
            return None
        if payload.get("aud") != settings.JWT_AUDIENCE:
            return None

        return payload
    except Exception:
        return None
