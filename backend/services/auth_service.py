import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from config import AUTH_SECRET


TOKEN_DAYS = 7


def hash_password(password):
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120000,
    ).hex()
    return f"{salt}${password_hash}"


def verify_password(password, stored_hash):
    try:
        salt, old_hash = stored_hash.split("$", 1)
    except ValueError:
        return False

    new_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120000,
    ).hex()
    return hmac.compare_digest(new_hash, old_hash)


def _sign(message):
    return hmac.new(
        AUTH_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def create_token(user_id):
    expires_at = int((datetime.now(timezone.utc) + timedelta(days=TOKEN_DAYS)).timestamp())
    message = f"{user_id}:{expires_at}"
    signature = _sign(message)
    raw_token = f"{message}:{signature}".encode("utf-8")
    return base64.urlsafe_b64encode(raw_token).decode("utf-8")


def read_token(token):
    try:
        raw_token = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        user_id_text, expires_at_text, signature = raw_token.split(":", 2)
    except Exception:
        return None

    message = f"{user_id_text}:{expires_at_text}"
    if not hmac.compare_digest(_sign(message), signature):
        return None

    try:
        expires_at = int(expires_at_text)
        user_id = int(user_id_text)
    except ValueError:
        return None

    if expires_at < int(datetime.now(timezone.utc).timestamp()):
        return None

    return user_id
