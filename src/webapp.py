from flask import Flask, render_template, request, jsonify, Response
from src.services.coze_chat_service import CozeChatService
from src.services.signalService import SignalService
from src.services.analysisService import DeepseekAnalysisService
from src.services.deepfaceEmotionService import DeepfaceEmotionService
from src.services.baiduAudioService import BaiduAudioService
import subprocess
import tempfile
import shutil
import socket
import json
import os
import sys
import re
from src.generate_cert import generate_self_signed_cert

class WebApp:
    """Luminest Web应用"""
    
    def __init__(self):
        """初始化Web应用"""
        self.app = Flask(__name__)
        self.chatService = CozeChatService()
        # 用于后端语音识别（浏览器上传音频后调用）
        try:
            self.audioService = BaiduAudioService()
        except Exception:
            self.audioService = None
        self.signalService = SignalService()
        self.analysisService = DeepseekAnalysisService()
        self.emotionService = DeepfaceEmotionService()
        self.preferences = {}
        self._setupRoutes()
        try:
            self.cert_file, self.key_file = generate_self_signed_cert()
            print(f"使用证书文件: {self.cert_file}")
            print(f"使用私钥文件: {self.key_file}")
            # 启动HTTPS服务器
            print(f"启动HTTPS服务器")
            print("注意: 首次访问时浏览器可能会显示安全警告，请点击'高级'并'继续访问'")
        except ImportError:
            print("错误: 需要安装pyOpenSSL库以支持HTTPS")
            print("请运行: pip install pyOpenSSL")
            sys.exit(1)
        except Exception as e:
            print(f"启动HTTPS服务器失败: {str(e)}")
            sys.exit(1)
        
    def _setupRoutes(self):
        """设置路由"""
        # 页面路由
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/dashboard', 'dashboard', self.dashboard)
        self.app.add_url_rule('/assessment', 'assessment', self.assessment)
        self.app.add_url_rule('/danger_signals', 'dangerSignals', self.dangerSignals)
        self.app.add_url_rule('/chat', 'chatPage', self.chatPage)
        self.app.add_url_rule('/stream_page', 'streamPage', self.streamPage)
        self.app.add_url_rule('/user_operations', 'userOperations', self.userOperations)
        self.app.add_url_rule('/client_chat', 'clientChat', self.clientChat)
        self.app.add_url_rule('/emotion_monitor', 'emotionMonitor', self.emotionMonitor)

        
        # API路由
        self.app.add_url_rule('/api/receive', 'receiveData', self.receiveData, methods=['POST'])
        self.app.add_url_rule('/api/signals', 'getSignals', self.getSignals, methods=['GET'])
        self.app.add_url_rule('/api/chat', 'chatApi', self.chatApi, methods=['POST'])
        self.app.add_url_rule('/api/stream_chat', 'streamChatApi', self.streamChatApi, methods=['POST'])
        self.app.add_url_rule('/api/voice_to_text', 'voiceToText', self.voice_to_text, methods=['POST'])
        self.app.add_url_rule('/api/tts', 'tts', self.tts, methods=['POST'])
        self.app.add_url_rule('/api/stream_action', 'streamAction', self.stream_action, methods=['POST'])
        self.app.add_url_rule('/favicon.ico', 'favicon', self.favicon, methods=['GET'])
        self.app.add_url_rule('/api/save_history', 'saveChatHistory', self.saveChatHistory, methods=['GET'])
        self.app.add_url_rule('/api/del_history', 'delHistory', self.delHistory, methods=['GET'])
        self.app.add_url_rule('/api/analyze', 'analyzePreferences', self.analyzePreferences, methods=['GET'])
        self.app.add_url_rule('/api/analyze_emotion', 'analyzeEmotion', self.analyzeEmotion, methods=['POST'])
        self.app.add_url_rule('/api/capture_emotion', 'captureEmotion', self.captureEmotion, methods=['POST'])
        self.app.add_url_rule('/api/chat_history', 'getChatHistory', self.getChatHistory, methods=['GET'])
        self.app.add_url_rule('/api/emotions', 'getEmotions', self.getEmotions, methods=['GET'])
        self.app.add_url_rule('/api/ai_danger_keywords', 'aiDangerKeywords', self.ai_danger_keywords, methods=['POST'])
        self.app.add_url_rule('/api/ai_crisis_index', 'aiCrisisIndex', self.ai_crisis_index, methods=['POST'])
        self.app.add_url_rule('/api/clear_chats', 'clearChats', self.clear_chats, methods=['POST'])
        self.app.add_url_rule('/api/clear_emotions', 'clearEmotions', self.clear_emotions, methods=['POST'])
        self.app.add_url_rule('/api/clear_signals', 'clearSignals', self.clear_signals, methods=['POST'])
        self.app.add_url_rule('/api/clear_preferences', 'clearPreferences', self.clear_preferences, methods=['POST'])


    def getChatHistory(self):
        """返回所有聊天记录（用于综合评估页面统计）"""
        try:
            if self.chatService.data_service is not None:
                chats = self.chatService.data_service.get_chats()
                return jsonify(chats)
            else:
                print("chatService.data_service 未初始化")
                return jsonify([])
        except Exception as e:
            print(f"获取聊天记录时出错: {str(e)}")
            return jsonify([])

    def getEmotions(self):
        """返回所有表情识别记录（用于综合评估页面统计）"""
        try:
            if self.emotionService.data_service is not None:
                emotions = self.emotionService.data_service.get_emotions()
                return jsonify(emotions)
            else:
                print("emotionService.data_service 未初始化")
                return jsonify([])
        except Exception as e:
            print(f"获取表情记录时出错: {str(e)}")
            return jsonify([])
        
    def ai_danger_keywords(self):
        """AI分析用户危机关键词，POST传入聊天历史"""
        try:
            data = request.get_json()
            history = data.get('history', []) if data else []
            keywords = self.analysisService.analyze_danger_keywords(history)
            return jsonify({'keywords': keywords})
        except Exception as e:
            print(f"AI危机关键词分析失败: {str(e)}")
            return jsonify({'keywords': ''})

    def ai_crisis_index(self):
        """AI综合分析生成心理危机指数并返回结构化结果"""
        try:
            data = request.get_json()
            history = data.get('history', []) if data else []
            emotions = data.get('emotions', []) if data else []
            result = self.analysisService.analyze_crisis_index(history, emotions)
            return jsonify(result)
        except Exception as e:
            print(f"AI危机指数分析失败: {str(e)}")
            return jsonify({"score":0, "interpretation":"分析失败","features":[],"explanation":"","suggestions":"","validation":""})
        
    # 页面路由处理
    def index(self):
        return render_template('admin.html')
        
    def dashboard(self):
        return render_template('admin.html')
        
    def dangerSignals(self):
        return render_template('danger_signals.html')
    
    def assessment(self):
        """综合评估页面"""
        return render_template('assessment.html')
    
    def chatPage(self):
        return render_template('chat.html')
        
    def userOperations(self):
        return render_template('user_operations.html')
        
    def clientChat(self):
        return render_template('client_chat.html')
        
    def emotionMonitor(self):
        """表情监控页面"""
        return render_template('emotion_monitor.html')

    def streamPage(self):
        """流式交互页面（带语音输入）"""
        return render_template('stream_chat.html')

    def voice_to_text(self):
        """接收浏览器上传的音频文件并返回识别文本"""
        try:
            if 'audio' not in request.files:
                return jsonify({'error': '没有收到音频文件'}), 400
            audio = request.files['audio']
            # 保存到唯一临时文件，避免并发覆盖
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio.filename or '')[1] or '.tmp') as tf:
                tmp_input = tf.name
                audio.save(tmp_input)

            # 检查文件头是否是 RIFF/WAVE
            is_riff = False
            try:
                with open(tmp_input, 'rb') as f:
                    header = f.read(12)
                    if len(header) >= 12 and header[0:4] == b'RIFF' and header[8:12] == b'WAVE':
                        is_riff = True
            except Exception:
                is_riff = False

            wav_path = None
            try:
                # 如果不是 RIFF/WAVE，尝试用 ffmpeg 转换（如果可用）
                if not is_riff:
                    ffmpeg_path = shutil.which('ffmpeg')
                    if ffmpeg_path:
                        wav_fd, wav_path = tempfile.mkstemp(suffix='.wav')
                        os.close(wav_fd)
                        cmd = [ffmpeg_path, '-y', '-i', tmp_input, '-ar', '16000', '-ac', '1', '-f', 'wav', wav_path]
                        try:
                            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
                            is_riff = True
                        except subprocess.CalledProcessError as e:
                            print(f"ffmpeg 转码失败: {e.output.decode(errors='replace')}")
                            # 保留 is_riff=False，以便后续给出友好提示
                    else:
                        print('系统中未找到 ffmpeg，可选项：安装 ffmpeg 或在前端导出 WAV')

                # 选择要传给 ASR 的路径
                asr_input = wav_path if wav_path and os.path.exists(wav_path) else tmp_input

                if self.audioService is None:
                    return jsonify({'text': ''})

                if not is_riff:
                    # 返回清晰的错误，提示用户或管理员安装 ffmpeg 或使用前端 WAV 导出
                    try:
                        os.remove(tmp_input)
                    except Exception:
                        pass
                    if wav_path and os.path.exists(wav_path):
                        try:
                            os.remove(wav_path)
                        except Exception:
                            pass
                    return jsonify({'error': '上传的音频格式不是标准 WAV (RIFF)。请安装 ffmpeg 以启用服务器端转码，或在浏览器端导出 16kHz 单声道 WAV 后重试。'}), 400

                # 调用 ASR
                text = self.audioService.speech_to_text(asr_input)
                return jsonify({'text': text}), 200
            finally:
                # 清理临时文件
                try:
                    if os.path.exists(tmp_input):
                        os.remove(tmp_input)
                except Exception:
                    pass
                try:
                    if wav_path and os.path.exists(wav_path):
                        os.remove(wav_path)
                except Exception:
                    pass
        except Exception as e:
            print(f"voice_to_text 错误: {str(e)}")
            return jsonify({'error': '识别失败'}), 500

    def tts(self):
        """生成 TTS 并返回音频二进制（MP3）"""
        try:
            data = request.get_json() or {}
            text = data.get('text', '')
            if not text:
                return jsonify({'error': '没有提供要合成的文本'}), 400
            if self.audioService is None:
                return jsonify({'error': '服务器未配置语音合成服务'}), 500

            # 调用合成（会把文件写入临时文件并记录到 _last_tts_file）
            try:
                self.audioService.text_to_speech(text)
            except Exception as e:
                print(f"TTS 合成失败: {e}")
                return jsonify({'error': 'TTS 合成失败'}), 500

            audio_file = getattr(self.audioService, '_last_tts_file', None)
            if not audio_file or not os.path.exists(audio_file):
                return jsonify({'error': '未能生成语音文件'}), 500

            # 以二进制读入内存并删除临时文件
            try:
                with open(audio_file, 'rb') as f:
                    content = f.read()
            except Exception as e:
                print(f"读取 TTS 临时文件失败: {e}")
                return jsonify({'error': '读取 TTS 文件失败'}), 500
            finally:
                try:
                    os.remove(audio_file)
                except Exception:
                    pass

            return Response(content, mimetype='audio/mpeg')
        except Exception as e:
            print(f"TTS 接口错误: {e}")
            return jsonify({'error': 'TTS 服务内部错误'}), 500

