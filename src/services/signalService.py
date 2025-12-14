from typing import List, Dict, Any
from datetime import datetime
import json
import os
from src.services.baseSignalService import BaseSignalService

class SignalService(BaseSignalService):
    """危险信号服务实现"""
    
    def __init__(self, signals_file: str = os.path.join("data", "signals.json")):
        """
        初始化危险信号服务
        :param signals_file: 信号存储文件路径
        """
        self.signals: List[Dict] = []
        self.signals_file = signals_file
        # 确保目录存在
        try:
            dir_path = os.path.dirname(self.signals_file)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
        except Exception:
            pass
        self.load_signals()
        
    def add_emotion_signal(self, emotion_data: Dict) -> None:
        """添加表情分析危险信号
        
        Args:
            emotion_data: 表情分析结果
        """
        signal = {
            "type": "emotion",
            "user_id": "",
            "trigger_message": emotion_data["dominant_emotion"],
            "timestamp": datetime.now().isoformat(),
            "data": {
                "dominant_emotion": emotion_data["dominant_emotion"],
                "emotions": emotion_data["emotions"]
            },
            "analyze": f"用户表情呈现出抑郁特征，请关注用户情绪健康。"
        }
        self.add_signal(signal)
        
    def add_signal(self, signal: Dict[str, Any]) -> None:
        """
        添加一个危险信号
        :param signal: 危险信号数据
        """
        if not isinstance(signal, dict):
            raise ValueError("信号数据必须是字典类型")
        print("收到了新的危机信号:", signal.get('type'), signal.get('trigger_message'))
        self.signals.append(signal)
        try:
            self.save_signals()
        except Exception as e:
            # 保存失败时打印错误，但不要抛出异常以免影响调用者（例如流式处理器）
            print(f"保存危险信号失败: {e}")
        
    def add_dangerous_chat(self, user_id: str, content: str, analysis: str) -> None:
        """
        添加一个危险对话记录
        :param user_id: 用户ID
        :param content: 对话内容
        :param analysis: 分析结果
        """
        signal = {
            "type": "dangerous_chat",
            "user_id": user_id,
            "trigger_message": content,
            "analyze": analysis,
            "timestamp": datetime.now().isoformat()
        }
        self.add_signal(signal)
        
    def get_signals(self) -> List[Dict]:
        """
        获取所有危险信号
        :return: 危险信号列表（倒序排列）
        """
        return self.signals[::-1]
        
    def save_signals(self) -> None:
        """保存信号到文件"""
        try:
            with open(self.signals_file, 'w', encoding='utf-8') as f:
                json.dump(self.signals, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存危险信号时出错: {str(e)}")
            # 不抛出异常，保证调用流程稳定
            return
            
    def load_signals(self) -> None:
        """从文件加载信号"""
        if os.path.exists(self.signals_file):
            try:
                with open(self.signals_file, 'r', encoding='utf-8') as f:
                    self.signals = json.load(f)
            except Exception as e:
                print(f"加载危险信号时出错: {str(e)}")
                print("还没保存过危险信号记录")
                self.signals = []
        else:
            print("还没保存过危险信号记录")
            self.signals = []
    
    def clear_signals(self) -> None:
        """清空所有信号"""
        self.signals = []
        
    def get_signals_by_type(self, signal_type: str) -> List[Dict]:
        """
        按类型获取信号
        :param signal_type: 信号类型
        :return: 指定类型的信号列表
        """
        return [signal for signal in self.signals if signal.get("type") == signal_type]
        
    def get_signals_by_user(self, user_id: str) -> List[Dict]:
        """
        获取指定用户的所有信号
        :param user_id: 用户ID
        :return: 该用户的信号列表
        """
        return [signal for signal in self.signals if signal.get("user_id") == user_id]
