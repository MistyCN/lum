"""
Luminest 项目入口点
"""
from src.main import main
from src.services.model_manager import ensure_models

if __name__ == "__main__":
    ensure_models()
    main()
