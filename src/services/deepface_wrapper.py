import sys
import os
import warnings
import numpy as np
import importlib.util
import importlib.machinery

def create_module(name):
    """创建一个模拟的 imp 模块"""
    class MockImp:
        @staticmethod
        def find_module(name, path=None):
            if path is None:
                path = sys.path
            try:
                # 使用新的 importlib API
                spec = importlib.util.find_spec(name, path)
                if spec is None:
                    return None
                return None, spec.origin, ('.py', 'r', importlib.machinery.SourceFileLoader)
            except Exception:
                return None
        
        @staticmethod
        def load_module(name):
            spec = importlib.util.find_spec(name)
            if spec is None:
                raise ImportError(f"No module named '{name}'")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module

    return MockImp()

def init_deepface():
    """初始化 DeepFace 的兼容性包装"""
    if sys.version_info >= (3, 12):
        # 创建一个模拟的 imp 模块
        sys.modules['imp'] = create_module('imp')

    # 现在可以安全地导入 DeepFace
    from deepface import DeepFace
    return DeepFace

def analyze_face(image_path, actions=['emotion'], enforce_detection=False):
    """
    包装 DeepFace.analyze 函数，处理所有可能的兼容性问题
    """
    try:
        print("正在初始化 DeepFace...")
        DeepFace = init_deepface()
        
        print(f"正在分析图片: {image_path}")
        result = DeepFace.analyze(
            image_path,
            actions=actions,
            enforce_detection=enforce_detection
        )
        
        # 确保结果是单个分析结果
        if isinstance(result, list):
            result = result[0]
            
        # 确保情绪值是普通的 Python float
        if "emotion" in result:
            emotions = {}
            for emotion, value in result["emotion"].items():
                if isinstance(value, (np.float32, np.float64)):
                    emotions[emotion] = float(value)
                else:
                    emotions[emotion] = value
            result["emotion"] = emotions
            
        return result
    except ImportError as e:
        print(f"DeepFace 导入错误: {str(e)}")
        print("请确保已正确安装 DeepFace 及其依赖")
        raise
    except Exception as e:
        print(f"表情分析错误: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        return None

def get_deepface_home():
    """获取 DeepFace 模型存储路径"""
    return os.path.join(os.path.expanduser("~"), ".deepface", "weights")
