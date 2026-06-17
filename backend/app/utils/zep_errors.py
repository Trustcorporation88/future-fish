"""Helpers for Zep Cloud API error messages."""


def format_zep_error(exc: Exception) -> str:
    text = str(exc)
    lower = text.lower()
    if "401" in text or "unauthorized" in lower:
        return (
            "ZEP_API_KEY inválida ou expirada. "
            "Gere uma nova chave em https://app.getzep.com e atualize no Railway → Variables."
        )
    if "403" in text or "forbidden" in lower:
        return "Acesso negado à API Zep (403). Verifique o plano e permissões da ZEP_API_KEY."
    if "429" in text or "rate limit" in lower:
        return "Limite de requisições da API Zep excedido. Tente novamente em alguns minutos."
    return text[:500] if len(text) > 500 else text


def verify_zep_api_key(api_key: str | None) -> str | None:
    """Return error message if the Zep API key is missing or rejected."""
    if not api_key:
        return "ZEP_API_KEY não configurada."

    try:
        from zep_cloud.client import Zep

        client = Zep(api_key=api_key)
        client.graph.list_all(limit=1)
        return None
    except Exception as exc:
        return format_zep_error(exc)
