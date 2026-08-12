"""
Supabase Storage - arquivo durável para os artefatos de backend/uploads/

O filesystem do Railway é efêmero: cada redeploy, restart ou crash-restart apaga
uploads/ por inteiro, e com ele o histórico e os relatórios já entregues. Este
módulo espelha os artefatos finalizados no Supabase Storage e os traz de volta ao
disco sob demanda, mantendo o disco local como cache de trabalho.

Desligado por padrão: sem SUPABASE_URL + SUPABASE_SERVICE_KEY toda função aqui é
no-op e o comportamento é idêntico ao de antes.

Nenhuma falha deste módulo pode derrubar um request. Durabilidade é bônus, não
dependência dura: uma indisponibilidade do Supabase não pode impedir a geração de
um relatório. Por isso tudo captura exceção, loga warning e devolve None/False.

Fala HTTP direto com a Storage REST API via requests (já é dependência) em vez de
supabase-py, que traria httpx, gotrue, postgrest, realtime e storage3 para uma
imagem que já carrega camel-ai e camel-oasis.
"""

import os
import re
from typing import List, Optional

import requests

from ..config import Config
from ..utils.ids import validate_id, InvalidIdError
from ..utils.logger import get_logger

logger = get_logger('mirofish.services.object_store')

# Uploads de relatório são pequenos (Markdown/JSON); um teto baixo evita que uma
# indisponibilidade do Supabase segure a thread de geração por muito tempo.
_TIMEOUT = 20

# Uma página da API de listagem do Supabase
_PAGE_SIZE = 100

# Nomes de arquivo são constantes internas (meta.json, section_00.md). Validar
# ainda assim mantém a montagem de key com a mesma garantia dos caminhos em disco.
_FILENAME_PATTERN = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$')


class StorageKeyError(ValueError):
    """Key rejeitada antes de sair para a rede (possível travessia de caminho)"""


def enabled() -> bool:
    """Storage configurado. Falso mantém todo caminho de leitura/escrita local."""
    return Config.storage_enabled()


def build_key(prefix: str, entity_id: str, filename: str = '') -> str:
    """
    Monta a key espelhando a árvore em disco: `{prefix}/{entity_id}/{filename}`

    O entity_id passa por validate_id - a mesma guarda usada antes de concatenar
    caminho local - para que um ID hostil não escape do prefixo do bucket. O nome
    do arquivo é conferido contra uma allowlist, o que descarta `..` e separadores.
    """
    try:
        validate_id(entity_id, f'{prefix}_id')
    except InvalidIdError as e:
        raise StorageKeyError(str(e)) from e

    key = f'{prefix}/{entity_id}'
    if filename:
        if not _FILENAME_PATTERN.match(filename) or '..' in filename:
            raise StorageKeyError(f"nome de arquivo inválido: {filename!r}")
        key = f'{key}/{filename}'
    return key


def _object_url(key: str) -> str:
    base = (Config.SUPABASE_URL or '').rstrip('/')
    return f'{base}/storage/v1/object/{Config.SUPABASE_BUCKET}/{key}'


def _headers(extra: Optional[dict] = None) -> dict:
    headers = {
        'Authorization': f'Bearer {Config.SUPABASE_SERVICE_KEY}',
        'apikey': Config.SUPABASE_SERVICE_KEY or '',
    }
    if extra:
        headers.update(extra)
    return headers


def put_bytes(key: str, data: bytes, content_type: str = 'application/octet-stream') -> bool:
    """Grava (ou sobrescreve) um objeto. Devolve se a gravação foi confirmada."""
    if not enabled():
        return False

    try:
        response = requests.post(
            _object_url(key),
            data=data,
            headers=_headers({'Content-Type': content_type, 'x-upsert': 'true'}),
            timeout=_TIMEOUT,
        )
        if response.status_code >= 400:
            logger.warning(f"Storage put falhou em {key}: HTTP {response.status_code}")
            return False
        return True
    except requests.RequestException as e:
        logger.warning(f"Storage put falhou em {key}: {e}")
        return False


