from langchain.adapters.openai import convert_openai_messages
from langchain_openai import ChatOpenAI


def _common(prompt: list, model: str, max_retries: int = 2, response_format: str = None) -> tuple:
    optional_params = {}
    if response_format == 'json':
        optional_params = {
            "response_format": {"type": "json_object"}
        }
    lc_messages = convert_openai_messages(prompt)
    model = ChatOpenAI(model=model, max_retries=max_retries, model_kwargs=optional_params)
    return optional_params, lc_messages, model


def call_model(prompt: list, model: str, max_retries: int = 2, response_format: str = None) -> str:
    optional_params, lc_messages, llm = _common(prompt, model, max_retries, response_format)
    response = llm.invoke(lc_messages)
    content = response.content
    return content


async def acall_model(prompt: list, model: str, max_retries: int = 2, response_format: str = None) -> str:
    optional_params, lc_messages, llm = _common(prompt, model, max_retries, response_format)
    response = await llm.ainvoke(lc_messages)
    content = response.content
    return content
