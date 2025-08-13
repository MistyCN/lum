from abc import ABC, abstractmethod
from typing import Dict, List
import openai
from ..config import Config

class BaseAnalysisService(ABC):
    """AI分析服务基类"""
    
    @abstractmethod
    def analyze_danger(self, history_messages: List[Dict]) -> str:
        """分析危险内容"""
        pass
    
    @abstractmethod
    def analyze_preferences(self, history_messages: List[Dict]) -> Dict:
        """分析用户偏好"""
        pass

class DeepseekAnalysisService(BaseAnalysisService):
    """基于Deepseek的AI分析服务实现"""
    
    def __init__(self):
        self.config = Config()
        self.client = openai.OpenAI(
            api_key=self.config.deepseekApiKey,
            base_url="https://api.deepseek.com"
        )
        
    def _format_history(self, history_messages: List[Dict]) -> str:
        """格式化历史消息"""
        return "\n".join([
            f"{msg['role']}:{msg['content']}"
            for msg in history_messages
        ])
        
    def analyze_danger(self, history_messages: List[Dict]) -> str:
        """分析对话中的危险内容"""
        messages = [
            {
                "role": "system",
                "content": """
                现有一个心理分析项目，目前检测到了用户存在心理危机,
                你需要分析用户和机器人的对话，为"介入的专业人士"给出总结和处理建议。
                要求: 1.结合专业心理学知识回答 
                     2.字数控制在200字左右（历史总结占100字左右），适度分行便于阅读
                """
            },
            {
                "role": "user",
                "content": self._format_history(history_messages)
            }
        ]
        
        print("Deepseek危机分析中...")
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=1.0
        )
        
        return response.choices[0].message.content
        
    def analyze_preferences(self, history_messages: List[Dict]) -> Dict:
        """分析用户偏好"""
        messages = [
            {
                "role": "system",
                "content": "请分析聊天历史，总结用户的话题偏好、性格特点等信息。"
            },
            {
                "role": "user",
                "content": self._format_history(history_messages)
            }
        ]
        
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7
        )
        
        return response.choices[0].message.content
