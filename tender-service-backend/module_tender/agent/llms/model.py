from llms.deepseek import DeepSeekModel

def get_llm():
    return DeepSeekModel.create_model()
