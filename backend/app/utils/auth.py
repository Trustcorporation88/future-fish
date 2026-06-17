"""JWT auth for VIP access (admin + client)."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any, Callable, Optional

import jwt
from flask import g, jsonify, request

from ..config import Config


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def load_vip_users() -> dict[str, dict[str, str]]:
    """username -> {password, role, label}"""
    users: dict[str, dict[str, str]] = {}

    if Config.VIP_ADMIN_USERNAME and Config.VIP_ADMIN_PASSWORD:
        users[Config.VIP_ADMIN_USERNAME] = {
            "password": Config.VIP_ADMIN_PASSWORD,
            "role": "admin",
            "label": "Administrador",
        }

    if Config.VIP_CLIENT_USERNAME and Config.VIP_CLIENT_PASSWORD:
        users[Config.VIP_CLIENT_USERNAME] = {
            "password": Config.VIP_CLIENT_PASSWORD,
            "role": "client",
            "label": "Cliente VIP",
        }

    for entry in (Config.VIP_CLIENT_USERS or "").split(","):
        entry = entry.strip()
        if not entry or ":" not in entry:
            continue
        username, password = entry.split(":", 1)
        username = username.strip()
        password = password.strip()
        if username and password:
            users[username] = {
                "password": password,
                "role": "client",
                "label": "Cliente VIP",
            }

    return users


def verify_credentials(username: str, password: str) -> Optional[dict[str, str]]:
    user = load_vip_users().get(username)
    if not user:
        return None
    if not secrets.compare_digest(password, user["password"]):
        return None
    return {"username": username, "role": user["role"], "label": user["label"]}


def create_access_token(username: str, role: str, label: str) -> str:
    payload = {
        "sub": username,
        "role": role,
        "label": label,
        "exp": _utcnow() + timedelta(hours=Config.VIP_JWT_HOURS),
        "iat": _utcnow(),
    }
    return jwt.encode(payload, Config.jwt_secret(), algorithm="HS256")


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    try:
        return jwt.decode(token, Config.jwt_secret(), algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


def _bearer_token() -> Optional[str]:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:].strip()
    return None


def vip_required(f: Callable):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not Config.vip_auth_enabled():
            return f(*args, **kwargs)

        token = _bearer_token()
        if not token:
            return jsonify({"success": False, "error": "VIP login required", "code": "auth_required"}), 401

        payload = decode_access_token(token)
        if not payload:
            return jsonify({"success": False, "error": "Invalid or expired session", "code": "auth_invalid"}), 401

        g.vip_user = {
            "username": payload.get("sub"),
            "role": payload.get("role"),
            "label": payload.get("label"),
        }
        return f(*args, **kwargs)

    return decorated


def register_vip_auth_guard(app):
    """Protect simulation APIs when VIP auth is enabled."""

    @app.before_request
    def require_vip_for_api():
        if not Config.vip_auth_enabled():
            return None

        path = request.path or ""
        if not path.startswith("/api/"):
            return None

        public_prefixes = (
            "/api/auth/",
            "/api/health",
        )
        if any(path.startswith(p) for p in public_prefixes):
            return None

        token = _bearer_token()
        if not token:
            return jsonify({"success": False, "error": "VIP login required", "code": "auth_required"}), 401

        payload = decode_access_token(token)
        if not payload:
            return jsonify({"success": False, "error": "Invalid or expired session", "code": "auth_invalid"}), 401

        g.vip_user = {
            "username": payload.get("sub"),
            "role": payload.get("role"),
            "label": payload.get("label"),
        }
        return None
