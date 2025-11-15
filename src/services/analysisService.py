from abc import ABC, abstractmethod
from typing import Dict, List
import openai
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
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
        messages = [
            ChatCompletionSystemMessageParam(
                role="system",
                content="""
                现有一个心理分析项目，目前检测到了用户存在心理危机,
                你需要分析用户和机器人的对话，为"介入的专业人士"给出总结和处理建议。
                要求: 1.结合专业心理学知识回答 
                     2.字数控制在200字左右（历史总结占100字左右），适度分行便于阅读
                """
            ),
            ChatCompletionUserMessageParam(
                role="user",
                content=self._format_history(history_messages)
            )
        ]
        
        print("Deepseek危机分析中...")
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=1.0
        )

        if response.choices[0].message.content is not None:
            analysis = response.choices[0].message.content
            vidlie = self.cross_validation(analysis)
            return analysis + "\n\n\n以下为对分析结果多模型交叉验证的结果：\n" + vidlie
        else:
            return ""
    
    def cross_validation(self, ai_response: str) -> str:
        messages = [
            ChatCompletionSystemMessageParam(
                role="system",
                content="""
                现在有一个AI智能体为人类出具建议，请评估这个建议的可靠性并给出0%~100%的置信度，确保人类不会被AI幻觉误导。
                要求: 1.结合专业心理学知识回答
                     2.输出置信度，例如：置信度：90%（由多模型交叉验证得出），并附加100字以内的简短理由
                """
            ),
            ChatCompletionUserMessageParam(
                role="user",
                content=ai_response
            )
        ]
        print("Deepseek交叉验证中...")
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.5
        )

        return response.choices[0].message.content if response.choices[0].message.content is not None else ""
        
    def analyze_preferences(self, history_messages: List[Dict]) -> Dict:
        messages = [
            ChatCompletionSystemMessageParam(
                role="system",
                content="请分析聊天历史，总结用户的话题偏好、性格特点等信息。"
            ),
            ChatCompletionUserMessageParam(
                role="user",
                content=self._format_history(history_messages)
            )
        ]
        
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7
        )
        
        import json
        content = response.choices[0].message.content
        if content is None:
            return {}
        try:
            return json.loads(content)
        except Exception:
            return {"summary": content}
