from flask import Flask, render_template, request, jsonify, Response
from src.services.coze_chat_service import CozeChatService
from src.services.signalService import SignalService
from src.services.analysisService import DeepseekAnalysisService
from src.services.deepfaceEmotionService import DeepfaceEmotionService
import json
import os

class WebApp:
    """Luminest Web应用"""
    
    def __init__(self):
        """初始化Web应用"""
        self.app = Flask(__name__)
        self.chatService = CozeChatService()
        self.signalService = SignalService()
        self.analysisService = DeepseekAnalysisService()
        self.emotionService = DeepfaceEmotionService()
        self.preferences = {}
        self._setupRoutes()
        
    def _setupRoutes(self):
        """设置路由"""
        # 页面路由
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/dashboard', 'dashboard', self.dashboard)
        self.app.add_url_rule('/danger_signals', 'dangerSignals', self.dangerSignals)
        self.app.add_url_rule('/chat', 'chatPage', self.chatPage)
        self.app.add_url_rule('/user_operations', 'userOperations', self.userOperations)
        self.app.add_url_rule('/client_chat', 'clientChat', self.clientChat)
        self.app.add_url_rule('/emotion_monitor', 'emotionMonitor', self.emotionMonitor)
        
        # API路由
        self.app.add_url_rule('/api/receive', 'receiveData', self.receiveData, methods=['POST'])
        self.app.add_url_rule('/api/signals', 'getSignals', self.getSignals, methods=['GET'])
        self.app.add_url_rule('/api/chat', 'chatApi', self.chatApi, methods=['POST'])
        self.app.add_url_rule('/api/stream_chat', 'streamChatApi', self.streamChatApi, methods=['POST'])
        self.app.add_url_rule('/api/save_history', 'saveChatHistory', self.saveChatHistory, methods=['GET'])
        self.app.add_url_rule('/api/del_history', 'delHistory', self.delHistory, methods=['GET'])
        self.app.add_url_rule('/api/analyze', 'analyzePreferences', self.analyzePreferences, methods=['GET'])
        self.app.add_url_rule('/api/analyze_emotion', 'analyzeEmotion', self.analyzeEmotion, methods=['POST'])
        self.app.add_url_rule('/api/capture_emotion', 'captureEmotion', self.captureEmotion, methods=['POST'])
        
    # 页面路由处理
    def index(self):
        return render_template('admin.html')
        
    def dashboard(self):
        return render_template('admin.html')
        
    def dangerSignals(self):
        return render_template('danger_signals.html')
        
    def chatPage(self):
        return render_template('chat.html')
        
    def userOperations(self):
        return render_template('user_operations.html')
        
    def clientChat(self):
        return render_template('client_chat.html')
        
    def emotionMonitor(self):
        """表情监控页面"""
        return render_template('emotion_monitor.html')

#危险数据接收与处理
    # API路由处理
    def receiveData(self):
        """处理接收到的危险数据"""
        data = request.json
        self.signalService.add_signal(data)
        return jsonify({"status": "success"})
        
    def getSignals(self):
        """获取所有危险信号"""
        return jsonify(self.signalService.get_signals())
        
    def chatApi(self):
        """处理聊天请求"""
        data = request.json
        userMessage = data.get('message')
        if not userMessage:
            return jsonify({'response': "请输入有效的信息。"})
            
        try:
            result = self.chatService.processMessage(userMessage)
            resultDict = json.loads(result)
            
            if resultDict['type'] == 'dangerous':
                history = self.chatService.getChatHistory()
                historyStr = "\n".join([f"{msg['role']}:{msg['content']}" for msg in history])
                analysis = self.analysisService.analyze_danger(history)
                self.signalService.add_dangerous_chat("测试ID", userMessage, analysis)
            return jsonify({'response': resultDict['message']})
        except Exception as e:
            print(f"Error in chat API: {str(e)}")
            return jsonify({'response': "抱歉，处理您的消息时出现错误，请稍后重试。"})

    def streamChatApi(self):
        """处理流式聊天请求"""
        data = request.json
        userMessage = data.get('message')
        if not userMessage:
            return jsonify({'response': "请输入有效的信息。"})
        
        def generate():
            try:
                history = self.chatService.getChatHistory()
                historyStr = "\n".join([f"{msg['role']}:{msg['content']}" for msg in history])
                for chunk in self.chatService.processStreamMessage(userMessage):
                    try:
                        jsonData = chunk if isinstance(chunk, dict) else json.loads(chunk)
                        if jsonData.get('type') == 'dangerous':
                            analysis = self.analysisService.analyze_danger(history)
                            self.signalService.add_dangerous_chat("测试ID", userMessage, analysis)
                        if 'message' in jsonData:
                            yield f"data: {json.dumps({'chunk': jsonData['message']})}\n\n"
                        else:
                            yield f"data: {json.dumps({'chunk': str(chunk)})}\n\n"
                    except json.JSONDecodeError:
                        yield f"data: {json.dumps({'chunk': str(chunk)})}\n\n"
                    except Exception as e:
                        print(f"Error processing chunk: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"Error in stream chat API: {str(e)}")
                yield f"data: {json.dumps({'error': '抱歉，处理您的消息时出现错误，请稍后重试。'})}\n\n"
        
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
            if self.emotionService.is_depressed(result):
                self.signalService.add_emotion_signal(result)
                
            return jsonify({
                'status': 'success',
                'result': result,
                'is_depressed': self.emotionService.is_depressed(result)
            }), 200
            
        except Exception as e:
            print(f'分析表情时出错: {str(e)}')
            return jsonify({'status': 'error', 'message': '分析表情时出错，请稍后重试'}), 500
            
    def captureEmotion(self):
        """从摄像头捕获并分析表情"""
        try:
            result = self.emotionService.capture_and_analyze()
            if self.emotionService.is_depressed(result):
                self.signalService.add_emotion_signal(result)
                
            return jsonify({
                'status': 'success',
                'result': result,
                'is_depressed': self.emotionService.is_depressed(result)
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
            
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """运行Web应用"""
        self._loadHistory()
        print("Luminest 工作坊网页版启动")
        self.app.run(host=host, port=port, debug=debug)


def create_app():
    """创建并配置Web应用"""
    webapp = WebApp()
    return webapp
    
    
if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=True)