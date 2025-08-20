from typing import List, Dict, Generator
import json
from cozepy import Coze, TokenAuth, Message, ChatEventType, COZE_CN_BASE_URL
from src.services.baseChatService import BaseChatService
from src.config import Config

class CozeChatService(BaseChatService):
    """基于Coze的聊天服务实现"""
    
    def __init__(self):
        self.config = Config()
        self.chatHistory = []
        self.coze = Coze(
            auth=TokenAuth(token=self.config.cozeApiToken),
            base_url=COZE_CN_BASE_URL
        )
    
    def processStreamMessage(self, userMessage: str) -> Generator:
        """处理流式消息"""
        if not userMessage:
            yield {"type": "error", "message": "请输入有效的信息。"}
            return
        self.chatHistory.append({"role": "user", "content": userMessage})
        context_messages = self._prepareContextMessages()
        current = ''
        for event in self.coze.chat.stream(
            bot_id="7499749049093570598",
            user_id="random_string",
            additional_messages=context_messages
        ):
            if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                print(event.message.content, end="", flush=True)
                current += event.message.content
                yield {"type": "normal", "message": event.message.content}
        self.chatHistory.append({"role": "assistant", "content": current})

    def processMessage(self, userMessage: str) -> str:
        """处理单条消息"""
        m = self.processStreamMessage(userMessage)
        sum = ""
        for each in m:
            sum += each.get('message', '')
        print("\n历史记录:", self.chatHistory, "\n")
        return sum

    def _prepareContextMessages(self) -> List[Message]:
        """准备上下文消息"""
        messages = []
        for msg in self.chatHistory[-self.config.maxHistoryLength:]:
            if msg["role"] == "user":
                messages.append(Message.build_user_question_text(msg["content"]))
            else:
                messages.append(Message.build_assistant_answer(msg["content"]))
        return messages

    def getChatHistory(self) -> List[Dict]:
        """获取聊天历史"""
        return self.chatHistory

    def saveChatHistory(self) -> None:
        """保存聊天历史到文件"""
        try:
            with open('chat_history.json', 'w', encoding='utf-8') as f:
                json.dump(self.chatHistory, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存聊天历史时出错: {str(e)}")
            raise

    def loadChatHistory(self) -> None:
        """从文件加载聊天历史"""
        try:
            with open('chat_history.json', 'r', encoding='utf-8') as f:
                self.chatHistory = json.load(f)
        except FileNotFoundError:
            print("未找到聊天历史文件")
            self.chatHistory = []
        except Exception as e:
            print(f"加载聊天历史时出错: {str(e)}")
            raise

    def deleteChatHistory(self) -> None:
        """删除聊天历史"""
        self.chatHistory = []
        
    def updateUserPreferences(self, preferences: Dict) -> None:
        """更新用户喜好"""
        self.chatHistory.append({
            "role": "user",
            "content": "当前最新的用户喜好:" + str(preferences)
        })
