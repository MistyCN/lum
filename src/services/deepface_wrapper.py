import sys
import os
import warnings
import numpy as np
import importlib.util
import importlib.machinery
from pathlib import Path
import time

def init_deepface():
    """初始化 DeepFace 的兼容性包装"""
    try:
        # 禁用 TensorFlow 警告
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        warnings.filterwarnings('ignore', category=FutureWarning)
        
        # 确保使用正确的 keras 版本
        if 'keras' in sys.modules:
            del sys.modules['keras']
        os.environ['KERAS_HOME'] = str(Path.home() / '.keras')

        reload_six = importlib.reload
        
        from deepface import DeepFace
        return DeepFace
    except Exception as e:
        print(f"DeepFace 初始化错误: {str(e)}")
        raise

def analyze_face_with_retry(image_path, actions=['emotion'], enforce_detection=False, silent=True):
    """
    包装 DeepFace.analyze 函数，处理所有可能的兼容性问题（带重试机制）
    """
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
            
        retries = 3
        while retries > 0:
            try:
                DeepFace = init_deepface()
                result = DeepFace.analyze(
                    img_path=image_path,
                    actions=actions,
                    enforce_detection=enforce_detection,
                    silent=silent
                )
                
                # 确保结果是单个分析结果
                if isinstance(result, list):
                    result = result[0]
                    
                # 确保情绪值是普通的 Python float
                if isinstance(result, dict) and "emotion" in result:
                    emotions = {}
                    for emotion, value in result["emotion"].items():
                        if isinstance(value, np.floating):
                            emotions[emotion] = float(value)
                        else:
                            emotions[emotion] = value
                    result["emotion"] = emotions
                    
                return result
            except Exception as e:
                retries -= 1
                if retries > 0:
                    print(f"分析失败，正在重试... ({3-retries}/3)")
                    time.sleep(1)
                else:
                    raise e
                    
    except Exception as e:
        print(f"表情分析错误: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        return None

def get_deepface_weights_dir():
    """获取 DeepFace 模型存储路径"""
    home = Path.home()
    deepface_home = home / '.deepface'
    weights_dir = deepface_home / 'weights'
    return str(weights_dir)

def ensure_model_downloaded():
    """确保模型文件被正确下载"""
    weights_dir = Path(get_deepface_weights_dir())
    required_models = {
        'emotion': ['facial_expression_model_weights.h5'],
        #'face_detector': ['haarcascade_frontalface_default.xml'],
    }
    
    # 确保目录存在
    weights_dir.mkdir(parents=True, exist_ok=True)
    
    # 检查每个必需的模型文件
    missing_models = []
    for category, files in required_models.items():
        category_dir = weights_dir / files[0].split('/')[0]
        if not category_dir.exists():
            missing_models.append(category)
    
    return len(missing_models) == 0

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
        if isinstance(result, dict) and "emotion" in result:
            emotions = {}
            for emotion, value in result["emotion"].items():
                if isinstance(value, np.floating):
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
