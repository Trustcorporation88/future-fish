"""
MiroFish Backend 启动入口
"""

import os
import sys

# 解决 Windows 控制台中文乱码问题：在所有导入之前设置 UTF-8 编码
if sys.platform == 'win32':
    # 设置环境变量确保 Python 使用 UTF-8
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    # 重新配置标准输出流为 UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.config import Config, refresh_config


def main():
    """主函数"""
    refresh_config()
    errors = Config.validate()
    # DEBUG: log SUPABASE vars
    import logging as _log
    _dbg = _log.getLogger('mirofish.startup')
    _dbg.info("DEBUG SUPABASE_URL set=%s len=%d", bool(Config.SUPABASE_URL), len(Config.SUPABASE_URL or ''))
    _dbg.info("DEBUG SUPABASE_SERVICE_KEY set=%s len=%d", bool(Config.SUPABASE_SERVICE_KEY), len(Config.SUPABASE_SERVICE_KEY or ''))
    _dbg.info("DEBUG SUPABASE_BUCKET=%s", Config.SUPABASE_BUCKET)
    _dbg.info("DEBUG storage_enabled=%s", Config.storage_enabled())
    if errors:
        print("Aviso de configuracao (app sobe, mas simulacoes podem falhar):")
        for err in errors:
            print(f"  - {err}")
        print("Defina LLM_API_KEY e ZEP_API_KEY no Railway → Variables")
        if os.environ.get('REQUIRE_CONFIG', '').lower() in ('1', 'true', 'yes'):
            sys.exit(1)
    
    # 创建应用
    app = create_app()
    
    # Railway usa PORT; local usa FLASK_PORT
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('PORT') or os.environ.get('FLASK_PORT', 5001))
    debug = Config.DEBUG

    # 对外监听时开启 DEBUG 会把 Werkzeug 调试控制台暴露到网络上，
    # 等同于允许任意人执行代码，因此直接拒绝启动。
    if debug and host not in ('127.0.0.1', 'localhost', '::1'):
        print(
            f"拒绝启动：FLASK_DEBUG 已开启且监听地址为 {host}。\n"
            "调试模式会暴露可执行代码的交互式控制台。\n"
            "请设置 FLASK_DEBUG=false，或将 FLASK_HOST 改为 127.0.0.1。"
        )
        sys.exit(1)

    # 启动服务
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    main()

