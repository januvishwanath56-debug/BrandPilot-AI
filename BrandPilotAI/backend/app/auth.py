"""Optional private pilot identity. Demo mode remains explicitly unauthenticated."""
import base64
import hashlib
import hmac
import json
import os
import secrets
import time
import threading
from fastapi import HTTPException

_attempts = {}
_lock = threading.Lock()


def reserve_login(username):
    # Process-local guard for the single-instance pilot; distributed protection
    # belongs at the reverse proxy before deploying multiple workers.
    now = time.monotonic()
    with _lock:
        for key in list(_attempts):
            if now - _attempts[key][0] > 900:
                del _attempts[key]
        start, count = _attempts.get(username, (now, 0))
        if count >= 12 or len(_attempts) >= 10000:
            raise HTTPException(429, 'Too many sign-in attempts. Retry in 15 minutes.')
        _attempts[username] = (start, count + 1)


def private_mode():
    return os.getenv('AUTH_MODE', 'demo') == 'private'


def password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 600000).hex()
    return f'{salt}${digest}'


def accounts():
    return json.loads(os.getenv('AUTH_USERS_JSON', '{}'))


def secret():
    value = os.getenv('AUTH_SECRET', '')
    if len(value) < 32:
        raise RuntimeError('Private mode requires AUTH_SECRET of at least 32 characters')
    return value.encode()


def login(username, password):
    reserve_login(username)
    user = accounts().get(username)
    stored = (user or {}).get('password_hash', 'missing$invalid')
    candidate = password_hash(password, stored.split('$')[0])
    if not user or not hmac.compare_digest(candidate, stored):
        raise HTTPException(401, 'Invalid username or password')
    payload = base64.urlsafe_b64encode(json.dumps({'sub': username, 'exp': int(time.time()) + 28800}).encode()).decode()
    signature = hmac.new(secret(), payload.encode(), hashlib.sha256).hexdigest()
    return {'token': f'{payload}.{signature}', 'role': user['role'], 'actor': username}


def identity(authorization):
    try:
        payload, signature = authorization.removeprefix('Bearer ').split('.')
        expected = hmac.new(secret(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError()
        claims = json.loads(base64.urlsafe_b64decode(payload))
        user = accounts().get(claims['sub'])
        if not user or claims['exp'] <= time.time() or user['role'] not in ('creator', 'reviewer', 'manager'):
            raise ValueError()
        return claims['sub'], user['role']
    except (ValueError, KeyError, TypeError):
        raise HTTPException(401, 'Sign in to your private workspace')
