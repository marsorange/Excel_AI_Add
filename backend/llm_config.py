"""
统一的LLM配置模块
支持多种LLM提供商，提供统一的配置入口
"""

import os
import httpx
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()


class LLMConfig:
    """统一的LLM配置类"""
    
    def __init__(self):
        # 优先使用 Qwen，如果没有配置则回退到 DeepSeek，最后是 OpenAI
        self.qwen_api_key = os.getenv("DASHSCOPE_API_KEY")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # 确定使用的LLM提供商
        if self.qwen_api_key and self.qwen_api_key != "你的API_KEY":
            self.provider = "qwen"
            self.api_key = self.qwen_api_key
            self.api_url = os.getenv("DASHSCOPE_API_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
            self.model_name = os.getenv("QWEN_MODEL", "qwen-turbo-latest")
        elif self.deepseek_api_key and self.deepseek_api_key != "你的API_KEY":
            self.provider = "deepseek"
            self.api_key = self.deepseek_api_key
            self.api_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
            self.model_name = "deepseek-chat"
        elif self.openai_api_key:
            self.provider = "openai"
            self.api_key = self.openai_api_key
            self.api_url = "https://api.openai.com/v1/chat/completions"
            self.model_name = "gpt-3.5-turbo"
        else:
            raise ValueError("未找到有效的LLM API配置，请配置 DASHSCOPE_API_KEY、DEEPSEEK_API_KEY 或 OPENAI_API_KEY")
    
    def check_api_key(self) -> bool:
        """检查API密钥是否有效"""
        return bool(self.api_key and self.api_key != "你的API_KEY")
    
    async def call_llm_api(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        统一的LLM API调用接口
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            **kwargs: 其他参数如 temperature, max_tokens 等
        
        Returns:
            LLM响应内容
        """
        if not self.check_api_key():
            raise ValueError(f"无效的 {self.provider.upper()} API Key")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建请求数据
        data = {
            "model": self.model_name,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000)
        }
        
        # 添加其他参数
        if "stream" in kwargs:
            data["stream"] = kwargs["stream"]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_url, headers=headers, json=data, timeout=30.0)
                response.raise_for_status()
                
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    raise ValueError("LLM API返回了意外的响应格式")
                    
        except httpx.RequestError as e:
            raise ConnectionError(f"连接到 {self.provider.upper()} API 时出错: {e}")
        except httpx.HTTPStatusError as e:
            raise ConnectionError(f"{self.provider.upper()} API返回错误: {e.response.status_code}")
        except Exception as e:
            raise RuntimeError(f"调用 {self.provider.upper()} API时出现未知错误: {e}")
    
    def get_provider_info(self) -> Dict[str, Any]:
        """获取当前LLM提供商信息"""
        return {
            "provider": self.provider,
            "model": self.model_name,
            "api_url": self.api_url,
            "has_valid_key": self.check_api_key()
        }


# 全局LLM配置实例
llm_config = LLMConfig()


def get_llm_config() -> LLMConfig:
    """获取全局LLM配置实例"""
    return llm_config


# 便捷函数
async def call_llm(messages: List[Dict[str, str]], **kwargs) -> str:
    """便捷的LLM调用函数"""
    return await llm_config.call_llm_api(messages, **kwargs)


def check_llm_config() -> bool:
    """检查LLM配置是否有效"""
    return llm_config.check_api_key() 