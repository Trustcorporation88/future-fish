"""
Testes do espelhamento no Supabase Storage

Três garantias, nesta ordem de importância:

1. Desligado é idêntico ao comportamento anterior. Sem SUPABASE_URL +
   SUPABASE_SERVICE_KEY nenhuma função pode tocar a rede - é o que mantém o
   ambiente local e os outros testes funcionando sem bucket nenhum.
2. Nenhuma key sai para a rede sem passar pela mesma guarda de ID usada nos
   caminhos em disco: um `../` no ID escaparia do prefixo do bucket.
3. Falha do Storage nunca propaga. Durabilidade é bônus - uma indisponibilidade
   do Supabase não pode derrubar a geração de um relatório.
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import Mock, patch

import requests

from app.config import Config
from app.services import object_store


class StorageTestCase(unittest.TestCase):
    """Base com diretório temporário e as variáveis do Supabase controladas"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir, True)

    def set_storage(self, url='https://proj.supabase.co', key='service_key', bucket='mirofish'):
        """Liga (ou desliga, com url='') o Storage, restaurando os valores ao fim"""
        for attr, value in (('SUPABASE_URL', url), ('SUPABASE_SERVICE_KEY', key),
                            ('SUPABASE_BUCKET', bucket)):
            self.addCleanup(setattr, Config, attr, getattr(Config, attr))
            setattr(Config, attr, value)

    def write(self, filename, content='conteudo'):
        path = os.path.join(self.temp_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path


class TestDisabledIsNoOp(StorageTestCase):
    """Sem variáveis do Supabase, nada vai para a rede"""

    def setUp(self):
        super().setUp()
        self.set_storage(url='', key='')
        # Qualquer ida à rede com o Storage desligado é falha de teste
        patcher = patch.object(object_store, 'requests', autospec=True)
        self.requests_mock = patcher.start()
        self.addCleanup(patcher.stop)

    def test_enabled_is_false(self):
        self.assertFalse(object_store.enabled())

    def test_write_paths_are_no_ops(self):
        self.write('meta.json')
        self.assertEqual(
            object_store.mirror_folder('reports', 'report_abc', self.temp_dir), 0)
        self.assertFalse(object_store.put_bytes('reports/report_abc/meta.json', b'x'))
        self.assertFalse(object_store.delete_folder('reports', 'report_abc'))
        self.assertFalse(object_store.delete_keys(['reports/report_abc/meta.json']))

    def test_read_paths_are_no_ops(self):
        self.assertIsNone(object_store.get_bytes('reports/report_abc/meta.json'))
        self.assertEqual(object_store.list_prefix('reports'), [])
        self.assertEqual(
            object_store.hydrate_index('reports', self.temp_dir, 'meta.json'), 0)

    def test_hydrate_does_not_invent_a_file(self):
        missing = os.path.join(self.temp_dir, 'ausente.md')
        self.assertFalse(object_store.hydrate(missing, 'reports/report_abc/ausente.md'))
        self.assertFalse(os.path.exists(missing))

    def test_no_request_was_ever_made(self):
        """A checagem que dá sentido às anteriores"""
        object_store.mirror_folder('reports', 'report_abc', self.temp_dir)
        object_store.get_bytes('reports/report_abc/meta.json')
        object_store.list_prefix('reports')
        self.requests_mock.post.assert_not_called()
        self.requests_mock.get.assert_not_called()
        self.requests_mock.delete.assert_not_called()


class TestBuildKey(StorageTestCase):
    """A guarda de travessia, antes de qualquer ida à rede"""

    BAD_IDS = ('../etc', '..\\etc', 'report/../../secret', 'a/b', 'C:\\Windows', '', None)
    BAD_FILENAMES = ('../meta.json', 'sub/meta.json', '..', '.hidden', 'a' * 200, '')

    def test_rejects_traversal_ids(self):
        for bad_id in self.BAD_IDS:
            with self.subTest(entity_id=bad_id):
                with self.assertRaises(object_store.StorageKeyError):
                    object_store.build_key('reports', bad_id, 'meta.json')

    def test_rejects_bad_filenames(self):
        for bad_name in self.BAD_FILENAMES:
            with self.subTest(filename=bad_name):
                if bad_name == '':
                    # Vazio é o caso legítimo "key da pasta", não um erro
                    self.assertEqual(
                        object_store.build_key('reports', 'report_abc', ''),
                        'reports/report_abc')
                    continue
                with self.assertRaises(object_store.StorageKeyError):
                    object_store.build_key('reports', 'report_abc', bad_name)

    def test_builds_key_mirroring_disk_tree(self):
        self.assertEqual(
            object_store.build_key('reports', 'report_abc123', 'section_01.md'),
            'reports/report_abc123/section_01.md')


class TestNetworkFailureNeverPropagates(StorageTestCase):
    """Storage fora do ar não pode derrubar a geração de relatório"""

    def setUp(self):
        super().setUp()
        self.set_storage()

    def run_all_entry_points(self):
        """Toda função pública que fala com a rede, uma vez"""
        self.write('meta.json')
        return (
            object_store.put_bytes('reports/report_abc/meta.json', b'x'),
            object_store.get_bytes('reports/report_abc/meta.json'),
            object_store.list_prefix('reports'),
            object_store.delete_keys(['reports/report_abc/meta.json']),
            object_store.mirror_folder('reports', 'report_abc', self.temp_dir),
            object_store.hydrate_index('reports', self.temp_dir, 'meta.json'),
            object_store.delete_folder('reports', 'report_abc'),
        )

    def test_connection_error_is_swallowed(self):
        boom = requests.ConnectionError('sem rede')
        with patch.object(object_store.requests, 'post', side_effect=boom), \
             patch.object(object_store.requests, 'get', side_effect=boom), \
             patch.object(object_store.requests, 'delete', side_effect=boom):
            put, get, listed, deleted, mirrored, restored, folder = self.run_all_entry_points()

        self.assertFalse(put)
        self.assertIsNone(get)
        self.assertEqual(listed, [])
        self.assertFalse(deleted)
        self.assertEqual(mirrored, 0)
        self.assertEqual(restored, 0)
        self.assertFalse(folder)

    def test_timeout_is_swallowed(self):
        boom = requests.Timeout('estourou o tempo')
        with patch.object(object_store.requests, 'post', side_effect=boom), \
             patch.object(object_store.requests, 'get', side_effect=boom), \
             patch.object(object_store.requests, 'delete', side_effect=boom):
            self.run_all_entry_points()  # não levanta

    def test_http_error_status_is_not_treated_as_success(self):
        # Só os métodos, nunca o módulo inteiro: trocar `requests` por um Mock
        # faria requests.RequestException virar Mock e quebrar os `except`.
        error = Mock(status_code=500)
        forbidden = Mock(status_code=403)
        with patch.object(object_store.requests, 'post', return_value=error), \
             patch.object(object_store.requests, 'get', return_value=error), \
             patch.object(object_store.requests, 'delete', return_value=forbidden):
            self.assertFalse(object_store.put_bytes('reports/report_abc/meta.json', b'x'))
            self.assertIsNone(object_store.get_bytes('reports/report_abc/meta.json'))
            self.assertEqual(object_store.list_prefix('reports'), [])
            self.assertFalse(object_store.delete_keys(['reports/report_abc/meta.json']))

    def test_malformed_list_response_is_swallowed(self):
        response = Mock(status_code=200)
        response.json.side_effect = ValueError('não é JSON')
        with patch.object(object_store.requests, 'post', return_value=response):
            self.assertEqual(object_store.list_prefix('reports'), [])


class FakeBucket:
    """Bucket em memória falando o dialeto HTTP da Storage REST API do Supabase"""

    def __init__(self, bucket='mirofish'):
        self.objects = {}
        self._marker = f'/object/{bucket}/'
        self._list_marker = f'/object/list/{bucket}'

    def _key(self, url):
        return url.split(self._marker, 1)[1]

    def post(self, url, data=None, json=None, headers=None, timeout=None):
        if self._list_marker in url:
            return self._list(json or {})
        self.objects[self._key(url)] = data
        return Mock(status_code=200)

    def _list(self, body):
        prefix = body.get('prefix', '').rstrip('/')
        names = []
        for key in sorted(self.objects):
            if not key.startswith(f'{prefix}/'):
                continue
            child = key[len(prefix) + 1:].split('/', 1)[0]
            if child not in names:
                names.append(child)
        page = names[body.get('offset', 0):][:body.get('limit', 100)]
        return Mock(status_code=200, **{'json.return_value': [{'name': n} for n in page]})

    def get(self, url, headers=None, timeout=None):
        data = self.objects.get(self._key(url))
        if data is None:
            return Mock(status_code=404)
        return Mock(status_code=200, content=data)

    def delete(self, url, json=None, headers=None, timeout=None):
        for key in (json or {}).get('prefixes', []):
            self.objects.pop(key, None)
        return Mock(status_code=200)


class TestRoundTrip(StorageTestCase):
    """O caso que motiva o módulo: disco zerado por um redeploy e histórico de volta"""

    def setUp(self):
        super().setUp()
        self.set_storage()
        self.bucket = FakeBucket()
        for verb in ('post', 'get', 'delete'):
            patcher = patch.object(object_store.requests, verb,
                                   side_effect=getattr(self.bucket, verb))
            patcher.start()
            self.addCleanup(patcher.stop)

    def mirror_a_report(self, report_id='report_abc123'):
        folder = os.path.join(self.temp_dir, report_id)
        os.makedirs(folder)
        for name, body in (('meta.json', '{"report_id": "x"}'),
                           ('full_report.md', '# Relatório'),
                           ('section_01.md', 'Seção com acentuação')):
            with open(os.path.join(folder, name), 'w', encoding='utf-8') as f:
                f.write(body)
        return folder, object_store.mirror_folder('reports', report_id, folder)

    def test_mirror_then_hydrate_after_disk_wipe(self):
        folder, sent = self.mirror_a_report()
        self.assertEqual(sent, 3)

        shutil.rmtree(folder)  # o redeploy do Railway, fielmente

        local = os.path.join(folder, 'full_report.md')
        self.assertTrue(object_store.hydrate(local, 'reports/report_abc123/full_report.md'))
        with open(local, encoding='utf-8') as f:
            self.assertEqual(f.read(), '# Relatório')

    def test_hydrate_index_restores_the_listing(self):
        for report_id in ('report_aaa', 'report_bbb'):
            folder, _ = self.mirror_a_report(report_id)
            shutil.rmtree(folder)

        self.assertEqual(
            object_store.hydrate_index('reports', self.temp_dir, 'meta.json'), 2)
        self.assertEqual(sorted(os.listdir(self.temp_dir)), ['report_aaa', 'report_bbb'])
        # Só o índice desce: o Markdown espera alguém abrir o relatório
        self.assertEqual(os.listdir(os.path.join(self.temp_dir, 'report_aaa')), ['meta.json'])

    def test_delete_folder_stops_the_resurrection(self):
        folder, _ = self.mirror_a_report()
        self.assertTrue(object_store.delete_folder('reports', 'report_abc123'))
        shutil.rmtree(folder)
        self.assertEqual(
            object_store.hydrate_index('reports', self.temp_dir, 'meta.json'), 0)

    def test_existing_local_file_never_hits_the_network(self):
        """O polling dos logs passa por aqui a cada poucos segundos"""
        local = self.write('console_log.txt')
        with patch.object(object_store, 'get_bytes') as get_bytes:
            self.assertTrue(object_store.hydrate(local, 'reports/report_abc123/console_log.txt'))
        get_bytes.assert_not_called()

    def test_partial_download_leaves_no_truncated_file(self):
        local = os.path.join(self.temp_dir, 'novo', 'full_report.md')
        with patch.object(object_store, 'os', wraps=os) as os_mock:
            os_mock.replace.side_effect = OSError('disco cheio')
            self.assertFalse(
                object_store.hydrate(local, 'reports/report_abc123/full_report.md'))
        self.assertFalse(os.path.exists(local))
        self.assertFalse(os.path.exists(f'{local}.part'))

    def test_list_prefix_pages_past_the_first_page(self):
        """Sem paginação um bucket grande truncaria o histórico em silêncio"""
        for index in range(5):
            self.mirror_a_report(f'report_{index:03d}')
        with patch.object(object_store, '_PAGE_SIZE', 2):
            self.assertEqual(len(object_store.list_ids('reports')), 5)
