from typing import List, Dict, Generator
import json
import os
from datetime import datetime
from cozepy import Coze, TokenAuth, Message, ChatEventType, COZE_CN_BASE_URL
from src.services.baseChatService import BaseChatService
from src.config import Config
from src.services.dataService import DataService

class CozeChatService(BaseChatService):
    """基于Coze的聊天服务实现"""
    
    def __init__(self):
        self.config = Config()
        self.chatHistory = []
        # 使用 data/chat 作为聊天数据存储目录
        self.data_service = DataService()
        token = self.config.cozeApiToken if self.config.cozeApiToken is not None else ""
        if not token:
            raise ValueError("Coze API token is missing. Please set cozeApiToken in the configuration.")
        self.coze = Coze(
            auth=TokenAuth(token=token),
            base_url=COZE_CN_BASE_URL
        )
    
    def processStreamMessage(self, message: str) -> Generator:
        """处理流式消息"""
        if not message:
            yield {"type": "error", "message": "请输入有效的信息。"}
            return
        user_ts = datetime.now().isoformat()
        self.chatHistory.append({"role": "user", "message": message, "timestamp": user_ts})
        # 立即保存用户发言到 DataService
        try:
            self.data_service.save_chat(user_id="", message=message, role="user", timestamp=user_ts)
        except Exception:
            pass
        context_messages = self._prepareContextMessages()
        current = ''
        for event in self.coze.chat.stream(
            bot_id="7499749049093570598",
            user_id="random_string",
            additional_messages=context_messages
        ):
            if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                if event.message is not None and hasattr(event.message, "content"):
                    print(event.message.content, end="", flush=True)
                    current += event.message.content
                    yield {"type": "normal", "message": event.message.content}
        self.chatHistory.append({"role": "assistant", "message": current})
        # 保存助理回复
        assistant_ts = datetime.now().isoformat()
        self.chatHistory[-1]["timestamp"] = assistant_ts
        try:
            self.data_service.save_chat(user_id="", message=current, role="assistant", timestamp=assistant_ts)
        except Exception:
            pass

    def processMessage(self, message: str) -> str:
        """处理单条消息"""
        m = self.processStreamMessage(message)
        sum = ""
        for each in m:
            sum += each.get('message', '')
        print("\n历史记录:", self.chatHistory, "\n")
        return sum

    def _prepareContextMessages(self) -> List[Message]:
        """准备上下文消息"""
        messages = []
        for msg in self.chatHistory[-self.config.maxHistoryLength:]:
            # 兼容旧字段名 'content'，并对缺失消息做容错处理
            text = None
            if isinstance(msg, dict):
                text = msg.get("message") if msg.get("message") is not None else msg.get("content")
            if not text:
                # 跳过没有实际文本的历史项
                continue
            if msg.get("role") == "user":
                messages.append(Message.build_user_question_text(text))
            else:
                messages.append(Message.build_assistant_answer(text))
        return messages

    def getChatHistory(self) -> List[Dict]:
        """获取聊天历史"""
        return self.chatHistory

    def saveChatHistory(self) -> None:
        """保存聊天历史到文件"""
        try:
            # 使用 DataService 覆盖写入 chats.json
            self.data_service._write_json(self.data_service.chats_file, self.chatHistory)
        except Exception as e:
            print(f"保存聊天历史时出错: {str(e)}")
            raise

    def loadChatHistory(self) -> None:
        """从文件加载聊天历史"""
        try:
            # 优先从 DataService 加载
            self.chatHistory = self.data_service.get_chats()
        except FileNotFoundError:
            print("未找到聊天历史文件")
            self.chatHistory = []
        except Exception as e:
            print(f"加载聊天历史时出错: {str(e)}")
            raise

    def deleteChatHistory(self) -> None:
        """删除聊天历史"""
        self.chatHistory = []
        try:
            # 清空 DataService 中的 chats 文件
            self.data_service._write_json(self.data_service.chats_file, [])
        except Exception:
            pass
        
    def updateUserPreferences(self, preferences: Dict) -> None:
        """更新用户喜好"""
        ts = datetime.now().isoformat()
        entry = {"role": "user", "message": "当前最新的用户喜好:" + str(preferences), "timestamp": ts}
        self.chatHistory.append(entry)
        try:
            # 保存时使用 message 字段
            self.data_service.save_chat(user_id="", message=entry["message"], role="user", timestamp=ts)
        except Exception:
            pass
