from typing import Dict
import cv2
import numpy as np
import os
from datetime import datetime
from src.services.deepface_wrapper import analyze_face

from src.services.baseEmotionService import BaseEmotionService
from src.services.model_manager import ensure_models
from src.services.dataService import DataService

class DeepfaceEmotionService(BaseEmotionService):
    """基于Deepface的表情分析服务实现"""
    
    def __init__(self):
        """初始化表情分析服务"""
        # 确保模型已下载
        ensure_models()
        # DataService 用于持久化表情识别记录，保存在 data/emotion
        try:
            self.data_service = DataService()
        except Exception:
            # 若初始化失败，仍确保属性存在以避免后续报错
            self.data_service = None
        # 抑郁倾向判断阈值
        self.depression_thresholds = {
            "sad": 0.4,      # 悲伤情绪阈值
            "fear": 0.3,     # 恐惧情绪阈值
            "disgust": 0.3,  # 厌恶情绪阈值
            "angry": 0.3     # 愤怒情绪阈值
        }
    
    def normalize_emotions(self, emotions: Dict) -> Dict:
        """归一化情绪值，确保所有情绪值在0-1之间，并且总和为1"""
        # 确保所有值非负
        normalized = {k: max(0, float(v)) for k, v in emotions.items()}
        
        # 计算总和
        total = sum(normalized.values())
        
        # 如果总和为0，返回平均分布
        if total == 0:
            num_emotions = len(normalized)
            return {k: 1.0/num_emotions for k in normalized}
            
        # 归一化处理
        return {k: v/total for k, v in normalized.items()}

    def analyze_emotion(self, image_path: str) -> Dict:
        """分析图片中的表情"""
        try:
            result = analyze_face(
                image_path,
                actions=['emotion'],
                enforce_detection=False
            )
            
            if result is None:
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
            
            # 归一化情绪值
            normalized_emotions = self.normalize_emotions(result["emotion"])
            
            # 找出最大值对应的情绪
            dominant_emotion = max(normalized_emotions.items(), key=lambda x: x[1])[0]
            # 保存识别结果到 DataService（非阻塞）
            try:
                record = {
                    "user_id": "",
                    "dominant_emotion": dominant_emotion,
                    "emotions": normalized_emotions,
                    "timestamp": datetime.now().isoformat()
                }
                if self.data_service is not None:
                    # DataService.save_emotion 会补充 timestamp
                    self.data_service.save_emotion(record)
            except Exception as e:
                # 保存失败不影响主流程
                print(f"保存表情记录失败: {e}")

            return {
                "dominant_emotion": dominant_emotion,
                "emotions": normalized_emotions
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
        """判断是否呈现抑郁特征
        
        Args:
            emotion_result: analyze_emotion返回的分析结果
            
        Returns:
            bool: 是否呈现抑郁特征
        """
        emotions = emotion_result["emotions"]
        negative_emotions = ["sad", "fear", "disgust", "angry"]
        positive_emotions = ["happy", "surprise"]
        
        # 计算正面和负面情绪的总和
        total_negative = sum(emotions.get(e, 0) for e in negative_emotions)
        total_positive = sum(emotions.get(e, 0) for e in positive_emotions)
        neutral = emotions.get("neutral", 0)
        
        reasons = []
        risk_level = "low"
        
        # 检查各种抑郁特征
        if total_negative > 0.5:  # 负面情绪占主导
            reasons.append("负面情绪比重较高")
            risk_level = "medium"
            
        if total_positive < 0.1 and neutral > 0.4:  # 积极情绪明显缺乏
            reasons.append("积极情绪明显不足")
            risk_level = "medium"
            
        # 检查具体的负面情绪是否超过阈值
        for emotion, threshold in self.depression_thresholds.items():
            if emotions.get(emotion, 0) >= threshold:
                if emotion == "sad":
                    reasons.append("呈现明显的悲伤情绪")
                    risk_level = "high"
                else:
                    reasons.append(f"呈现明显的{emotion}情绪")
                    risk_level = "medium"
        
        # 特殊情况：长期性情绪平淡
        if neutral >= 0.8 and total_positive <= 0.1:
            reasons.append("情绪表现过于平淡")
            risk_level = "medium"
        
        # 综合判断
        is_depressed = len(reasons) > 0 and (
            risk_level in ["medium", "high"] or
            (total_negative > total_positive * 2 and total_negative > 0.3)
        )
        
        return is_depressed
        
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
