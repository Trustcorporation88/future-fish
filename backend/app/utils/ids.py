"""
标识符校验

ID 由服务端生成（形如 proj_/report_/sim_ + 十六进制），但会经由 URL 或请求体回传。
在用它们拼接文件路径之前必须校验，否则 `../` 之类的输入可以越出存储目录。
"""

import re
from typing import Any

# 服务端生成的 ID 只包含前缀、十六进制与下划线/连字符
_ID_PATTERN = re.compile(r'^[A-Za-z0-9_-]{1,64}$')


class InvalidIdError(ValueError):
    """ID 不符合允许的格式（可能是路径穿越尝试）"""


def validate_id(value: Any, kind: str = 'id') -> str:
    """
    校验用于拼接文件路径的标识符

    只允许字母、数字、下划线与连字符，因此点号、斜杠与反斜杠都会被拒绝，
    从根源上排除 `..`、绝对路径与 Windows 盘符等形式。

    Args:
        value: 待校验的标识符
        kind: 出错信息中显示的名称，例如 'report_id'

    Returns:
        校验通过的标识符

    Raises:
        InvalidIdError: 格式非法时抛出
    """
    if not isinstance(value, str) or not _ID_PATTERN.match(value):
        raise InvalidIdError(f"非法的 {kind}")
    return value
