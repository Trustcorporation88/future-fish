"""
配置管理
统一从项目根目录的 .env 文件加载配置
"""

import os
from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
# 路径: MiroFish/.env (相对于 backend/app/config.py)
project_root_env = os.path.join(os.path.dirname(__file__), '../../.env')

if os.path.exists(project_root_env):
    # override=False: variáveis do Railway/processo têm prioridade sobre .env local
    load_dotenv(project_root_env, override=False)
else:
    load_dotenv(override=False)


def refresh_config() -> None:
    """Relê env vars em runtime (Railway injeta após import do módulo)."""
    Config.LLM_API_KEY = _env_value('LLM_API_KEY')
    Config.LLM_BASE_URL = _env_value('LLM_BASE_URL', 'https://api.openai.com/v1')
    Config.LLM_MODEL_NAME = _env_value('LLM_MODEL_NAME', 'gpt-4o-mini')
    Config.ZEP_API_KEY = _env_value('ZEP_API_KEY')
    Config.FINNHUB_API_KEY = _env_value('FINNHUB_API_KEY', '')
    Config.BRAPI_TOKEN = _env_value('BRAPI_TOKEN', '')
    Config.DEBUG = _env_value('FLASK_DEBUG', 'False').lower() == 'true'
    Config.VIP_ADMIN_USERNAME = _env_value('VIP_ADMIN_USERNAME', '')
    Config.VIP_ADMIN_PASSWORD = _env_value('VIP_ADMIN_PASSWORD', '')
    Config.VIP_CLIENT_USERNAME = _env_value('VIP_CLIENT_USERNAME', '')
    Config.VIP_CLIENT_PASSWORD = _env_value('VIP_CLIENT_PASSWORD', '')
    Config.VIP_CLIENT_USERS = _env_value('VIP_CLIENT_USERS', '')

def _env_value(name: str, default: str | None = None) -> str | None:
    """读取环境变量，并兼容 Warp/模板中常见的 {{valor}} 占位写法。"""
    value = os.environ.get(name, default)
    if value is None:
        return None

    value = value.strip()
    if value.startswith('{{') and value.endswith('}}') and len(value) > 4:
        value = value[2:-2].strip()
    return value


class Config:
    """Flask配置类"""
    
    # Flask配置
    SECRET_KEY = _env_value('SECRET_KEY', 'mirofish-secret-key')
    DEBUG = _env_value('FLASK_DEBUG', 'False').lower() == 'true'
    
    # JSON配置 - 禁用ASCII转义，让中文直接显示（而不是 \uXXXX 格式）
    JSON_AS_ASCII = False
    
    # LLM配置（统一使用OpenAI格式）
    LLM_API_KEY = _env_value('LLM_API_KEY')
    LLM_BASE_URL = _env_value('LLM_BASE_URL', 'https://api.openai.com/v1')
    LLM_MODEL_NAME = _env_value('LLM_MODEL_NAME', 'gpt-4o-mini')
    
    # Zep配置
    ZEP_API_KEY = _env_value('ZEP_API_KEY')

    # Market data配置
    FINNHUB_API_KEY = _env_value('FINNHUB_API_KEY', '')
    BRAPI_TOKEN = _env_value('BRAPI_TOKEN', '')
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'md', 'txt', 'markdown'}
    
    # 文本处理配置
    DEFAULT_CHUNK_SIZE = 500  # 默认切块大小
    DEFAULT_CHUNK_OVERLAP = 50  # 默认重叠大小
    
    # OASIS模拟配置
    OASIS_DEFAULT_MAX_ROUNDS = int(os.environ.get('OASIS_DEFAULT_MAX_ROUNDS', '10'))
    OASIS_SIMULATION_DATA_DIR = os.path.join(os.path.dirname(__file__), '../uploads/simulations')
    
    # OASIS平台可用动作配置
    OASIS_TWITTER_ACTIONS = [
        'CREATE_POST', 'LIKE_POST', 'REPOST', 'FOLLOW', 'DO_NOTHING', 'QUOTE_POST'
    ]
    OASIS_REDDIT_ACTIONS = [
        'LIKE_POST', 'DISLIKE_POST', 'CREATE_POST', 'CREATE_COMMENT',
        'LIKE_COMMENT', 'DISLIKE_COMMENT', 'SEARCH_POSTS', 'SEARCH_USER',
        'TREND', 'REFRESH', 'DO_NOTHING', 'FOLLOW', 'MUTE'
    ]
    
    # Report Agent配置
    REPORT_AGENT_MAX_TOOL_CALLS = int(os.environ.get('REPORT_AGENT_MAX_TOOL_CALLS', '5'))
    REPORT_AGENT_MAX_REFLECTION_ROUNDS = int(os.environ.get('REPORT_AGENT_MAX_REFLECTION_ROUNDS', '2'))
    REPORT_AGENT_TEMPERATURE = float(os.environ.get('REPORT_AGENT_TEMPERATURE', '0.5'))

    # VIP access (admin + client logins)
    VIP_ADMIN_USERNAME = _env_value('VIP_ADMIN_USERNAME', '')
    VIP_ADMIN_PASSWORD = _env_value('VIP_ADMIN_PASSWORD', '')
    VIP_CLIENT_USERNAME = _env_value('VIP_CLIENT_USERNAME', '')
    VIP_CLIENT_PASSWORD = _env_value('VIP_CLIENT_PASSWORD', '')
    VIP_CLIENT_USERS = _env_value('VIP_CLIENT_USERS', '')  # extra clients: user:pass,user2:pass2
    VIP_JWT_HOURS = int(os.environ.get('VIP_JWT_HOURS', '168'))  # 7 days
    JWT_SECRET = _env_value('JWT_SECRET', '')

    @classmethod
    def jwt_secret(cls) -> str:
        return cls.JWT_SECRET or cls.SECRET_KEY or 'mirofish-jwt-fallback'

    @classmethod
    def vip_auth_enabled(cls) -> bool:
        explicit = _env_value('VIP_AUTH_ENABLED')
        if explicit is not None:
            return explicit.lower() == 'true'
        has_admin = bool(cls.VIP_ADMIN_USERNAME and cls.VIP_ADMIN_PASSWORD)
        has_client = bool(cls.VIP_CLIENT_USERNAME and cls.VIP_CLIENT_PASSWORD)
        has_extra = bool(cls.VIP_CLIENT_USERS and ':' in cls.VIP_CLIENT_USERS)
        return has_admin or has_client or has_extra
    
    @classmethod
    def validate(cls) -> list[str]:
        """验证必要配置"""
        refresh_config()
        errors: list[str] = []
        if not cls.LLM_API_KEY:
            errors.append("LLM_API_KEY 未配置")
        if not cls.ZEP_API_KEY:
            errors.append("ZEP_API_KEY 未配置")
        return errors

