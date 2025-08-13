from abc import ABC, abstractmethod
from typing import List, Dict, Generator

class BaseChatService(ABC):
    """聊天服务基类"""
    
    @abstractmethod
    def processMessage(self, message: str) -> str:
        """处理用户消息"""
        pass
        
    @abstractmethod
    def processStreamMessage(self, message: str) -> Generator:
        """流式处理用户消息"""
        pass
        
    @abstractmethod
    def getChatHistory(self) -> List[Dict]:
        """获取聊天历史"""
        pass
        
    @abstractmethod
    def saveChatHistory(self) -> None:
        """保存聊天历史"""
        pass
        
    @abstractmethod
    def loadChatHistory(self) -> None:
        """加载聊天历史"""
        pass
        
    @abstractmethod
    def deleteChatHistory(self) -> None:
        """删除聊天历史"""
        pass
        
    @abstractmethod
    def updateUserPreferences(self, preferences: Dict) -> None:
        """更新用户偏好"""
        pass
