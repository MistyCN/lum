from abc import ABC, abstractmethod
from typing import List

class BaseAudioService(ABC):
    """音频服务基类"""
    
    @abstractmethod
    def speech_to_text(self, audio_file: str) -> str:
        """语音转文字"""
        pass
    
    @abstractmethod
    def text_to_speech(self, text: str, output_file: str) -> None:
        """文字转语音"""
        pass
    
    @abstractmethod
    def play_audio(self, audio_file: str) -> None:
        """播放音频"""
        pass
    
    @abstractmethod
    def record_audio(self, output_file: str) -> None:
        """录制音频"""
        pass
