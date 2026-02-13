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
# 知微光年 — Luminest

Luminest 是一个面向心理健康与智能对话的演示平台，集成语音、文本、表情识别与心理危机评估能力。项目包含：命令行（CLI）交互、基于 Flask 的 Web 管理界面、多模态数据持久化与 AI 驱动的分析服务。

本 README 以开发者/部署者角度说明如何配置、运行与扩展本项目。

---

## 目录速览（关键功能）

- 智能对话（Coze） — 文本 + 流式响应
- 语音：百度语音识别与合成（TTS/ASR）
- 表情识别：DeepFace 实时/图片情绪识别与抑郁判断
- 心理危机评估：AI 输出“心理危机指数（0-100）”、危机关键词与专家建议，并进行多模型交叉验证
- 危险信号记录与管理
- Web 可视化仪表盘（综合评估、表情专项评估、对话专项评估等）

---

## 快速开始（开发/测试）

环境：推荐 Python 3.8+，在 Windows / Linux / macOS 均可运行。

1) 安装依赖：

```powershell
python -m pip install -r requirements.txt
```

2) 配置 API Key（在项目根目录创建 `.env` 或直接在 `src/config.py` 设置）：

- Coze 平台: `cozeApiToken` 或环境变量 `COZE_API_TOKEN`
- DeepSeek/Deepseek-like 服务: `deepseekApiKey`
- 百度语音: `baiduAppid`, `baiduApiKey`, `baiduSecretKey`

（不要将密钥提交到代码库）

3) 运行 CLI：

```powershell
python runCli.py
```

4) 运行 Web：

```powershell
python runWeb.py
```

然后在浏览器打开 `http://localhost:5000`（或 `https://localhost:5000`，项目会尝试生成自签名证书以启用 HTTPS）。

---

## 主要模块与文件说明

- `src/main.py` — CLI 入口，支持录音、ASR、对话请求、情感分析、TTS 与播放。
- `src/webapp.py` — Flask 应用，路由与 REST API 注册点，渲染 `src/templates/*` 页面。
- `src/config.py` — 项目配置（API key、路径、阈值等）。
- `src/services/` — 各类服务实现：
  - `coze_chat_service.py`：Coze 聊天服务（流式/非流式）
  - `baiduAudioService.py`：百度语音（ASR/TTS），已使用临时文件避免播放/写文件冲突
  - `deepfaceEmotionService.py`：基于 DeepFace 的表情识别与抑郁判断
  - `analysisService.py`：AI 分析服务（包含 `analyze_danger`, `analyze_danger_keywords`, `analyze_crisis_index`）
  - `signalService.py`：危机信号记录、保存与加载
  - `dataService.py`：持久化聊天与表情记录（`data/chats.json`, `data/emotions.json`）
- `src/templates/` — Flask HTML 模板（`assessment.html` 已包含丰富可视化）
- `runCli.py`, `runWeb.py` — 启动脚本（CLI / Web）

---

## Web 界面（重要页面）

- `/` 或 `/dashboard` — 系统管理页（管理入口）
- `/assessment` — 综合评估（包含心理危机指数、表情专项评估、用户对话专项评估与可视化图表）
- `/chat` — 聊天页面（文本/流式）
- `/emotion_monitor` — 表情监控与图片/摄像头分析
- `/danger_signals` — 危险信号监控与处理

assessment 页面亮点：
- 实时柱状图/饼图显示对话、表情、危机信号分布（基于 ECharts）
- 表情专项评估：展示各类情绪出现次数及百分比，并支持详细表格
- 用户对话专项评估：展示对话总数、危机对话次数、危机出现率与 AI 推测的危机关键词
- 心理危机指数（独立板块）：AI 返回 `score(0-100)`、interpretation、features、explanation、suggestions 与 validation（交叉验证结果），以仪表盘与文本美化展示
- 页面底部提供：清除聊天/表情/信号/用户喜好按钮（调用后端 API，带确认提示）

---

## 后端 REST API（摘要）

常用接口：

- POST `/api/chat` — 发送聊天请求
- POST `/api/stream_chat` — 流式聊天
- GET `/api/chat_history` — 获取聊天记录（JSON）
- GET `/api/emotions` — 获取表情识别记录
- GET `/api/signals` — 获取危机信号
- POST `/api/ai_danger_keywords` — AI 推测危机关键词（输入历史）
- POST `/api/ai_crisis_index` — AI 生成心理危机指数（输入历史 + 表情记录）

管理/清理接口（assessment 页面按钮调用）：

- POST `/api/clear_chats` — 清空聊天记录
- POST `/api/clear_emotions` — 清空表情记录
- POST `/api/clear_signals` — 清空危机信号
- POST `/api/clear_preferences` — 清空用户喜好

（更多内部 API 可在 `src/webapp.py` 中查看）

---

## 设计注意点与已实现的安全/容错

- AI 调用具有可失败的网络/密钥依赖，后端对外部调用加入 try/except 并返回保底结构
- 对 AI 输出做了增强解析：会识别 code-fence 中的 JSON 或文本中的第一个 JSON 对象，以减少非结构化输出导致的 UI 问题
- TTS 写入使用临时文件并在播放结束后删除，避免 Windows 上文件被占用导致的 PermissionError
- 所有敏感信息（API Key）建议通过环境变量或 CI 密钥注入管理

---

## 开发者指南

- 运行单元/集成测试（若有）前请确认已安装依赖
- 修改前端模板：`src/templates/*.html`，样式在 `src/static/css/` 中
- 若需要模拟或替换 AI 服务，可在 `src/services/analysisService.py` 中替换 client 调用或注入 Mock

调试建议：

- 查看 Flask 控制台日志（`runWeb.py` 启动时）以追踪 API 调用与异常
- 运行 CLI 时留意控制台输出以调试音频与 AI 调用流程

---

## 常见问题与排查（简要）

- PermissionError 写入 `output.mp3`：已解决，TTS 会写入临时文件并使用该临时文件播放；确保系统允许 Python 读写临时目录
- AI 返回非 JSON：分析服务会尝试提取 JSON code-fence，若无法解析会返保底结构并把原始文本放入 `explanation` 供人工核查
- 摄像头无法使用：浏览器需要授予权限，且在 HTTPS 下更稳定（项目尝试生成自签名证书以启用 HTTPS）

---

## 贡献与许可证

欢迎提交 Issue / PR。请遵循代码风格并写明变更目的。项目使用仓库根目录的 `LICENSE`，请参阅该文件获取授权信息。

---

如果你希望，我可以继续：

- 把 README 中的 API 示例扩展为可复制的 curl/PowerShell 命令；
- 添加本地开发快速启动脚本（比如 `scripts/dev_start.bat` 或 `scripts/dev_start.sh`）；
- 或针对特定模块（如 TTS、DeepFace）撰写更详细的开发文档与调试步骤。

谢谢使用 Luminest，若要我把 README 的某部分另存为单独文档（例如 API 参考、部署说明），告诉我要拆哪一块。 


