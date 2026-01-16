from langchain_deepseek import ChatDeepSeek
from llms.deepseek import DeepSeekModel

def get_llm() -> ChatDeepSeek:
    """
    获取 LLM 实例
    """
    return DeepSeekModel.create_model()
