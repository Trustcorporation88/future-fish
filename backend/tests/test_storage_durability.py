"""
Durabilidade entre deploys, no nível dos managers

O test_object_store cobre o módulo isoladamente. Aqui está o que o cliente
enxerga: gerar um relatório, apagar backend/uploads/ inteiro - a simulação fiel
do redeploy do Railway, que não tem volume - e o histórico continuar lá.

Também cobre o inverso, que é fácil de esquecer: um relatório excluído não pode
ressuscitar na hidratação do índice do próximo deploy.
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from app.config import Config
from app.services import object_store
from app.services.report_agent import Report, ReportManager, ReportStatus

from tests.test_object_store import FakeBucket


class TestReportSurvivesRedeploy(unittest.TestCase):
    """ReportManager contra um bucket em memória"""

    REPORT_ID = 'report_abc123'
    MARKDOWN = '# Análise\n\nConclusão com acentuação.'

    def setUp(self):
        self.reports_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.reports_dir, True)
        self.addCleanup(setattr, ReportManager, 'REPORTS_DIR', ReportManager.REPORTS_DIR)
        ReportManager.REPORTS_DIR = self.reports_dir

        for attr, value in (('SUPABASE_URL', 'https://proj.supabase.co'),
                            ('SUPABASE_SERVICE_KEY', 'service_key'),
                            ('SUPABASE_BUCKET', 'mirofish')):
            self.addCleanup(setattr, Config, attr, getattr(Config, attr))
            setattr(Config, attr, value)

        self.bucket = FakeBucket()
        for verb in ('post', 'get', 'delete'):
            patcher = patch.object(object_store.requests, verb,
                                   side_effect=getattr(self.bucket, verb))
            patcher.start()
            self.addCleanup(patcher.stop)

        self.addCleanup(setattr, ReportManager, '_index_restored', False)
        ReportManager._index_restored = False

    def save_completed_report(self):
        ReportManager.save_report(Report(
            report_id=self.REPORT_ID,
            simulation_id='sim_abc123',
            graph_id='graph_abc123',
            simulation_requirement='O que acontece com a Petrobras?',
            status=ReportStatus.COMPLETED,
            markdown_content=self.MARKDOWN,
            created_at='2026-01-01T00:00:00',
        ))

    def wipe_disk(self):
        """O redeploy: uploads/ desaparece e o índice volta a ser reconstruído"""
        shutil.rmtree(self.reports_dir, ignore_errors=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        ReportManager._index_restored = False

    def test_history_repopulates_after_wipe(self):
        self.save_completed_report()
        self.assertEqual(len(ReportManager.list_reports()), 1)

        self.wipe_disk()
        self.assertEqual(os.listdir(self.reports_dir), [])

        reports = ReportManager.list_reports()
        self.assertEqual([r.report_id for r in reports], [self.REPORT_ID])

    def test_full_markdown_comes_back_on_open(self):
        self.save_completed_report()
        self.wipe_disk()

        report = ReportManager.get_report(self.REPORT_ID)
        self.assertIsNotNone(report)
        self.assertEqual(report.markdown_content, self.MARKDOWN)

    def test_lookup_by_simulation_survives_wipe(self):
        """É por aqui que a Home liga o card do histórico ao relatório"""
        self.save_completed_report()
        self.wipe_disk()

        report = ReportManager.get_report_by_simulation('sim_abc123')
        self.assertIsNotNone(report)
        self.assertEqual(report.report_id, self.REPORT_ID)

    def test_deleted_report_does_not_resurrect(self):
        self.save_completed_report()
        self.assertTrue(ReportManager.delete_report(self.REPORT_ID))

        self.wipe_disk()
        self.assertEqual(ReportManager.list_reports(), [])

    def test_unfinished_report_is_not_mirrored(self):
        """Espelhar a cada checkpoint gastaria rede no meio da geração"""
        ReportManager.save_report(Report(
            report_id='report_emcurso',
            simulation_id='sim_abc123',
            graph_id='graph_abc123',
            simulation_requirement='Em andamento',
            status=ReportStatus.GENERATING,
            created_at='2026-01-01T00:00:00',
        ))
        self.assertEqual(self.bucket.objects, {})


class TestStorageOffKeepsLocalBehaviour(unittest.TestCase):
    """Sem as variáveis do Supabase tudo funciona como antes, só em disco"""

    def setUp(self):
        self.reports_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.reports_dir, True)
        self.addCleanup(setattr, ReportManager, 'REPORTS_DIR', ReportManager.REPORTS_DIR)
        ReportManager.REPORTS_DIR = self.reports_dir

        for attr in ('SUPABASE_URL', 'SUPABASE_SERVICE_KEY'):
            self.addCleanup(setattr, Config, attr, getattr(Config, attr))
            setattr(Config, attr, '')

    def test_save_and_read_without_storage(self):
        with patch.object(object_store, 'requests', autospec=True) as requests_mock:
            ReportManager.save_report(Report(
                report_id='report_local01',
                simulation_id='sim_local01',
                graph_id='graph_local01',
                simulation_requirement='Só disco',
                status=ReportStatus.COMPLETED,
                markdown_content='# Local',
                created_at='2026-01-01T00:00:00',
            ))
            report = ReportManager.get_report('report_local01')
            listed = ReportManager.list_reports()

            requests_mock.post.assert_not_called()
            requests_mock.get.assert_not_called()

        self.assertEqual(report.markdown_content, '# Local')
        self.assertEqual([r.report_id for r in listed], ['report_local01'])


if __name__ == '__main__':
    unittest.main()
