"""
Classificação de erro do Zep e a probe do /health

O bug que motivou estes testes: `format_zep_error` decidia "chave inválida ou
expirada" procurando a substring "401" no texto da exceção. Um trace ID, um
timestamp ou um corpo de resposta contendo 401 caía no mesmo ramo, então uma
falha de rede mandava o operador trocar uma credencial que estava boa - foi
exatamente o que aconteceu em produção, com uma chave válida.
"""

import sys
import os
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.utils import zep_errors
from app.utils.zep_errors import format_zep_error, verify_zep_api_key


class FakeApiError(Exception):
    """Reproduz a forma do zep_cloud ApiError: status_code como atributo"""

    def __init__(self, status_code=None, message=''):
        super().__init__(message)
        self.status_code = status_code


class TestErrorClassification(unittest.TestCase):

    def test_real_401_still_says_the_key_is_bad(self):
        msg = format_zep_error(FakeApiError(401, 'unauthorized'))
        self.assertIn('ZEP_API_KEY inválida ou expirada', msg)

    def test_403_and_429_keep_their_own_messages(self):
        self.assertIn('Acesso negado', format_zep_error(FakeApiError(403, 'forbidden')))
        self.assertIn('Limite de requisições', format_zep_error(FakeApiError(429, 'rate limit')))

    def test_trace_id_containing_401_is_not_an_auth_error(self):
        # Este é o falso positivo: sem status HTTP, o texto não pode decidir.
        exc = TimeoutError('request failed after 30s traceId=4985949016401075737')
        msg = format_zep_error(exc)
        self.assertNotIn('ZEP_API_KEY inválida', msg)
        self.assertIn('Não foi possível falar com a API Zep', msg)

    def test_network_failure_is_reported_as_network_failure(self):
        msg = format_zep_error(ConnectionResetError('read ECONNRESET'))
        self.assertNotIn('inválida ou expirada', msg)
        self.assertIn('ConnectionResetError', msg)

    def test_word_unauthorized_in_body_without_401_status(self):
        # Um 500 cujo corpo cita "unauthorized" não é chave expirada.
        msg = format_zep_error(FakeApiError(500, 'upstream said unauthorized'))
        self.assertNotIn('ZEP_API_KEY inválida', msg)
        self.assertIn('HTTP 500', msg)

    def test_unmapped_status_reports_the_code(self):
        self.assertIn('HTTP 503', format_zep_error(FakeApiError(503, 'unavailable')))


class TestProbeCache(unittest.TestCase):

    def setUp(self):
        zep_errors._probe_cache.clear()

    def tearDown(self):
        zep_errors._probe_cache.clear()

    def test_missing_key_needs_no_network_call(self):
        self.assertEqual(verify_zep_api_key(None), 'ZEP_API_KEY não configurada.')
        self.assertEqual(verify_zep_api_key(''), 'ZEP_API_KEY não configurada.')

    def test_repeated_calls_hit_the_api_once(self):
        calls = []

        class FakeZep:
            def __init__(self, api_key=None):
                calls.append(api_key)
                self.graph = self

            def list_all(self):
                return []

        with patch.dict(sys.modules, {'zep_cloud.client': type(sys)('zep_cloud.client')}):
            sys.modules['zep_cloud.client'].Zep = FakeZep
            for _ in range(5):
                self.assertIsNone(verify_zep_api_key('key-abc'))

        # O healthcheck do Railway bate no /health de forma contínua; sem cache
        # cada batida viraria uma chamada externa ao Zep.
        self.assertEqual(len(calls), 1)

    def test_changing_the_key_bypasses_the_cache(self):
        calls = []

        class FakeZep:
            def __init__(self, api_key=None):
                calls.append(api_key)
                self.graph = self

            def list_all(self):
                return []

        with patch.dict(sys.modules, {'zep_cloud.client': type(sys)('zep_cloud.client')}):
            sys.modules['zep_cloud.client'].Zep = FakeZep
            verify_zep_api_key('key-antiga')
            verify_zep_api_key('key-nova')

        self.assertEqual(calls, ['key-antiga', 'key-nova'])

    def test_use_cache_false_forces_a_live_check(self):
        calls = []

        class FakeZep:
            def __init__(self, api_key=None):
                calls.append(api_key)
                self.graph = self

            def list_all(self):
                return []

        with patch.dict(sys.modules, {'zep_cloud.client': type(sys)('zep_cloud.client')}):
            sys.modules['zep_cloud.client'].Zep = FakeZep
            verify_zep_api_key('key-abc')
            verify_zep_api_key('key-abc', use_cache=False)

        self.assertEqual(len(calls), 2)


if __name__ == '__main__':
    unittest.main()
