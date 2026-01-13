import os
from typing import Any, Type, TypeVar
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)

class DeepSeekModel:
    """
    DeepSeek 模型
    """

    @classmethod
    def create_model(cls) -> ChatDeepSeek:
        api_key = "sk-bab3d0968b544542b626ee2f13cd61f6"
        base_url = os.getenv("DEEPSEEK_BASE_URL")
        if not api_key:
            raise RuntimeError("缺少环境变量 DEEPSEEK_API_KEY")
        return ChatDeepSeek(model="deepseek-chat", api_key=api_key, base_url=base_url)

    @classmethod
    def build_structured_agent(cls, response_format: Type[T]) -> Any:
        model = cls.create_model()
        agent = create_agent(model=model, response_format=response_format)
        return agent