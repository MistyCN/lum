import os
import wave
import pyaudio
import pygame
from aip import AipSpeech
from src.services.baseAudioService import BaseAudioService
from src.config import Config

class BaiduAudioService(BaseAudioService):
    """百度语音服务实现"""
    
    def __init__(self):
        self.config = Config()
        self.client = AipSpeech(
            self.config.baiduAppid,
            self.config.baiduApiKey,
            self.config.baiduSecretKey
        )
        
    def _get_file_content(self, file_path: str) -> bytes:
        """获取文件内容"""
        with open(file_path, 'rb') as fp:
            return fp.read()
            
    def speech_to_text(self, audio_file: str) -> str:
        """语音转文字"""
        result = self.client.asr(self._get_file_content(audio_file), 'pcm', 16000, {
            'dev_pid': 1537,
        })
        return result["result"][0] if result.get("result") else ""
        
    def text_to_speech(self, text: str, output_file: str = "output.mp3") -> None:
        """文字转语音"""
        result = self.client.synthesis(text, 'zh', 1, {
            'vol': 5,
            'per': 4,
            'spd': 5,
            'pit': 5,
            'aue': 3,
        })
        
        if not isinstance(result, dict):
            with open(output_file, 'wb') as f:
                f.write(result)
                
    def play_audio(self, audio_file: str) -> None:
        """播放音频"""
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        
    def record_audio(self, output_file: str) -> None:
        """录制音频"""
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )
        
        print('开始录音...（按回车键停止）')
        frames = []
        
        while True:
            data = stream.read(1024)
            frames.append(data)
            
            if os.name == 'nt':
                import msvcrt
                if msvcrt.kbhit() and msvcrt.getch() == b'\r':
                    break
            else:
                import select
                import sys
                if select.select([sys.stdin], [], [], 0)[0] and sys.stdin.read(1) == '\n':
                    break
                    
        print('录音结束')
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        with wave.open(output_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)
            wf.writeframes(b''.join(frames))
