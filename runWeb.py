"""
Luminest Web应用启动脚本
"""
from src.webapp import create_app
from src.services.model_manager import ensure_models


if __name__ == "__main__":
    # 预下载模型
    ensure_models()
    # 启动应用
    app = create_app()
    app.run(port=5000, debug=True)
