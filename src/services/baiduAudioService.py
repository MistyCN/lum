import os
from typing import Optional
import wave
import pyaudio
import pygame
from aip import AipSpeech
import tempfile
import time
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
        """语音转文字

        增强逻辑：如果上传的是 WAV 文件，读取后确保为 16kHz、单声道、16-bit PCM，然后将原始 PCM bytes 发送给百度 ASR。
        这样能提升不同浏览器录音生成格式导致的识别不准确问题。
        """
        try:
            # 如果是 WAV 文件，进行必要的格式规范化
            if audio_file.lower().endswith('.wav'):
                import wave
                import audioop
                with wave.open(audio_file, 'rb') as wf:
                    nchannels = wf.getnchannels()
                    sampwidth = wf.getsampwidth()
                    framerate = wf.getframerate()
                    frames = wf.readframes(wf.getnframes())

                    data = frames
                    # 转为单声道
                    if nchannels > 1:
                        data = audioop.tomono(data, sampwidth, 1, 1)
                        sampwidth = sampwidth
                        nchannels = 1
                    # 转为 16-bit
                    if sampwidth != 2:
                        try:
                            data = audioop.lin2lin(data, sampwidth, 2)
                            sampwidth = 2
                        except Exception:
                            pass
                    # 采样率调整到 16000
                    if framerate != 16000:
                        try:
                            data, _ = audioop.ratecv(data, sampwidth, 1, framerate, 16000, None)
                        except Exception:
                            pass

                    result = self.client.asr(data, 'pcm', 16000, {
                        'dev_pid': 1537,
                    })
            else:
                # 其他文件类型，直接读取原始 bytes 交由百度处理（可能会失败）
                result = self.client.asr(self._get_file_content(audio_file), 'pcm', 16000, {
                    'dev_pid': 1537,
                })

            if isinstance(result, dict) and result.get('err_no') != 0:
                # 出错或无识别结果
                return ''
            return result["result"][0] if result.get("result") else ""
        except Exception as e:
            print(f"speech_to_text 处理音频失败: {e}")
            try:
                # 尝试作为原始读取回退
                result = self.client.asr(self._get_file_content(audio_file), 'pcm', 16000, {'dev_pid': 1537})
                return result["result"][0] if result.get("result") else ""
            except Exception as e2:
                print(f"speech_to_text 回退也失败: {e2}")
                return ""
        
    def text_to_speech(self, text: str, output_file: str = "output.mp3") -> None:
        """文字转语音"""
        result = self.client.synthesis(text, 'zh', 1, {
            'vol': 5,
            'per': 4,
            'spd': 5,
            'pit': 5,
            'aue': 3,
        })
        # 将合成音频写入临时文件以避免文件锁冲突
        if not isinstance(result, dict):
            if isinstance(result, bytes):
                # 使用临时文件，确保每次调用文件名唯一，避免被播放器锁定
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3', prefix='luminest_', dir=None)
                try:
                    tmp.write(result)
                    tmp.flush()
                    tmp.close()
                    # 记录最新生成的临时文件，供播放使用
                    self._last_tts_file = tmp.name
                    return None
                except Exception as e:
                    try:
                        tmp.close()
                    except Exception:
                        pass
                    print(f"写入临时音频文件失败: {e}")
                    return None
            else:
                print("语音合成失败，返回内容:", result)
                return None
                
    def play_audio(self, audio_file: str) -> None:
        """播放音频"""
        # 初始化并播放，然后等待播放结束再退出mixer，最后尝试删除临时文件
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            # 等待播放结束
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            print(f"播放音频出错: {e}")
        finally:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
            try:
                pygame.mixer.quit()
            except Exception:
                pass
            # 尝试删除文件（通常是临时文件）
            try:
                if audio_file and os.path.exists(audio_file):
                    os.remove(audio_file)
            except Exception:
                pass
        
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
