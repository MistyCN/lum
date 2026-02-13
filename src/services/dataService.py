from typing import List, Dict, Any, Optional
import os
import json
from datetime import datetime


class DataService:
    """处理需要保存的数据：聊天记录和表情识别结果

    存储文件（默认）：
    - data/chats.json
    - data/emotions.json
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.chats_file = os.path.join(self.data_dir, "chats.json")
        self.emotions_file = os.path.join(self.data_dir, "emotions.json")

    # ---- 低级文件操作辅助方法 ----
    def _read_json(self, path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_json(self, path: str, data: List[Dict[str, Any]]) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def _now_iso(self) -> str:
        return datetime.now().isoformat()

    # ---- 聊天记录相关 ----
    def save_chat(
        self,
        user_id: str,
        message: str,
        role: str = "user",
        timestamp: Optional[str] = None,
    ) -> None:
        """保存一条聊天记录

        Args:
            user_id: 用户ID
            message: 消息文本
            role: 消息角色，'user' 或 'assistant' 等
            timestamp: ISO 格式时间字符串（可选）
        """
        if timestamp is None:
            timestamp = self._now_iso()

        entry = {
            "type": "chat",
            "user_id": user_id,
            "role": role,
            "message": message,
            "timestamp": timestamp,
        }

        chats = self._read_json(self.chats_file)
        chats.append(entry)
        self._write_json(self.chats_file, chats)

    def get_chats(self) -> List[Dict[str, Any]]:
        """返回按时间升序排列的所有聊天记录"""
        chats = self._read_json(self.chats_file)
        return sorted(chats, key=lambda x: x.get("timestamp", ""))

    # ---- 表情记录相关 ----
    def save_emotion(self, emotion_data: Dict[str, Any]) -> None:
        """保存一条表情识别结果。

        emotion_data 推荐格式参考 `add_emotion_signal` 中的参数：
        {
            "dominant_emotion": "sad",
            "emotions": { ... },
            "user_id": "optional",
            "timestamp": "optional ISO time"
        }
        """
        # 填充 timestamp
        timestamp = emotion_data.get("timestamp") or self._now_iso()
        entry = {
            "type": "emotion",
            "user_id": emotion_data.get("user_id", ""),
            "trigger_message": emotion_data.get("dominant_emotion", ""),
            "timestamp": timestamp,
            "data": {
                "dominant_emotion": emotion_data.get("dominant_emotion", ""),
                "emotions": emotion_data.get("emotions", {}),
            },
            "note": emotion_data.get("note", "")
        }

        emotions = self._read_json(self.emotions_file)
        emotions.append(entry)
        self._write_json(self.emotions_file, emotions)

    def get_emotions(self) -> List[Dict[str, Any]]:
        """返回按时间升序排列的所有表情记录"""
        emotions = self._read_json(self.emotions_file)
        return sorted(emotions, key=lambda x: x.get("timestamp", ""))

    # ---- 合并读取 ----
    def get_all_data(self) -> List[Dict[str, Any]]:
        """返回聊天记录与表情记录的合并列表，按时间升序排列"""
        chats = self._read_json(self.chats_file)
        emotions = self._read_json(self.emotions_file)
        combined = []
        # 标准化各条目的 timestamp 字段
        for c in chats:
            combined.append(c)
        for e in emotions:
            combined.append(e)

        # 尝试以 ISO 时间排序，降级到字符串比较
        def _key(item: Dict[str, Any]) -> str:
            return item.get("timestamp", "")

        return sorted(combined, key=_key)

    # ---- 可选：清理数据 ----
    def clear_all(self) -> None:
        """清空聊天和表情数据文件（慎重使用）"""
        self._write_json(self.chats_file, [])
        self._write_json(self.emotions_file, [])
