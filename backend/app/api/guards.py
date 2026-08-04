"""
蓝图级请求校验

把会参与文件路径拼接的 ID 集中在进入视图之前校验，
避免逐个路由手写校验时漏掉某个入口。
"""

from flask import request

from ..utils.ids import validate_id


# 会被用于拼接文件路径的 ID。graph_id / entity_uuid / task_id 不在其中：
# 前两者是 Zep 侧标识，后者只用于内存中的任务表，都不参与路径拼接。
_PATH_ID_KEYS = ('project_id', 'simulation_id', 'report_id')


class MalformedBodyError(ValueError):
    """请求体声明为 JSON，但无法解析或不是对象"""


def _json_body():
    """
    取出 JSON 请求体，非法时抛 MalformedBodyError

    各路由统一写 `data = request.get_json(silent=True) or {}` 再 `data.get(...)`，
    因此请求体若是数组或字符串（没有 .get），会在视图里抛 AttributeError，
    被通用 except 吞成 500。在这里提前拦成 400，19 个路由一次性覆盖。

    空请求体按 {} 放行：前端有些 POST 不带 body 却带着 JSON 头，
    这类请求本来就能正常工作，不应该被这次改动破坏。
    """
    if not (request.content_type and 'json' in request.content_type):
        return None

    if not request.get_data():
        return {}

    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise MalformedBodyError("请求体必须是 JSON 对象")
    return body


def _validate_path_ids():
    """
    在进入视图之前校验请求中的 ID

    各路由都有自己的通用 except Exception，若在视图内部校验，
    非法 ID 会被吞成 500。放在这里抛出，异常不经过视图，
    直接由应用级的 InvalidIdError 处理器转成 400。

    只校验非空值：ID 缺失时各路由自己会返回更具体的提示。
    """
    sources = [request.view_args or {}, request.args]
    body = _json_body()
    if body:
        sources.append(body)

    for source in sources:
        for name in _PATH_ID_KEYS:
            value = source.get(name)
            if value:
                validate_id(value, name)


def register_path_id_guard(*blueprints) -> None:
    """给蓝图挂上 ID 校验钩子"""
    for bp in blueprints:
        bp.before_request(_validate_path_ids)
