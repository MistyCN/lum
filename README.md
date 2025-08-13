# 知微光年 **Luminest**

一个基于AI的智能语音对话系统，集成了语音识别、自然语言处理、危险信号检测和Web管理界面的完整解决方案。

## 🌟 项目特色

- **多模态交互**: 支持语音输入输出和文本聊天
- **智能对话**: 基于`Coze`平台的AI聊天服务，支持流式响应
- **情感分析**: 基于DeepFace的实时面部表情识别与抑郁检测
- **危险检测**: 实时监测对话中的危险信号并进行心理学专业分析
- **Web管理**: 提供完整的Web界面进行管理和监控
- **语音处理**: 集成百度AI的语音识别和合成服务
- **用户画像**: 智能分析用户偏好和性格特征

## 🚀 快速开始

### 环境要求

- Python 3.7+
- Windows/Linux/macOS
- 摄像头设备（用于情感分析功能）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 环境配置

在项目根目录创建 `.env` 文件，配置以下API密钥：

```env
# Coze平台配置（用于AI聊天）
COZE_API_TOKEN=your_coze_api_token

# DeepSeek API配置（用于心理分析）  
DEEP_SEEK_API_KEY=your_deepseek_api_key

# 百度AI配置（用于语音处理）
baidu_appid=your_baidu_appid
baidu_api_key=your_baidu_api_key
baidu_secret_key=your_baidu_secret_key
```

### 运行方式

#### 1. 命令行模式

```bash
python runCli.py
```

启动CLI版本，支持语音对话交互。

#### 2. Web应用模式

```bash
python runWeb.py
```

启动Web服务器，访问 `http://localhost:5000` 使用Web界面。

## 📁 项目结构

```
lum/
├── src/                              # 源代码目录
│   ├── main.py                       # CLI主程序
│   ├── webApp.py                     # Web应用主文件
│   ├── config.py                     # 配置管理
│   ├── services/                     # 服务模块
│   │   ├── analysisService.py        # DeepSeek危险分析服务
│   │   ├── baiduAudioService.py      # 百度语音服务
│   │   ├── coze_chat_service.py      # Coze聊天服务
│   │   ├── deepfaceEmotionService.py # DeepFace情感分析服务
│   │   ├── signalService.py          # 信号处理服务
│   │   ├── model_manager.py          # AI模型管理
│   │   └── base*.py                  # 基础服务类
│   ├── templates/                    # HTML模板
│   │   ├── admin.html                # 系统管理界面
│   │   ├── chat.html                 # 基础聊天界面
│   │   ├── client_chat.html          # 客户端聊天界面
│   │   ├── danger_signals.html       # 危险信号监控界面
│   │   ├── emotion_monitor.html      # 情感监控界面
│   │   └── user_operations.html      # 用户操作管理界面
│   └── static/css/                   # 静态样式文件
├── runCli.py                         # CLI启动脚本
├── runWeb.py                         # Web启动脚本
├── requirements.txt                  # Python依赖列表
├── .env                              # 环境变量配置文件
├── chat_history.json                 # 聊天历史记录
├── signals.json                      # 危险信号记录
└── README.md                         # 项目文档
```

## 🔧 核心功能

### 1. 智能对话系统

- **AI聊天**: 基于`Coze`平台的智能对话服务
- **流式响应**: 支持实时流式对话体验
- **上下文理解**: 多轮对话和上下文记忆
- **历史管理**: 自动保存和管理聊天记录

### 2. 语音处理模块

- **语音识别**: 使用百度AI将语音转换为文字
- **语音合成**: 将AI回复转换为自然语音输出
- **实时播放**: 支持音频录制、播放和格式转换
- **多格式支持**: WAV录制，MP3输出

### 3. 情感分析系统

- **面部识别**: 基于DeepFace的深度学习面部表情分析
- **情绪检测**: 识别愤怒、厌恶、恐惧、快乐、悲伤、惊讶、中性7种基本情绪
- **抑郁检测**: 智能判断用户是否呈现抑郁倾向特征
- **实时监控**: 支持摄像头实时捕获和图片上传分析
- **阈值配置**: 可配置的抑郁检测阈值和规则

### 4. 危险信号检测

- **内容监测**: 实时分析对话内容中的心理危机信号
- **专业分析**: 使用`DeepSeek` API结合心理学知识进行深度分析
- **自动记录**: 危险信号自动记录和分类存储
- **专业建议**: 为介入专业人士提供处理建议和总结

### 5. 用户画像分析