def _is_missing(response) -> bool:
    """
    A resposta diz "esse objeto não existe", em qualquer um dos dois dialetos

    A Storage REST API do Supabase não responde 404 nu para objeto ausente: manda
    **HTTP 400** com o 404 no corpo -

        {"statusCode":"404","error":"not_found","message":"Object not found",
         "code":"NoSuchKey"}

    Confiar só no status transforma todo cache miss em "Storage get falhou: HTTP
    400" no log. Isso importa porque ausência é o caminho normal: hydrate() e
    hydrate_index() leem justamente o que não está em disco depois de um redeploy,
    que é o momento em que alguém abre o log para ver se a persistência pegou. Com
    o miss gritando warning, uma chave revogada (401), um bucket apagado (404) ou
    throttling (429) ficam indistinguíveis do funcionamento normal.

    Aceita os dois dialetos: quem trocar de provedor - ou mockar com 404 nu - segue
    valendo.
    """
    if response.status_code == 404:
        return True
    if response.status_code >= 400:
        try:
            body = response.json()
        except (ValueError, AttributeError):
            return False
        if not isinstance(body, dict):
            return False
        return (str(body.get('statusCode')) == '404'
                or body.get('error') == 'not_found'
                or body.get('code') == 'NoSuchKey')
    return False


def get_bytes(key: str) -> Optional[bytes]:
    """
    Lê um objeto. None quando não existe ou quando a leitura falha.

    Ausência não é falha e não vira warning - ver _is_missing().
    """
    if not enabled():
        return None

    try:
        response = requests.get(_object_url(key), headers=_headers(), timeout=_TIMEOUT)
        if _is_missing(response):
            return None
        if response.status_code >= 400:
            logger.warning(f"Storage get falhou em {key}: HTTP {response.status_code}")
            return None
        return response.content
    except requests.RequestException as e:
        logger.warning(f"Storage get falhou em {key}: {e}")
        return None


def list_prefix(prefix: str) -> List[str]:
    """
    Lista os nomes imediatamente abaixo do prefixo (arquivos e subpastas)

    Pagina até o fim: a API do Supabase devolve no máximo uma página por chamada,
    e um bucket com muitos relatórios truncaria silenciosamente o histórico.
    """
    if not enabled():
        return []

    base = (Config.SUPABASE_URL or '').rstrip('/')
    url = f'{base}/storage/v1/object/list/{Config.SUPABASE_BUCKET}'
    names: List[str] = []
    offset = 0

    try:
        while True:
            response = requests.post(
                url,
                json={'prefix': prefix, 'limit': _PAGE_SIZE, 'offset': offset},
                headers=_headers({'Content-Type': 'application/json'}),
                timeout=_TIMEOUT,
            )
            if response.status_code >= 400:
                logger.warning(f"Storage list falhou em {prefix}: HTTP {response.status_code}")
                return names

            page = response.json()
            if not isinstance(page, list) or not page:
                return names

            for item in page:
                name = item.get('name') if isinstance(item, dict) else None
                if name:
                    names.append(name)

            if len(page) < _PAGE_SIZE:
                return names
            offset += _PAGE_SIZE
    except (requests.RequestException, ValueError) as e:
        # ValueError cobre resposta que não é JSON válido
        logger.warning(f"Storage list falhou em {prefix}: {e}")
        return names


def list_ids(prefix: str) -> List[str]:
    """IDs de entidade sob o prefixo, descartando nomes fora do padrão de validate_id"""
    ids = []
    for name in list_prefix(prefix):
        try:
            validate_id(name, f'{prefix}_id')
        except InvalidIdError:
            continue
        ids.append(name)
    return ids


def delete_keys(keys: List[str]) -> bool:
    """Apaga objetos. Sem isso um item excluído voltaria na próxima hidratação."""
    if not enabled() or not keys:
        return False

    base = (Config.SUPABASE_URL or '').rstrip('/')
    try:
        response = requests.delete(
            f'{base}/storage/v1/object/{Config.SUPABASE_BUCKET}',
            json={'prefixes': keys},
            headers=_headers({'Content-Type': 'application/json'}),
            timeout=_TIMEOUT,
        )
        if response.status_code >= 400:
            logger.warning(f"Storage delete falhou: HTTP {response.status_code}")
            return False
        return True
    except requests.RequestException as e:
        logger.warning(f"Storage delete falhou: {e}")
        return False


