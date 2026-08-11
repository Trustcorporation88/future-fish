"""Helpers for Zep Cloud API error messages."""

import time
from typing import Optional, Tuple


def _status_code(exc: Exception) -> Optional[int]:
    """
    Status HTTP da exceção, quando ela for um erro de API do Zep

    O SDK levanta `ApiError` com `status_code` preenchido. Ler o atributo é a
    única forma confiável de classificar: procurar "401" no texto da exceção
    também casa com trace ID, timestamp e corpo de resposta, o que transforma
    qualquer falha de rede em "sua chave expirou".
    """
    code = getattr(exc, 'status_code', None)
    return code if isinstance(code, int) else None


def format_zep_error(exc: Exception) -> str:
    status = _status_code(exc)

    if status == 401:
        return (
            "ZEP_API_KEY inválida ou expirada. "
            "Gere uma nova chave em https://app.getzep.com e atualize no Railway → Variables."
        )
    if status == 403:
        return "Acesso negado à API Zep (403). Verifique o plano e permissões da ZEP_API_KEY."
    if status == 429:
        return "Limite de requisições da API Zep excedido. Tente novamente em alguns minutos."

    text = str(exc)
    if status is None:
        # Sem status HTTP não houve resposta da API: timeout, DNS, TLS. Dizer que a
        # chave está inválida aqui manda o operador trocar uma credencial boa.
        detail = text[:300] if text else exc.__class__.__name__
        return f"Não foi possível falar com a API Zep ({exc.__class__.__name__}): {detail}"

    return f"API Zep respondeu HTTP {status}: {text[:300]}" if text else f"API Zep respondeu HTTP {status}"


# A probe é uma chamada de rede externa, e o /health é batido pelo healthcheck do
# Railway em intervalo curto (railway.toml). Sem cache, cada batida gera tráfego
# para o Zep e qualquer soluço momentâneo aparece como configuração quebrada.
_PROBE_TTL = 300
_probe_cache: dict[str, Tuple[float, Optional[str]]] = {}


def verify_zep_api_key(api_key: Optional[str], use_cache: bool = True) -> Optional[str]:
    """
    Devolve a mensagem de erro quando a ZEP_API_KEY está ausente ou é rejeitada

    O resultado fica em cache por alguns minutos, indexado pelo próprio valor da
    chave: trocar a credencial invalida a entrada na hora, sem esperar o TTL.
    Passe `use_cache=False` para forçar uma verificação ao vivo.
    """
    if not api_key:
        return "ZEP_API_KEY não configurada."

    if use_cache:
        cached = _probe_cache.get(api_key)
        if cached and (time.monotonic() - cached[0]) < _PROBE_TTL:
            return cached[1]

    try:
        from zep_cloud.client import Zep

        client = Zep(api_key=api_key)
        client.graph.list_all()
        result: Optional[str] = None
    except Exception as exc:
        result = format_zep_error(exc)

    _probe_cache[api_key] = (time.monotonic(), result)
    return result
