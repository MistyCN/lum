# 知微光年 **Luminest**

一个基于AI的智能语音对话系统，集成了语音识别、自然语言处理、危险信号检测和Web管理界面的完整解决方案。

## 🌟 项目特色

- **多模态交互**: 支持语音输入输出和文本聊天
- **智能对话**: 基于`Coze`平台的AI聊天服务
- **危险检测**: 实时监测对话中的危险信号并进行分析
- **Web管理**: 提供完整的Web界面进行管理和监控
- **语音处理**: 集成百度AI的语音识别和合成服务

## 🚀 快速开始

### 环境要求

- Python 3.7+
- Windows/Linux/macOS

### 安装依赖

```bash
pip install -r requirements.txt
```

### 环境配置

在项目根目录创建 `.env` 文件，配置以下API密钥：

```env
# Coze平台配置
COZE_API_TOKEN=your_coze_api_token

# DeepSeek API配置  
DEEP_SEEK_API_KEY=your_deepseek_api_key

# 百度AI配置
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
├── src/                          # 源代码目录
│   ├── main.py                   # CLI主程序
│   ├── webApp.py                 # Web应用
│   ├── config.py                 # 配置管理
│   ├── services/                 # 服务模块
│   │   ├── analysisService.py    # 危险分析服务
│   │   ├── baiduAudioService.py  # 百度语音服务
│   │   ├── coze_chat_service.py  # Coze聊天服务
│   │   ├── signalService.py      # 信号处理服务
│   │   └── ...
│   ├── templates/                # HTML模板
│   │   ├── admin.html            # 管理界面
│   │   ├── chat.html             # 聊天界面
│   │   ├── client_chat.html      # 客户端聊天
│   │   ├── danger_signals.html   # 危险信号监控
│   │   └── ...
│   └── static/                   # 静态资源
├── runCli.py                     # CLI启动脚本
├── runWeb.py                     # Web启动脚本
├── requirements.txt              # 依赖列表
├── .env                          # 环境变量配置
└── README.md                     # 项目文档
```

## 🔧 核心功能

### 1. 智能对话系统

- 基于`Coze`平台的AI聊天服务
- 支持多轮对话和上下文理解
- 自动保存和管理聊天历史

### 2. 语音处理

- **语音识别**: 使用百度AI将语音转换为文字
- **语音合成**: 将AI回复转换为语音输出
- **实时播放**: 支持音频录制和播放功能

### 3. 危险信号检测

- 实时监测对话内容中的危险信息
- 使用`DeepSeek` API进行深度分析
- 自动记录和存储危险信号数据

### 4. Web管理界面

- **管理后台**: 完整的系统管理功能
- **实时聊天**: Web端聊天界面
- **信号监控**: 危险信号实时监控和分析
- **用户操作**: 用户管理和操作记录

## 🛠 技术栈

### 后端技术

- **Python**: 主要开发语言
- **Flask**: Web框架
- **`Coze` API**: AI聊天服务
- **`DeepSeek` API**: 内容分析服务
- **百度AI**: 语音识别和合成

### 前端技术

- **HTML5/CSS3**: 页面结构和样式
- **JavaScript**: 交互逻辑
- **Bootstrap**: UI框架

### 音频处理

- **`PyAudio`**: 音频录制
- **`Pygame`**: 音频播放
- **`NumPy`**: 音频数据处理

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
   - **聊天**: 进行文本或语音对话
   - **管理**: 查看系统状态和设置
   - **监控**: 查看危险信号和分析结果

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

