"""
存储层 ID 校验与目录遍历的回归测试

两个关注点：
1. 拼接存储路径的入口都要校验 ID——HTTP 钩子只覆盖请求入口，
   后台线程与脚本会直接调用这些类方法
2. 遍历存储目录时遇到不合规的名字（手工复制出的副本、系统文件）
   要跳过，而不是让整个列表接口失败
"""

import json
import os
import shutil
import tempfile
import unittest

from app.services.report_agent import ReportManager
from app.services.simulation_manager import SimulationManager
from app.services.simulation_runner import SimulationRunner
from app.utils.ids import InvalidIdError


class TempDirTestCase(unittest.TestCase):
    """把某个类属性指向临时目录，测试结束后还原"""

    def redirect(self, owner, attr):
        temp_dir = tempfile.mkdtemp()
        original = getattr(owner, attr)
        setattr(owner, attr, temp_dir)
        self.addCleanup(setattr, owner, attr, original)
        self.addCleanup(shutil.rmtree, temp_dir, True)
        return temp_dir


class TestSimulationRunnerPathGuard(unittest.TestCase):
    """SimulationRunner._sim_dir 是 HTTP 钩子之外的第二道防线"""

    BAD_IDS = (
        '../etc',
        '..\\etc',           # Windows 上反斜杠同样是分隔符
        'sim/../../secret',
        'sim_a/b',
        'C:\\Windows',
        '',
        None,
    )

    def test_rejects_traversal_ids(self):
        for bad_id in self.BAD_IDS:
            with self.subTest(simulation_id=bad_id):
                with self.assertRaises(InvalidIdError):
                    SimulationRunner._sim_dir(bad_id)

    def test_joins_valid_id_under_run_state_dir(self):
        path = SimulationRunner._sim_dir('sim_0123abcd', 'run_state.json')
        expected = os.path.join(
            SimulationRunner.RUN_STATE_DIR, 'sim_0123abcd', 'run_state.json'
        )
        self.assertEqual(path, expected)

    def test_load_run_state_rejects_bad_id(self):
        """经由公开方法进来的非法 ID 同样被拦下"""
        with self.assertRaises(InvalidIdError):
            SimulationRunner._load_run_state('../etc')


class TestReportListingSkipsJunk(TempDirTestCase):
    """reports 目录里的杂项不应让列表接口整体失败"""

    def setUp(self):
        self.reports_dir = self.redirect(ReportManager, 'REPORTS_DIR')

        # 合规条目：新格式文件夹（缺 report.json）与旧格式 JSON 文件（内容被截断）
        os.mkdir(os.path.join(self.reports_dir, 'report_0123abcd'))
        open(os.path.join(self.reports_dir, 'report_legacy01.json'), 'w').close()

        # 不合规条目：手工复制的副本、系统文件、无关文件
        os.mkdir(os.path.join(self.reports_dir, 'report_0123abcd - Copy'))
        open(os.path.join(self.reports_dir, '.DS_Store'), 'w').close()
        open(os.path.join(self.reports_dir, 'notes.txt'), 'w').close()

    def test_iter_report_ids_keeps_only_valid_names(self):
        self.assertEqual(
            sorted(ReportManager._iter_report_ids()),
            ['report_0123abcd', 'report_legacy01'],
        )

    def test_list_reports_does_not_raise(self):
        """副本目录与截断的 JSON 都跳过，接口仍要返回结果"""
        self.assertEqual(ReportManager.list_reports(), [])

    def test_get_report_by_simulation_does_not_raise(self):
        self.assertIsNone(ReportManager.get_report_by_simulation('sim_0123abcd'))

    def test_corrupt_json_does_not_hide_other_reports(self):
        """一份报告写坏了，其余报告仍要列得出来"""
        good_id = 'report_9999beef'
        os.mkdir(os.path.join(self.reports_dir, good_id))
        with open(
            os.path.join(self.reports_dir, good_id, 'meta.json'), 'w', encoding='utf-8'
        ) as f:
            json.dump(
                {
                    'report_id': good_id,
                    'simulation_id': 'sim_0123abcd',
                    'graph_id': 'graph_1',
                    'simulation_requirement': '测试',
                    'status': 'completed',
                },
                f,
            )

        reports = ReportManager.list_reports()
        self.assertEqual([r.report_id for r in reports], [good_id])
        self.assertEqual(
            ReportManager.get_report_by_simulation('sim_0123abcd').report_id, good_id
        )


class TestSimulationListingSkipsJunk(TempDirTestCase):
    """simulations 目录同理"""

    def setUp(self):
        self.data_dir = self.redirect(SimulationManager, 'SIMULATION_DATA_DIR')

        self._write_state('sim_0123abcd', project_id='proj_0123abcd')
        self._write_state('sim_0123abcd - Copy', project_id='proj_0123abcd')
        os.mkdir(os.path.join(self.data_dir, '.hidden'))

        self.manager = SimulationManager()

    def _write_state(self, sim_id, project_id):
        sim_dir = os.path.join(self.data_dir, sim_id)
        os.mkdir(sim_dir)
        with open(os.path.join(sim_dir, 'state.json'), 'w', encoding='utf-8') as f:
            json.dump({'project_id': project_id, 'status': 'created'}, f)

    def test_list_simulations_skips_invalid_dir_names(self):
        simulations = self.manager.list_simulations()
        self.assertEqual([s.simulation_id for s in simulations], ['sim_0123abcd'])

    def test_list_simulations_filtered_by_project(self):
        simulations = self.manager.list_simulations(project_id='proj_0123abcd')
        self.assertEqual([s.simulation_id for s in simulations], ['sim_0123abcd'])
        self.assertEqual(self.manager.list_simulations(project_id='proj_other'), [])

    def test_corrupt_state_does_not_hide_other_simulations(self):
        """一个模拟的 state.json 被截断，其余模拟仍要列得出来"""
        broken_dir = os.path.join(self.data_dir, 'sim_9999beef')
        os.mkdir(broken_dir)
        open(os.path.join(broken_dir, 'state.json'), 'w').close()

        simulations = self.manager.list_simulations()
        self.assertEqual([s.simulation_id for s in simulations], ['sim_0123abcd'])


if __name__ == '__main__':
    unittest.main()
