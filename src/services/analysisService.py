from abc import ABC, abstractmethod
from typing import Dict, List
import openai
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
from ..config import Config

class BaseAnalysisService(ABC):
    """AI分析服务基类"""
    
    @abstractmethod
    def analyze_danger(self, history_messages: List[Dict]) -> str:
        """分析危险内容"""
        pass
    
    @abstractmethod
    def analyze_preferences(self, history_messages: List[Dict]) -> Dict:
        """分析用户偏好"""
        pass

class DeepseekAnalysisService(BaseAnalysisService):
    """基于Deepseek的AI分析服务实现"""

    def __init__(self):
        self.config = Config()
        self.client = openai.OpenAI(
            api_key=self.config.deepseekApiKey,
            base_url="https://api.deepseek.com"
        )

    def _format_history(self, history_messages: List[Dict]) -> str:
        """格式化历史消息"""
        # 兼容不同历史记录字段（'message' 或 'content'）
        lines = []
        for msg in history_messages:
            if not isinstance(msg, dict):
                continue
            role = msg.get('role', '')
            text = msg.get('message') if msg.get('message') is not None else msg.get('content', '')
            if text:
                lines.append(f"{role}:{text}")
        return "\n".join(lines)

    def analyze_danger_keywords(self, history_messages: List[Dict]) -> str:
        """AI推测用户危机关键词"""
        messages = [
            ChatCompletionSystemMessageParam(
                role="system",
                content="""
                你是心理健康AI助手，请根据用户与智能体的全部对话内容，分析并推测用户可能存在的心理危机关键词。
                仅从type: dangerous的对话中提取用户表达的内容作为输入，
                只需输出最相关的1~3个关键词（如：自杀、绝望、伤害、抑郁、孤独、无助等），无需解释。
                格式要求：以逗号分隔关键词。
                """
            ),
            ChatCompletionUserMessageParam(
                role="user",
                content=self._format_history(history_messages)
            )
        ]
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=0.7
            )
            content = response.choices[0].message.content
            return content if content else ""
        except Exception as e:
            # 友好处理常见的余额/认证错误，返回空字符串以避免前端崩溃
            err = str(e)
            if 'Insufficient Balance' in err or '402' in err:
                print('Deepseek analyze_danger_keywords: 服务不可用（余额不足或计费问题）')
            else:
                print(f'Deepseek analyze_danger_keywords 调用失败: {err}')
            return ""
        
    def analyze_danger(self, history_messages: List[Dict]) -> str:
        messages = [
            ChatCompletionSystemMessageParam(
                role="system",
                content="""
                现有一个心理分析项目，目前检测到了用户存在心理危机,
                你需要分析用户和机器人的对话，为"介入的专业人士"给出总结和处理建议。
                要求: 1.结合专业心理学知识回答 
                     2.字数控制在200字左右（历史总结占100字左右），适度分行便于阅读
                """
            ),
            ChatCompletionUserMessageParam(
                role="user",
                content=self._format_history(history_messages)
            )
        ]
        
        print("Deepseek危机分析中...")
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=1.0
            )
            if response.choices[0].message.content is not None:
                analysis = response.choices[0].message.content
                try:
                    vidlie = self.cross_validation(analysis)
                except Exception as e:
                    print(f"交叉验证失败: {e}")
                    vidlie = "交叉验证失败"
                return analysis + "\n\n\n以下为对分析结果多模型交叉验证的结果：\n" + vidlie
            else:
                return ""
        except Exception as e:
            err = str(e)
            if 'Insufficient Balance' in err or '402' in err:
                print('Deepseek analyze_danger: 服务不可用（余额不足或计费问题）')
                return 'AI 服务暂不可用（余额或计费问题），无法生成危机分析。'
            else:
                print(f'Deepseek analyze_danger 调用失败: {err}')
                return 'AI 服务调用失败，无法生成危机分析。'
    
    def cross_validation(self, ai_response: str) -> str:
        messages = [
            ChatCompletionSystemMessageParam(
                role="system",
                content="""
                现在有一个AI智能体为人类出具建议，请评估这个建议的可靠性并给出0%~100%的置信度，确保人类不会被AI幻觉误导。
                要求: 1.结合专业心理学知识回答
                     2.输出置信度，例如：置信度：90%（由多模型交叉验证得出），并附加100字以内的简短理由
                """
            ),
            ChatCompletionUserMessageParam(
                role="user",
                content=ai_response
            )
        ]
        print("Deepseek交叉验证中...")
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=0.5
            )
            return response.choices[0].message.content if response.choices[0].message.content is not None else ""
        except Exception as e:
            err = str(e)
            if 'Insufficient Balance' in err or '402' in err:
                print('Deepseek cross_validation: 服务不可用（余额不足或计费问题）')
            else:
                print(f"交叉验证失败: {err}")
            return "交叉验证失败"
        
            return parsed
    def analyze_preferences(self, history_messages: List[Dict]) -> Dict:
        messages = [
            ChatCompletionSystemMessageParam(
                role="system",
                content="请分析聊天历史，总结用户的话题偏好、性格特点等信息。"
            ),
            ChatCompletionUserMessageParam(
                role="user",
                content=self._format_history(history_messages)
            )
        ]
        
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7
        )
        
        import json
        content = response.choices[0].message.content
        if content is None:
            return {}
        try:
            return json.loads(content)
        except Exception:
            return {"summary": content}

    def analyze_crisis_index(self, history_messages: List[Dict], emotion_records: List[Dict]) -> Dict:
        """综合聊天记录与表情识别记录，计算心理危机指数(0-100)，并输出说明、特征、建议与交叉验证结果。"""
        # 1. 准备输入
        combined_text = self._format_history(history_messages)
        emotion_summary_lines = []
        counts = {}
        if isinstance(emotion_records, list):
            for e in emotion_records:
                if isinstance(e, dict):
                    dom = None
                    if e.get('data') and isinstance(e.get('data'), dict):
                        dom = e['data'].get('dominant_emotion')
                    if not dom:
                        dom = e.get('trigger_message')
                    if dom:
                        counts[dom] = counts.get(dom, 0) + 1
        if counts:
            emotion_summary_lines.append('表情统计:')
            for k, v in counts.items():
                emotion_summary_lines.append(f"{k}:{v}")

        input_content = combined_text + "\n\n" + "\n".join(emotion_summary_lines)

        system_prompt = (
            "你是专业的心理健康分析师。请根据以下用户与智能体的全部对话和表情识别总结，计算一个心理危机指数（0-100，整数），"
            "指数越高表示危机可能性越高。请同时输出：score（整数）、interpretation（简短含义）、features（导致高分的关键特征列表）、"
            "explanation（给出评分的解释，3-5句）、suggestions（给专业心理专家的干预建议，50-150字）。以合法JSON格式返回以上字段。"
        )

        messages = [
            ChatCompletionSystemMessageParam(role="system", content=system_prompt),
            ChatCompletionUserMessageParam(role="user", content=input_content)
        ]

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=0.7
            )
            content = response.choices[0].message.content or ""
        except Exception as e:
            print(f"analyze_crisis_index 调用失败: {e}")
            content = ""

        # 解析为 JSON（增强：支持提取 code-fence 中的 JSON 或文本内第一个 JSON 对象）
        import json as _json, re
        parsed = None
        # 尝试直接解析
        try:
            parsed = _json.loads(content)
        except Exception:
            # 尝试提取 ```json ... ``` 或 ``` ... ``` 中的 JSON
            m = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", content, re.IGNORECASE)
            if not m:
                m = re.search(r"```\s*(\{[\s\S]*?\})\s*```", content)
            if not m:
                # 尝试提取文本中第一个花括号包围的 JSON 对象
                m = re.search(r"(\{[\s\S]*?\})", content)

            if m:
                json_text = m.group(1)
                try:
                    parsed = _json.loads(json_text)
                except Exception:
                    parsed = None

        if parsed is None:
            # 保底解析：尝试从文本中抽取一个数字作为分数，并将全文放入 explanation
            score = 0
            mnum = re.search(r"(\d{1,3})", content)
            if mnum:
                try:
                    score = max(0, min(100, int(mnum.group(1))))
                except Exception:
                    score = 0
            parsed = {
                "score": score,
                "interpretation": "AI未返回结构化JSON，已根据文本尝试推断",
                "features": [],
                "explanation": content.strip() or "",
                "suggestions": "请查看原始AI输出",
                "validation": "无"
            }

        # 多模型交叉验证（保留原有行为）
        try:
            validation = self.cross_validation(_json.dumps(parsed))
            parsed['validation'] = validation
        except Exception as e:
            print(f"交叉验证失败: {e}")

        return parsed
