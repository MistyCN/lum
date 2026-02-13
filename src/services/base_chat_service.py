from abc import ABC, abstractmethod
from typing import List, Dict, Generator
from cozepy import Message

class BaseChatService(ABC):
    """聊天服务基类"""
    
    @abstractmethod
    def process_message(self, user_message: str) -> str:
        """处理用户消息"""
        pass
        
    @abstractmethod
    def process_stream_message(self, user_message: str) -> Generator:
        """处理流式消息"""
        pass
    
    @abstractmethod
    def get_chat_history(self) -> List[Dict]:
        """获取聊天历史"""
        pass
    
    @abstractmethod
    def save_chat_history(self) -> None:
        """保存聊天历史"""
        pass
    
    @abstractmethod
    def load_chat_history(self) -> None:
        """加载聊天历史"""
        pass
    
    @abstractmethod
    def delete_chat_history(self) -> None:
        """删除聊天历史"""
        pass
