import os
from deepface import DeepFace
from pathlib import Path

def ensure_models():
    """确保所需的模型文件已下载"""
    # DeepFace模型默认存储路径
    base_model_path = os.path.join(Path.home(), ".deepface", "weights")
    # 创建临时图片用于模型初始化
    temp_image_path = "temp_emotion.jpg"
    if not os.path.exists(temp_image_path):
        import numpy as np
        import cv2
        img = np.zeros((100, 100, 3), np.uint8)
        cv2.imwrite(temp_image_path, img)
    
    try:
        if os.path.exists(base_model_path):
            print("首次运行，正在下载必要的模型...")
            os.makedirs(base_model_path, exist_ok=True)
            # 调用analyze会自动下载所需模型
            DeepFace.analyze(
                temp_image_path,
                actions=['emotion'],
                enforce_detection=False
            )
            print("模型下载完成")
        else:
            print("模型文件已存在，无需下载")
            
    except Exception as e:
        print(f"模型下载或检查过程中出错: {str(e)}")
        raise
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
