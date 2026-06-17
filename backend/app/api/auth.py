"""VIP login API."""

from flask import Blueprint, jsonify, request

from ..config import Config
from ..utils.auth import create_access_token, decode_access_token, load_vip_users, verify_credentials
from ..utils.locale import t

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/config", methods=["GET"])
def auth_config():
    enabled = Config.vip_auth_enabled()
    return jsonify(
        {
            "success": True,
            "data": {
                "vip_auth_enabled": enabled,
                "vip_label": "Acesso VIP",
            },
        }
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    if not Config.vip_auth_enabled():
        return jsonify({"success": False, "error": "VIP auth is disabled"}), 503

    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"success": False, "error": t("auth.missingCredentials")}), 400

    user = verify_credentials(username, password)
    if not user:
        return jsonify({"success": False, "error": t("auth.invalidCredentials")}), 401

    token = create_access_token(user["username"], user["role"], user["label"])
    return jsonify(
        {
            "success": True,
            "data": {
                "token": token,
                "username": user["username"],
                "role": user["role"],
                "label": user["label"],
                "vip": True,
            },
        }
    )


@auth_bp.route("/me", methods=["GET"])
def me():
    if not Config.vip_auth_enabled():
        return jsonify(
            {
                "success": True,
                "data": {"vip_auth_enabled": False, "authenticated": True, "role": "guest"},
            }
        )

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"success": False, "error": "Not authenticated", "code": "auth_required"}), 401

    payload = decode_access_token(auth[7:].strip())
    if not payload:
        return jsonify({"success": False, "error": "Invalid session", "code": "auth_invalid"}), 401

    return jsonify(
        {
            "success": True,
            "data": {
                "vip_auth_enabled": True,
                "authenticated": True,
                "username": payload.get("sub"),
                "role": payload.get("role"),
                "label": payload.get("label"),
                "vip": True,
            },
        }
    )
