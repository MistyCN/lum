from abc import ABC, abstractmethod
from typing import Dict

class BaseEmotionService(ABC):
    """表情分析服务基类"""
    
    @abstractmethod
    def analyze_emotion(self, image_path: str) -> Dict:
        """分析图片中的表情
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            Dict: 包含表情分析结果的字典
            {
                "dominant_emotion": str,  # 主要情绪
                "emotions": {             # 各种情绪的概率
                    "angry": float,
                    "disgust": float,
                    "fear": float,
                    "happy": float,
                    "sad": float,
                    "surprise": float,
                    "neutral": float
                }
            }
        """
        pass
        
    @abstractmethod
    def is_depressed(self, emotion_result: Dict) -> bool:
        """判断是否呈现抑郁特征
        
        Args:
            emotion_result: analyze_emotion返回的分析结果
            
        Returns:
            bool: 是否呈现抑郁特征
        """
        pass
