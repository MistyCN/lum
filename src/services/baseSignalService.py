from abc import ABC, abstractmethod
from typing import List, Dict

class BaseSignalService(ABC):
    """危险信号服务基类"""
    
    @abstractmethod
    def add_signal(self, signal: Dict) -> None:
        """添加一个危险信号"""
        pass
        
    @abstractmethod
    def add_dangerous_chat(self, user_id: str, content: str, analysis: str) -> None:
        """添加一个危险对话记录"""
        pass
    
    @abstractmethod
    def get_signals(self) -> List[Dict]:
        """获取所有危险信号"""
        pass
    
    @abstractmethod
    def save_signals(self) -> None:
        """保存信号到文件"""
        pass
    
    @abstractmethod
    def load_signals(self) -> None:
        """从文件加载信号"""
        pass
