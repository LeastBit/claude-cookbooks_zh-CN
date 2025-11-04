from anthropic import Anthropic
import os
import re

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def llm_call(prompt: str, system_prompt: str = "", model="claude-sonnet-4-5") -> str:
    """
    使用给定的提示调用模型并返回响应。

    参数:
        prompt (str): 发送给模型的用户提示。
        system_prompt (str, 可选): 发送给模型的系统提示。默认为""。
        model (str, 可选): 用于调用的模型。默认为"claude-sonnet-4-5"。

    返回:
        str: 来自语言模型的响应。
    """
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    messages = [{"role": "user", "content": prompt}]
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system_prompt,
        messages=messages,
        temperature=0.1,
    )
    return response.content[0].text


def extract_xml(text: str, tag: str) -> str:
    """
    从给定文本中提取指定XML标签的内容。用于解析结构化响应

    参数:
        text (str): 包含XML的文本。
        tag (str): 要提取内容的XML标签。

    返回:
        str: 指定XML标签的内容，如果未找到标签则返回空字符串。
    """
    match = re.search(f"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
    return match.group(1) if match else ""
