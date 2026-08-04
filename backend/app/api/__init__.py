"""
API路由模块
"""

from flask import Blueprint

graph_bp = Blueprint('graph', __name__)
simulation_bp = Blueprint('simulation', __name__)
report_bp = Blueprint('report', __name__)

from . import graph  # noqa: E402, F401
from . import simulation  # noqa: E402, F401
from . import report  # noqa: E402, F401

from .news import news_bp, quotes_bp  # noqa: E402, F401
from .auth import auth_bp  # noqa: E402, F401
from .guards import register_path_id_guard  # noqa: E402

# 所有蓝图统一校验参与路径拼接的 ID，并把非对象的 JSON 请求体拦成 400。
# news/quotes/auth 不接收路径 ID，挂钩子只为拿到请求体校验：
# /api/news/search 与 /api/auth/login 也是 `data.get(...)`，
# 数组请求体同样会变成 500（login 连 try/except 都没有）。
register_path_id_guard(graph_bp, simulation_bp, report_bp, news_bp, quotes_bp, auth_bp)

