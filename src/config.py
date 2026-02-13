from typing import Dict
import os
from dotenv import load_dotenv

class Config:
    """配置管理类"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loadConfig()
        return cls._instance
    
    def _loadConfig(self):
        """加载环境变量和配置"""
        load_dotenv()
        
        # API Keys
        self.cozeApiToken = os.getenv("COZE_API_TOKEN")
        self.deepseekApiKey = os.getenv("DEEP_SEEK_API_KEY")
        self.baiduAppid = os.getenv("baidu_appid")
        self.baiduApiKey = os.getenv("baidu_api_key")
        self.baiduSecretKey = os.getenv("baidu_secret_key")
        
        # 聊天相关配置
        self.maxHistoryLength = 50
        self.cozeCnBaseUrl = "https://www.coze.cn"