- **偏好分析**: 智能分析用户话题偏好和兴趣特点
- **性格识别**: 基于对话内容识别用户性格特征
- **行为模式**: 分析用户交互行为和习惯
- **数据持久化**: 分析结果自动保存为JSON格式

### 6. Web管理界面

- **系统管理**: 完整的后台管理功能(`/`)
- **实时聊天**: 多样化的Web端聊天界面(`/chat`, `/client_chat`)
- **信号监控**: 危险信号实时监控和历史查看(`/danger_signals`)
- **情感监控**: 表情分析和抑郁检测界面(`/emotion_monitor`)
- **用户管理**: 用户操作记录和管理(`/user_operations`)

## 🛠 技术栈

### 后端技术

- **Python**: 主要开发语言
- **Flask**: Web框架和RESTful API
- **`Coze` API**: AI聊天服务
- **`DeepSeek` API**: 心理危机分析服务
- **百度AI**: 语音识别和合成

### AI/ML技术

- **DeepFace**: 深度学习面部表情识别
- **OpenCV**: 计算机视觉和图像处理
- **TensorFlow/Keras**: 深度学习框架
- **NumPy**: 数据科学计算

### 前端技术

- **HTML5/CSS3**: 响应式页面结构和样式
- **JavaScript**: 交互逻辑和实时通信
- **Bootstrap**: 现代化UI框架
- **WebRTC**: 摄像头访问和媒体流处理

### 音频处理

- **`PyAudio`**: 实时音频录制
- **`Pygame`**: 音频播放和处理
- **`NumPy`**: 音频信号数据处理
- **百度AI SDK**: 语音识别和合成API

### 数据存储

- **JSON**: 结构化数据存储
- **文件系统**: 聊天历史和信号记录
- **环境变量**: 安全的配置管理

## 📱 使用指南

### CLI模式使用

1. 启动程序：`python runCli.py`
2. 看到提示后直接说话，系统会自动录音
3. 等待AI回复并播放语音
4. 输入 'Q' 退出程序

### Web模式使用

1. 启动服务：`python runWeb.py`
2. 浏览器访问：`http://localhost:5000`
3. 选择相应功能模块：
   - **系统管理** (`/`): 查看系统状态和后台管理
   - **智能聊天** (`/chat`, `/client_chat`): 进行文本对话和流式聊天
   - **危险监控** (`/danger_signals`): 查看危险信号和心理分析结果
   - **情感监控** (`/emotion_monitor`): 进行面部表情分析和抑郁检测
   - **用户管理** (`/user_operations`): 管理用户操作和偏好分析

### 情感分析功能使用

1. **图片上传分析**：
   - 访问情感监控页面
   - 上传包含人脸的图片
   - 查看详细的情绪分析结果

2. **实时摄像头分析**：
   - 点击"摄像头分析"按钮
   - 允许浏览器访问摄像头
   - 系统自动捕获并分析表情

3. **抑郁检测**：
   - 系统自动评估是否存在抑郁倾向
   - 超过阈值时会记录到危险信号中

## 🔍 API接口

### 聊天接口

```
POST /api/chat
Content-Type: application/json

{
    "message": "用户消息",
    "user_id": "用户ID"
}
```

### 信号获取接口

```
GET /api/signals
```

### 流式聊天接口

```
POST /api/stream_chat
Content-Type: application/json

{
    "message": "用户消息"
}
```

## ⚙️ 配置说明

### 聊天服务配置

- `max_history_length`: 最大历史记录长度（默认50）
- `coze_cn_base_url`: `Coze`服务基础URL

### 音频配置

- 录音格式：WAV
- 输出格式：MP3
- 采样率：16000Hz

## 🔒 安全特性

- **危险内容检测**: 实时监控对话内容
- **API密钥保护**: 使用环境变量管理敏感信息
- **数据隔离**: 不同用户数据独立存储

## 🐛 故障排除

### 常见问题

1. **音频设备问题**
   - 确保麦克风和扬声器正常工作
   - 检查音频设备权限设置

2. **API连接问题**
   - 验证API密钥配置正确
   - 检查网络连接状态

3. **依赖安装问题**
   - 使用Python 3.7+版本
   - 确保所有依赖正确安装

## 📄 许可证

本项目使用 [LICENSE](LICENSE) 许可证。

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目。

## 📞 联系我们

如有问题或建议，请通过以下方式联系：

- 提交Issue到项目仓库
- 发送邮件到项目维护者

## 🔗 相关链接

- 项目Blog: http://luminest.mistycn.top

---

**知微光年 Luminest**🌟

