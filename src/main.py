"""
Luminest CLI 主程序
"""

from src.services.coze_chat_service import CozeChatService
from src.services.signalService import SignalService
from src.services.analysisService import DeepseekAnalysisService
from src.services.baiduAudioService import BaiduAudioService
from src.services.deepfaceEmotionService import DeepfaceEmotionService
import json
import os

class LuminestCLI:
    """Luminest命令行界面类"""
    
    def __init__(self):
        self.chat_service = CozeChatService()
        self.signal_service = SignalService()
        self.analysis_service = DeepseekAnalysisService()
        self.audio_service = BaiduAudioService()
        self.emotion_service = DeepfaceEmotionService()
        self.running = True
        
    def run(self):
        """运行CLI程序"""
        print("====知微光年 Luminest v1.21====")
        print("输入'Q'退出程序")
        
        while self.running:
            user_input = input("\n欢迎使用>>")
            
            if user_input.upper() == 'Q':
                self.running = False
                continue
                
            self._process_input()
            
    def _process_input(self):
        """处理用户输入"""
        # 录音
        self.audio_service.record_audio("record.wav")
        
        # 语音转文字
        text = self.audio_service.speech_to_text("record.wav")
        print("<<", text)
        
        # 分析情感
        result = self.emotion_service.capture_and_analyze()
        depressed_data = self.emotion_service.is_depressed(result)
            # 仅当 depressed_data 为 dict 且非空时才调用 add_emotion_signal
        if isinstance(depressed_data, bool) and depressed_data:
            self.signal_service.add_emotion_signal(result)
        
        # 处理消息
        result = json.loads(self.chat_service.processMessage(text))
        
        # 检查是否需要危险处理
        if result["type"] == "dangerous":
            print("检测到危险信息,开始危险处理")
            history = self.chat_service.getChatHistory()
            analysis = self.analysis_service.analyze_danger(history)
            self.signal_service.add_dangerous_chat("测试ID", text, analysis)
            
        # 文字转语音并播放（使用临时文件避免文件锁）
        self.audio_service.text_to_speech(result["message"])
        print(">>", result["message"])
        # 尝试使用上一次生成的临时文件播放
        audio_file = getattr(self.audio_service, '_last_tts_file', None)
        if audio_file and os.path.exists(audio_file):
            self.audio_service.play_audio(audio_file)
        else:
            # 兼容回退：尝试播放默认文件名
            try:
                self.audio_service.play_audio('output.mp3')
            except Exception:
                pass

def main():
    """主程序入口"""
    cli = LuminestCLI()
    cli.run()
    
if __name__ == "__main__":
    main()