_CONTENT_TYPES = {
    '.json': 'application/json',
    '.md': 'text/markdown; charset=utf-8',
    '.txt': 'text/plain; charset=utf-8',
    '.jsonl': 'application/x-ndjson',
}


def _content_type(filename: str) -> str:
    return _CONTENT_TYPES.get(os.path.splitext(filename)[1].lower(), 'application/octet-stream')


def hydrate(local_path: str, key: str) -> bool:
    """
    Garante que o arquivo local exista, baixando do Storage se necessário

    Sai imediatamente quando o arquivo já está em disco - é o caso de toda
    leitura durante a geração e de toda leitura após a primeira, então nenhum
    request de polling paga uma ida à rede.

    Grava em arquivo temporário e renomeia: um download interrompido não deixa
    Markdown truncado no lugar do relatório.
    """
    if os.path.exists(local_path):
        return True
    if not enabled():
        return False

    data = get_bytes(key)
    if data is None:
        return False

    temp_path = f'{local_path}.part'
    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(temp_path, 'wb') as f:
            f.write(data)
        os.replace(temp_path, local_path)
        return True
    except OSError as e:
        logger.warning(f"Falha ao gravar {local_path} vindo do Storage: {e}")
        try:
            os.remove(temp_path)
        except OSError:
            pass
        return False


def hydrate_index(prefix: str, local_root: str, index_filename: str) -> int:
    """
    Reconstrói o índice varrido por diretório depois que o disco foi zerado

    list_reports/list_simulations descobrem IDs com os.listdir; após um redeploy
    a pasta está vazia e o histórico some. Aqui baixamos só o JSON de índice de
    cada ID (meta.json / state.json), não os artefatos completos - o Markdown do
    relatório só desce quando alguém abre aquele relatório.

    Devolve quantos IDs foram trazidos de volta.
    """
    if not enabled():
        return 0

    restored = 0
    for entity_id in list_ids(prefix):
        local_path = os.path.join(local_root, entity_id, index_filename)
        if os.path.exists(local_path):
            continue
        try:
            key = build_key(prefix, entity_id, index_filename)
        except StorageKeyError:
            continue
        if hydrate(local_path, key):
            restored += 1

    if restored:
        logger.info(f"Storage: {restored} item(ns) de {prefix} restaurados do arquivo durável")
    return restored


def mirror_folder(prefix: str, entity_id: str, local_folder: str,
                  filenames: Optional[List[str]] = None) -> int:
    """
    Sobe os arquivos de uma pasta local para o Storage

    Chamado nos checkpoints terminais. Com filenames=None sobe tudo que estiver
    na pasta; com uma lista, só os nomes indicados que existirem.

    Devolve quantos arquivos subiram.
    """
    if not enabled() or not os.path.isdir(local_folder):
        return 0

    try:
        candidates = filenames if filenames is not None else sorted(os.listdir(local_folder))
    except OSError as e:
        logger.warning(f"Não foi possível listar {local_folder} para espelhar: {e}")
        return 0

    sent = 0
    for filename in candidates:
        local_path = os.path.join(local_folder, filename)
        if not os.path.isfile(local_path):
            continue
        try:
            key = build_key(prefix, entity_id, filename)
        except StorageKeyError as e:
            logger.warning(f"Arquivo ignorado no espelhamento: {e}")
            continue
        try:
            with open(local_path, 'rb') as f:
                data = f.read()
        except OSError as e:
            logger.warning(f"Não foi possível ler {local_path} para espelhar: {e}")
            continue
        if put_bytes(key, data, _content_type(filename)):
            sent += 1

    if sent:
        logger.info(f"Storage: {sent} arquivo(s) de {prefix}/{entity_id} espelhados")
    return sent


def delete_folder(prefix: str, entity_id: str) -> bool:
    """Apaga todos os objetos de uma entidade, para que ela não volte na hidratação"""
    if not enabled():
        return False

    try:
        folder = build_key(prefix, entity_id)
    except StorageKeyError:
        return False

    keys = [f'{folder}/{name}' for name in list_prefix(folder)]
    if not keys:
        return False
    return delete_keys(keys)


