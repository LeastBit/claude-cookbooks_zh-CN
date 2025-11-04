"""
研究代理 - 使用内置会话管理的 Claude SDK
"""

import asyncio
from collections.abc import Callable
from typing import Any

from dotenv import load_dotenv

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

load_dotenv()


def get_activity_text(msg) -> str | None:
    """从消息中提取活动文本"""
    try:
        if "Assistant" in msg.__class__.__name__:
            # 检查内容是否存在且有项目
            if hasattr(msg, "content") and msg.content:
                first_content = msg.content[0] if isinstance(msg.content, list) else msg.content
                if hasattr(first_content, "name"):
                    return f"🤖 正在使用: {first_content.name}()"
            return "🤖 思考中..."
        elif "User" in msg.__class__.__name__:
            return "✓ 工具已完成"
    except (AttributeError, IndexError):
        pass
    return None


def print_activity(msg) -> None:
    """将活动打印到控制台"""
    activity = get_activity_text(msg)
    if activity:
        print(activity)


async def send_query(
    prompt: str,
    activity_handler: Callable[[Any], None | Any] = print_activity,
    continue_conversation: bool = False,
) -> str | None:
    """
    使用 Claude SDK 发送查询，最小化开销。

    参数:
        prompt: 要发送的查询
        activity_handler: 活动更新的回调函数
        continue_conversation: 如果为 True 则继续之前的对话

    注意:
        对于 activity_handler - 我们支持同步和异步处理器
        使模块能够在不同上下文中工作:
            - 同步处理器（如 print_activity）用于简单的控制台输出
            - 异步处理器用于需要 WebSocket/网络 I/O 的 Web 应用程序
        在生产环境中，您通常会根据需要只使用一种类型

    返回:
        最终结果文本，如果没有结果则返回 None
    """
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5",
        allowed_tools=["WebSearch", "Read"],
        continue_conversation=continue_conversation,
        system_prompt="您是专门从事人工智能研究的研究代理",
    )

    result = None

    try:
        async with ClaudeSDKClient(options=options) as agent:
            await agent.query(prompt=prompt)
            async for msg in agent.receive_response():
                if asyncio.iscoroutinefunction(activity_handler):
                    await activity_handler(msg)
                else:
                    activity_handler(msg)

                if hasattr(msg, "result"):
                    result = msg.result
    except Exception as e:
        print(f"❌ 查询错误: {e}")
        raise

    return result
