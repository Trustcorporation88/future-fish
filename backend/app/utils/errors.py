"""
错误响应辅助

把异常堆栈返回给客户端会泄露文件路径与内部结构，
但堆栈本身在排查问题时不可或缺，因此统一：始终写日志，仅调试模式下回传。
"""

import traceback
from typing import Dict

from .logger import get_logger

logger = get_logger('mirofish.error')


def report_exception(context: str = '') -> Dict[str, str]:
    """
    记录当前异常堆栈，并返回可展开进 JSON 响应的字典

    完整堆栈总是写入日志；只有在 DEBUG 开启时才包含在返回值里。

    Args:
        context: 出现异常的位置说明，便于检索日志

    Returns:
        调试模式下为 {"traceback": ...}，否则为空字典

    用法：
        return jsonify({"success": False, "error": str(e), **report_exception()}), 500
    """
    from ..config import Config

    stack = traceback.format_exc()
    logger.error(f"{context or '请求处理失败'}\n{stack}")

    if Config.DEBUG:
        return {"traceback": stack}
    return {}
