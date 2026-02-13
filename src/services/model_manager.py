import os
from pathlib import Path
from src.services.deepface_wrapper import (
    analyze_face,
    get_deepface_home,
    ensure_model_downloaded
)

def ensure_models():
    """确保所需的模型文件已下载"""
    from pathlib import Path
    
    # 创建临时图片用于模型初始化
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    temp_image_path = temp_dir / "temp_emotion.jpg"
    
    if not temp_image_path.exists():
        import numpy as np
        import cv2
        img = np.zeros((100, 100, 3), np.uint8)
        cv2.imwrite(str(temp_image_path), img)
    
    try:
        # 检查模型文件是否完整
        if not ensure_model_downloaded():
            print("检测到模型文件不完整，正在下载...")
            # 调用analyze会自动下载所需模型
            analyze_face(
                str(temp_image_path),
                actions=['emotion'],
                enforce_detection=False,
            )
            print("模型下载完成")
        else:
            print("模型文件已存在且完整，无需下载")
            
    except Exception as e:
        print(f"模型下载或检查过程中出错: {str(e)}")
        raise
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