#危险数据接收与处理
    # API路由处理
    def receiveData(self):
        """处理接收到的危险数据"""
        data = request.json
        if data is None or not isinstance(data, dict):
            return jsonify({"status": "error", "message": "无效的数据"}), 400
        self.signalService.add_signal(data)
        return jsonify({"status": "success"})

    def favicon(self):
            """返回一个内联 SVG 作为 favicon，避免静态文件缺失导致的 404 日志"""
            svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
<defs>
    <linearGradient id="g1" x1="0" x2="1">
        <stop offset="0%" stop-color="#34d399" />
        <stop offset="100%" stop-color="#06b6d4" />
    </linearGradient>
</defs>
<rect width="48" height="48" rx="8" fill="url(#g1)" />
<path d="M14 8 L28 8 L31 18 L22 34 L14 18 Z" fill="#ffffff" opacity="0.98"/>
</svg>'''
            return Response(svg, mimetype='image/svg+xml')

    def stream_action(self):
        """前端在流式页面点击后调用，后端可做简单记录或保存动作，然后前端会跳转到主页"""
        try:
            data = request.get_json() or {}
            # 记录动作到日志（可扩展为持久化）
            print(f"stream_action invoked, payload: {data}")
            # 可在这里做额外处理：如保存当前会话快照、触发持久化等
            try:
                self.chatService.saveChatHistory()
            except Exception:
                # 保存失败不要中止流程，仍然返回成功以便前端跳转
                print('警告: 保存聊天记录失败（stream_action）')
            return jsonify({'status': 'success', 'message': '已处理，正在返回主页'}), 200
        except Exception as e:
            print(f'stream_action 处理失败: {e}')
            return jsonify({'status': 'error', 'message': '操作失败'}), 500
        
    def getSignals(self):
        """获取所有危险信号"""
        return jsonify(self.signalService.get_signals())
        
    def chatApi(self):
        """处理聊天请求"""
        data = request.json
        userMessage = data.get('message') if data else None
        if not userMessage:
            return jsonify({'response': "请输入有效的信息。"})
            
        try:
            result = self.chatService.processMessage(userMessage)
            # 解析 AI 返回内容：优先当作 JSON 解析，若失败则当作普通文本
            try:
                resultDict = json.loads(result)
            except json.JSONDecodeError:
                # 尝试对可能包含原始换行符的 JSON 做安全转义再解析
                try:
                    sanitized = result.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                    resultDict = json.loads(sanitized)
                except Exception:
                    # 退回为普通文本响应
                    resultDict = {'type': 'text', 'message': result}

            if resultDict.get('type') == 'dangerous':
                history = self.chatService.getChatHistory()
                # 将历史按可用字段格式化为字符串（兼容 message/content）
                historyStr = "\n".join([
                    f"{msg.get('role')}:{msg.get('message') or msg.get('content', '')}"
                    for msg in history
                ])
                analysis = self.analysisService.analyze_danger(history)
                self.signalService.add_dangerous_chat("测试ID", userMessage, analysis)
            return jsonify({'response': resultDict.get('message', str(result))})
        except Exception as e:
            print(f"Error in chat API: {str(e)}")
            return jsonify({'response': "抱歉，处理您的消息时出现错误，请稍后重试。"})

    def streamChatApi(self):
        """处理流式聊天请求"""
        data = request.json
        userMessage = data.get('message') if data else None
        if not userMessage:
            return jsonify({'response': "请输入有效的信息。"})
        
        def generate():
            try:
                history = self.chatService.getChatHistory()
                historyStr = "\n".join([f"{msg.get('role')}:{msg.get('message') or msg.get('content','')}" for msg in history])
                dangerous_handled = False
                assistant_accum = ''
                for chunk in self.chatService.processStreamMessage(userMessage):
                    try:
                        # Normalize chunk to dict
                        try:
                            jsonData = chunk if isinstance(chunk, dict) else json.loads(chunk)
                        except Exception:
                            # not a JSON chunk
                            jsonData = {'message': str(chunk)}
                        # Extract the message text
                        raw_msg = jsonData.get('message') if isinstance(jsonData, dict) else str(jsonData)
                        out_text = ''
                        # 先尝试识别 ```json ... ``` 或 ``` ... ``` 中的 JSON
                        if isinstance(raw_msg, str):
                            s = raw_msg.strip()
                            m = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", s, re.IGNORECASE)
                            if not m:
                                m = re.search(r"```\s*(\{[\s\S]*?\})\s*```", s)
                            # 如果没找到 code-fence 包裹的 JSON，尝试文本中第一个 JSON 对象
                            if not m:
                                m = re.search(r"(\{[\s\S]*?\})", s)

                            if m:
                                json_text = m.group(1)
                                try:
                                    inner = json.loads(json_text)
                                    if isinstance(inner, dict):
                                        # 如果内部标注为危险，触发一次性处理（避免重复）
                                        if not dangerous_handled and inner.get('type') == 'dangerous':
                                            try:
                                                latest_history = self.chatService.getChatHistory()
                                                analysis = self.analysisService.analyze_danger(latest_history)
                                                self.signalService.add_dangerous_chat("测试ID", userMessage, analysis)
                                            except Exception as e:
                                                print(f"添加危险聊天信号失败: {e}")
                                            dangerous_handled = True
                                        out_text = inner.get('message', s)
                                    else:
                                        out_text = s
                                except Exception:
                                    out_text = s
                            else:
                                out_text = s
                        else:
                            out_text = str(raw_msg)

                        assistant_accum += out_text

                        # 如果 jsonData 指示了类型（例如服务端产生 dict 且 type 字段存在），也单独处理
                        if not dangerous_handled and isinstance(jsonData, dict) and jsonData.get('type') == 'dangerous':
                            try:
                                latest_history = self.chatService.getChatHistory()
                                analysis = self.analysisService.analyze_danger(latest_history)
                                self.signalService.add_dangerous_chat("测试ID", userMessage, analysis)
                            except Exception as e:
                                print(f"添加危险聊天信号失败: {e}")
                            dangerous_handled = True

                        yield f"data: {json.dumps({'chunk': out_text})}\n\n"
                    except Exception as e:
                        print(f"Error processing chunk: {str(e)}")
                        continue

                # 流结束后，若尚未处理到危险类型，尝试解析完整回复并处理
                if not dangerous_handled and assistant_accum:
                    try:
                        s = assistant_accum.strip()
                        if s.startswith('{') and s.endswith('}'):
                            inner = json.loads(s)
                            if isinstance(inner, dict) and inner.get('type') == 'dangerous':
                                try:
                                    latest_history = self.chatService.getChatHistory()
                                    analysis = self.analysisService.analyze_danger(latest_history)
                                    self.signalService.add_dangerous_chat("测试ID", userMessage, analysis)
                                except Exception as e:
                                    print(f"添加危险聊天信号失败(流结束后): {e}")
                    except Exception:
                        pass
                        
            except Exception as e:
                # 识别常见的权限/认证/网络错误并返回更友好的信息
                err_str = str(e)
                print(f"Error in stream chat API: {err_str}")
                friendly = '抱歉，处理您的消息时出现错误，请稍后重试。'
                # Coze 认证错误通常包含 code=4101 或提示 token 错误
                if '4101' in err_str or 'token' in err_str.lower() or 'authentication' in err_str.lower():
                    friendly = '后端 AI 服务认证失败：请检查 Coze/AI 服务的 API Token 配置（code 4101）。'
                # DNS/网络解析错误（Windows 常见 errno 11001）
                elif isinstance(e, socket.gaierror) or 'getaddrinfo' in err_str or '11001' in err_str:
                    friendly = '网络错误：无法解析或连接到后端 AI 服务主机。请检查服务器网络、DNS 或代理设置（getaddrinfo 失败）。'
                yield f"data: {json.dumps({'error': friendly})}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')

    def saveChatHistory(self):
        """保存历史记录到文件"""
        try:
            self.chatService.saveChatHistory()
            self.signalService.save_signals()
            return jsonify({'status': 'success', 'message': '聊天记录已保存'}), 200
        except Exception as e:
            print(f'保存聊天记录时出错: {str(e)}')
            return jsonify({'status': 'error', 'message': '保存聊天记录时出错，请稍后重试'}), 500
    
    def delHistory(self):
        """删除历史记录"""
        try:
            self.chatService.deleteChatHistory()
            return jsonify({'status': 'success', 'message': '已经删了'}), 200
        except Exception as e:
            print(f'删除聊天记录时出错: {str(e)}')
            return jsonify({'status': 'error', 'message': '删除聊天记录时出错，请稍后重试'}), 500

    def clear_chats(self):
        """API: 清空聊天记录（并持久化）"""
        try:
            self.chatService.deleteChatHistory()
            return jsonify({'status': 'success', 'message': '聊天记录已清空'}), 200
        except Exception as e:
            print(f'清空聊天记录时出错: {str(e)}')
            return jsonify({'status': 'error', 'message': '清空聊天记录失败'}), 500

    def clear_emotions(self):
        """API: 清空表情识别记录文件"""
        try:
            if self.emotionService.data_service is not None:
                self.emotionService.data_service._write_json(self.emotionService.data_service.emotions_file, [])
                return jsonify({'status': 'success', 'message': '表情识别记录已清空'}), 200
            else:
                return jsonify({'status': 'error', 'message': 'emotion data service 未初始化'}), 500
        except Exception as e:
            print(f'清空表情记录时出错: {str(e)}')
            return jsonify({'status': 'error', 'message': '清空表情记录失败'}), 500

    def clear_signals(self):
        """API: 清空危机信号"""
        try:
            self.signalService.clear_signals()
            try:
                self.signalService.save_signals()
            except Exception:
                pass
            return jsonify({'status': 'success', 'message': '危机信号已清空'}), 200
        except Exception as e:
            print(f'清空危机信号时出错: {str(e)}')
            return jsonify({'status': 'error', 'message': '清空危机信号失败'}), 500

    def clear_preferences(self):
        """API: 清空用户喜好（删除 preference.json）"""
        try:
            pref_file = 'preference.json'
            if os.path.exists(pref_file):
                try:
                    os.remove(pref_file)
                except Exception:
                    # 退回为写入空对象
                    with open(pref_file, 'w', encoding='utf-8') as f:
                        json.dump({}, f, ensure_ascii=False, indent=4)
            self.preferences = {}
            return jsonify({'status': 'success', 'message': '用户喜好已清空'}), 200
        except Exception as e:
            print(f'清空用户喜好时出错: {str(e)}')
            return jsonify({'status': 'error', 'message': '清空用户喜好失败'}), 500
            
    def analyzePreferences(self):
        """分析用户喜好"""
        try:
            history = self.chatService.getChatHistory()
            historyStr = "\n".join([f"{msg['role']}:{msg['content']}" for msg in history])
            result = self.analysisService.analyze_preferences(history)
            with open('preference.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
                
            return jsonify({'status': 'success', 'message': '已经分析完毕并保存到文件'}), 200
        except Exception as e:
            print(f'分析用户喜好时出错: {str(e)}')
            return jsonify({'status': 'error', 'message': '分析用户喜好时出错，请稍后重试'}), 500
            
    def analyzeEmotion(self):
        """分析上传的图片中的表情"""
        try:
            if 'image' not in request.files:
                return jsonify({'error': '没有收到图片文件'}), 400
                
            image = request.files['image']
            image_path = "temp_emotion.jpg"
            image.save(image_path)
            result = self.emotionService.analyze_emotion(image_path)
            depressed_data = self.emotionService.is_depressed(result)
            if isinstance(depressed_data, bool) and depressed_data:
                self.signalService.add_emotion_signal(result, )
                
            return jsonify({
                'status': 'success',
                'result': result,
                'is_depressed': depressed_data
            }), 200
            
        except Exception as e:
            print(f'分析表情时出错: {str(e)}')
            return jsonify({'status': 'error', 'message': '分析表情时出错，请稍后重试'}), 500
            
    def captureEmotion(self):
        """从摄像头捕获并分析表情"""
        try:
            result = self.emotionService.capture_and_analyze()
            depressed_data = self.emotionService.is_depressed(result)
            # 仅当 depressed_data 为 dict 且非空时才调用 add_emotion_signal
            if isinstance(depressed_data, bool) and depressed_data:
                self.signalService.add_emotion_signal(result)
                
            return jsonify({
                'status': 'success',
                'result': result,
                'is_depressed': depressed_data
            }), 200
            
        except Exception as e:
            print(f'捕获和分析表情时出错: {str(e)}')
            return jsonify({'status': 'error', 'message': '捕获和分析表情时出错，请稍后重试'}), 500
            
    def _loadPreferences(self):
        """加载用户喜好"""
        try:
            if os.path.exists('preference.json'):
                with open('preference.json', 'r', encoding='utf-8') as f:
                    self.preferences = json.load(f)
                    print("已载入喜好:", self.preferences)
            else:
                print("还没保存过喜好记录")
        except Exception as e:
            print(f"加载用户喜好时出错: {str(e)}")
            self.preferences = {}
            
    def _loadHistory(self):
        """加载聊天历史和信号"""
        self.chatService.loadChatHistory()
        self.signalService.load_signals()
        self._loadPreferences()
        if self.preferences:
            self.chatService.updateUserPreferences(self.preferences)
            
    def run(self, host='0.0.0.0', port=5000, debug=False, ssl_context=None):
        """运行Web应用"""
        ssl_context = (self.cert_file, self.key_file) if ssl_context is None else ssl_context
        self._loadHistory()
        print("Luminest 工作坊网页版启动")
        if ssl_context:
            print(f"HTTPS模式启动，访问地址: https://{host}:{port}")
            print("注意: 首次访问时浏览器可能会显示安全警告，请点击'高级'并'继续访问'")
        else:
            print(f"HTTP模式启动，访问地址: http://{host}:{port}")
            print("提示: 如果需要通过局域网IP访问摄像头功能，请使用HTTPS模式")
        self.app.run(host=host, port=port, debug=debug, ssl_context=ssl_context)


def create_app():
    """创建并配置Web应用"""
    webapp = WebApp()
    return webapp
    
    
if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=True)