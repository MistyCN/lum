from typing import Dict
import cv2
import numpy as np
from deepface import DeepFace
from src.services.baseEmotionService import BaseEmotionService
from src.services.model_manager import ensure_models

class DeepfaceEmotionService(BaseEmotionService):
    """基于Deepface的表情分析服务实现"""
    
    def __init__(self):
        """初始化表情分析服务"""
        # 确保模型已下载
        ensure_models()
        # 抑郁倾向判断阈值
        self.depression_thresholds = {
            "sad": 0.4,      # 悲伤情绪阈值
            "fear": 0.3,     # 恐惧情绪阈值
            "disgust": 0.3,  # 厌恶情绪阈值
            "angry": 0.3     # 愤怒情绪阈值
        }
    
    def analyze_emotion(self, image_path: str) -> Dict:
        """分析图片中的表情"""
        try:
            result = DeepFace.analyze(
                image_path,
                actions=['emotion'],
                enforce_detection=False
            )
            if isinstance(result, list):
                result = result[0]
            emotions = {}
            for emotion, value in result["emotion"].items():
                if isinstance(value, (np.float32, np.float64)):
                    emotions[emotion] = float(value)
                else:
                    emotions[emotion] = value
            return {
                "dominant_emotion": result["dominant_emotion"],
                "emotions": emotions
            }
            
        except Exception as e:
            print(f"表情分析出错: {str(e)}")
            return {
                "dominant_emotion": "unknown",
                "emotions": {
                    "angry": 0,
                    "disgust": 0,
                    "fear": 0,
                    "happy": 0,
                    "sad": 0,
                    "surprise": 0,
                    "neutral": 0
                }
            }
            
    def is_depressed(self, emotion_result: Dict) -> bool:
        """判断是否呈现抑郁特征"""
        emotions = emotion_result["emotions"]
        for emotion, threshold in self.depression_thresholds.items():
            if emotions.get(emotion, 0) >= threshold:
                return True
        if (emotions.get("neutral", 0) >= 0.8 and 
            emotions.get("happy", 0) <= 0.1):
            return True
            
        return False
        
    def capture_and_analyze(self, camera_index: int = 0) -> Dict:
        """从摄像头捕获并分析表情
        
        Args:
            camera_index: 摄像头索引，默认为0（第一个摄像头）
            
        Returns:
            Dict: 表情分析结果
        """
        try:
            cap = cv2.VideoCapture(camera_index)
            if not cap.isOpened():
                raise Exception("无法打开摄像头")
            ret, frame = cap.read()
            if not ret:
                raise Exception("无法捕获图像")
            temp_image = "temp_capture.jpg"
            cv2.imwrite(temp_image, frame)
            result = self.analyze_emotion(temp_image)
            cap.release()
            return result
        except Exception as e:
            print(f"捕获和分析表情时出错: {str(e)}")
            return {
                "dominant_emotion": "unknown",
                "emotions": {
                    "angry": 0,
                    "disgust": 0,
                    "fear": 0,
                    "happy": 0,
                    "sad": 0,
                    "surprise": 0,
                    "neutral": 0
                }
            }
