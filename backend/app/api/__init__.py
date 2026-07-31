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

from .guards import register_path_id_guard  # noqa: E402

# 三个蓝图统一校验参与路径拼接的 ID
register_path_id_guard(graph_bp, simulation_bp, report_bp)

