import sys
import os
import warnings
import numpy as np

def init_deepface():
    """初始化 DeepFace 的兼容性包装"""
    if sys.version_info >= (3, 12):
        # 在导入 DeepFace 之前，先处理 imp 模块的问题
        import importlib.util
        sys.modules['imp'] = importlib.util

    # 现在可以安全地导入 DeepFace
    from deepface import DeepFace
    return DeepFace

def analyze_face(image_path, actions=['emotion'], enforce_detection=False):
    """
    包装 DeepFace.analyze 函数，处理所有可能的兼容性问题
    """
    try:
        DeepFace = init_deepface()
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
    except Exception as e:
        print(f"Face analysis error: {str(e)}")
        return None

def get_deepface_home():
    """获取 DeepFace 模型存储路径"""
    return os.path.join(os.path.expanduser("~"), ".deepface", "weights")
