import os
from time import sleep
from typing import Any, Type, TypeVar

from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from pydantic import BaseModel

from exceptions.exception import ServiceException
from module_tender.entity.structured_entity.tender_notice_fetcher import TenderNoticeFetcher
from utils.log_util import logger

T = TypeVar("T", bound=BaseModel)


def build_deepseek_model() -> ChatDeepSeek:
    api_key = "sk-bab3d0968b544542b626ee2f13cd61f6"
    base_url = os.getenv("DEEPSEEK_BASE_URL")
    if not api_key:
        raise RuntimeError("缺少环境变量 DEEPSEEK_API_KEY")
    return ChatDeepSeek(model="deepseek-chat", api_key=api_key, base_url=base_url)


def build_structured_agent(response_format: Type[T]) -> Any:
    model = build_deepseek_model()
    agent = create_agent(model=model, response_format=response_format)
    return agent


def extract_structured_data(
    text: str,
    response_model: Type[T],
    instruction: str = "从下述文本中提取相关信息：",
    default_factory: Type[T] | None = None,
    *,
    max_retries: int = 2,
    retry_delay: float = 0.5,
    raise_on_error: bool = False,
    max_chars: int = 18000,
) -> T | None:
    """
    通用结构化数据提取方法

    :param text: 待提取的源文本
    :param response_model: 目标 Pydantic 模型类
    :param instruction: 提取指令/提示词前缀
    :param default_factory: 失败时返回的默认对象工厂（可选）
    :param max_retries: 最大重试次数
    :param retry_delay: 重试延迟
    :param raise_on_error: 最终失败是否抛出异常
    :param max_chars: 文本最大截断长度
    :return: 提取的模型实例或 None/默认值
    """
    safe_text = (text or "")[:max_chars]
    last_error: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            agent = build_structured_agent(response_format=response_model)
            result = agent.invoke(
                {"messages": [{"role": "user", "content": f"{instruction}{safe_text}"}]}
            )
            structured = result.get("structured_response")
            if isinstance(structured, response_model):
                return structured
            
            logger.warning(f"结构化提取返回为空或不符合模型 {response_model.__name__}")
            if default_factory:
                return default_factory()
            return None
            
        except Exception as e:
            last_error = e
            logger.error(f"结构化提取异常 ({response_model.__name__}): {e}")
            if attempt < max_retries:
                sleep(retry_delay * (2**attempt))
            else:
                if raise_on_error:
                    raise ServiceException(message=f"结构化提取失败: {response_model.__name__}") from e
                if default_factory:
                    return default_factory()
                return None
    
    # 理论上不会走到这里，除非循环逻辑有误，兜底处理
    return None


def _default_tender_notice() -> TenderNoticeFetcher:
    return TenderNoticeFetcher(
        projectType="其他",
        bidControlPrice=0.0,
        constructionScale="",
        tenderScope="",
        constructionContent="",
        duration="",
        registrationDeadline="",
    )


def extract_tender_fields(
    text: str,
    *,
    max_retries: int = 2,
    retry_delay: float = 0.5,
    raise_on_error: bool = False,
    max_chars: int = 18000,
) -> TenderNoticeFetcher:
    """
    特化方法：专门用于招标公告信息的提取
    """
    result = extract_structured_data(
        text=text,
        response_model=TenderNoticeFetcher,
        instruction="从下述公告中提取相关信息：",
        default_factory=_default_tender_notice,
        max_retries=max_retries,
        retry_delay=retry_delay,
        raise_on_error=raise_on_error,
        max_chars=max_chars
    )
    # 因为 extract_structured_data 可能返回 None，但我们在 default_factory 提供了默认值
    # 所以这里通常可以直接返回。为了类型安全，做个兜底
    return result if result is not None else _default_tender_notice()

