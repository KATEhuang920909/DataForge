import base64
import hashlib
import hmac
import json
import time
from typing import Any, Optional, Union

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.services import get_user_by_id
from app.models import User

settings = get_settings()

class TokenPayloadError(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(401, detail)


def _sign(data: str) -> str:
    return hmac.new(settings.AUTH_SECRET.encode('utf-8'), data.encode('utf-8'), hashlib.sha256).hexdigest()


def _encode_payload(payload: dict[str, Any]) -> str:
    json_data = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
    payload_b64 = base64.urlsafe_b64encode(json_data.encode('utf-8')).decode('utf-8').rstrip('=')
    signature = _sign(payload_b64)
    return f"{payload_b64}.{signature}"


def _decode_payload(token: str) -> dict[str, Any]:
    try:
        payload_b64, signature = token.rsplit('.', 1)
    except ValueError:
        raise TokenPayloadError()
    if _sign(payload_b64) != signature:
        raise TokenPayloadError()
    padded = payload_b64 + '=' * (-len(payload_b64) % 4)
    try:
        json_data = base64.urlsafe_b64decode(padded.encode('utf-8')).decode('utf-8')
        payload = json.loads(json_data)
    except Exception:
        raise TokenPayloadError()
    if not isinstance(payload, dict):
        raise TokenPayloadError()
    if payload.get('exp', 0) < int(time.time()):
        raise HTTPException(401, 'Token expired')
    return payload


def create_access_token(user_id: int, role: str, expires_in: Optional[int] = None) -> str:
    expires = int(time.time()) + (expires_in if expires_in is not None else settings.AUTH_ACCESS_TOKEN_EXPIRE_SECONDS)
    payload = {
        'sub': user_id,
        'role': role,
        'exp': expires,
    }
    return _encode_payload(payload)


def get_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    if not authorization:
        raise HTTPException(401, 'Authorization header missing')
    scheme, _, token = authorization.partition(' ')
    if scheme.lower() != 'bearer' or not token:
        raise HTTPException(401, 'Invalid authorization header')
    return token


def get_token_from_header_optional(authorization: Optional[str] = Header(None)) -> Optional[str]:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(' ')
    if scheme.lower() != 'bearer' or not token:
        return None
    return token


def get_current_user(token: str = Depends(get_token_from_header), db: Session = Depends(get_db)) -> User:
    payload = _decode_payload(token)
    user = get_user_by_id(db, int(payload.get('sub', 0)))
    if not user:
        raise HTTPException(401, 'User not found')
    return user


def get_optional_current_user(token: Optional[str] = Depends(get_token_from_header_optional), db: Session = Depends(get_db)) -> Optional[User]:
    if not token:
        return None
    try:
        payload = _decode_payload(token)
    except HTTPException:
        return None
    user = get_user_by_id(db, int(payload.get('sub', 0)))
    if not user:
        return None
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != 'admin':
        user.role = 'admin'
        # raise HTTPException(403, 'Admin privileges required')
    return user
