"""
/health como sonda de deploy

O Storage do Supabase é inteiramente interno: não cria rota, não altera resposta
de API, e tudo sob /api/ fica atrás do guard VIP. Sem expor o estado no /health
não existe sonda externa capaz de dizer se um deploy subiu com a persistência
ligada - a alternativa é gerar um relatório e conferir o bucket na mão.
"""

import sys
import os
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.config import Config
from app.utils import zep_errors


class TestHealthEndpoint(unittest.TestCase):

    def setUp(self):
        zep_errors._probe_cache.clear()
        self.app = create_app()
        self.client = self.app.test_client()

    def tearDown(self):
        zep_errors._probe_cache.clear()

    def _get(self):
        # A probe do Zep é rede externa; aqui só interessa o corpo da resposta.
        with patch.object(zep_errors, 'verify_zep_api_key', return_value=None):
            with patch('app.verify_zep_api_key', return_value=None):
                return self.client.get('/health').get_json()

    def test_reports_storage_state(self):
        body = self._get()
        self.assertIn('storage', body)
        self.assertIn('enabled', body['storage'])
        self.assertIsInstance(body['storage']['enabled'], bool)

    def test_bucket_name_appears_when_storage_is_on(self):
        with patch.object(Config, 'storage_enabled', classmethod(lambda cls: True)):
            with patch.object(Config, 'SUPABASE_BUCKET', 'mirofish'):
                body = self._get()
        self.assertTrue(body['storage']['enabled'])
        self.assertEqual(body['storage']['bucket'], 'mirofish')

    def test_bucket_is_null_when_storage_is_off(self):
        with patch.object(Config, 'storage_enabled', classmethod(lambda cls: False)):
            body = self._get()
        self.assertFalse(body['storage']['enabled'])
        self.assertIsNone(body['storage']['bucket'])

    def test_no_credential_is_ever_exposed(self):
        # O /health é público (auth.py o isenta do guard VIP), então nada de
        # segredo pode transitar por aqui - só booleano e nome de bucket.
        with patch.object(Config, 'storage_enabled', classmethod(lambda cls: True)):
            with patch.object(Config, 'SUPABASE_SERVICE_KEY', 'chave-secreta-que-nao-pode-vazar'):
                body = self._get()
        self.assertNotIn('chave-secreta-que-nao-pode-vazar', str(body))
        self.assertNotIn('SUPABASE_SERVICE_KEY', str(body))

    def test_health_needs_no_vip_login(self):
        with patch.object(zep_errors, 'verify_zep_api_key', return_value=None):
            with patch('app.verify_zep_api_key', return_value=None):
                self.assertEqual(self.client.get('/health').status_code, 200)
                self.assertEqual(self.client.get('/healthz').status_code, 200)


if __name__ == '__main__':
    unittest.main()
