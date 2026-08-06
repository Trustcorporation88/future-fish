"""
蓝图请求钩子的回归测试

覆盖两类此前会变成 500 的输入：
1. 请求体声明为 JSON 但不是对象（数组、字符串）——视图里 `data.get(...)` 会抛 AttributeError
2. 参与文件路径拼接的 ID 含非法字符——拼路径时的校验会在视图的 try/except 里被吞掉
"""

import unittest

from app import create_app


class RequestGuardTestCase(unittest.TestCase):
    """带 test_client 的基类"""

    @classmethod
    def setUpClass(cls):
        app = create_app()
        app.config['TESTING'] = True
        cls.client = app.test_client()


class TestMalformedJsonBody(RequestGuardTestCase):
    """非对象的 JSON 请求体应当是 400，而不是 500"""

    # 覆盖三个蓝图：都写着 `data = request.get_json(silent=True) or {}`
    ROUTES = (
        '/api/news/search',
        '/api/report/generate',
        '/api/simulation/create',
        '/api/auth/login',
    )

    def test_array_body_rejected(self):
        for route in self.ROUTES:
            with self.subTest(route=route):
                response = self.client.post(route, json=['x'])
                self.assertEqual(response.status_code, 400)
                self.assertFalse(response.get_json()['success'])

    def test_string_body_rejected(self):
        for route in self.ROUTES:
            with self.subTest(route=route):
                response = self.client.post(route, json='x')
                self.assertEqual(response.status_code, 400)

    def test_unparsable_body_rejected(self):
        response = self.client.post(
            '/api/news/search',
            data=b'{not json',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_empty_body_reaches_view(self):
        """空请求体按 {} 放行：由视图给出更具体的参数缺失提示"""
        response = self.client.post(
            '/api/news/search',
            data=b'',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Query', response.get_json()['error'])

    def test_object_body_reaches_view(self):
        response = self.client.post('/api/report/generate', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('simulation_id', response.get_json()['error'])

    def test_non_json_content_type_ignored(self):
        """表单请求不走 JSON 解析，钩子不应插手"""
        response = self.client.post('/api/news/search', data={'query': 'x'})
        self.assertNotEqual(response.status_code, 500)


class TestPathIdValidation(RequestGuardTestCase):
    """参与路径拼接的 ID 非法时应当是 400"""

    BAD_ID = 'sim_..%2Fetc'

    def test_rejected_in_query_string(self):
        response = self.client.get(f'/api/report/list?simulation_id={self.BAD_ID}')
        self.assertEqual(response.status_code, 400)
        self.assertIn('simulation_id', response.get_json()['error'])

    def test_rejected_in_json_body(self):
        response = self.client.post(
            '/api/simulation/close-env',
            json={'simulation_id': self.BAD_ID},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('simulation_id', response.get_json()['error'])

    def test_rejected_in_url_path(self):
        response = self.client.get('/api/report/bad.id/sections')
        self.assertEqual(response.status_code, 400)
        self.assertIn('report_id', response.get_json()['error'])

    def test_valid_id_passes_guard(self):
        """格式正确的 ID 应当进入视图：报告不存在时返回空章节列表而非 400"""
        response = self.client.get('/api/report/rep_0123abcd/sections')
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertTrue(body['success'])
        self.assertEqual(body['data']['sections'], [])

    def test_missing_id_left_to_view(self):
        """ID 缺失不由钩子处理：视图的提示更具体"""
        response = self.client.get('/api/report/list')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
