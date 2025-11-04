"""
可观测性代理 - 使用MCP服务器监控GitHub
基于研究代理模式构建
"""

import asyncio
import os
from collections.abc import Callable
from typing import Any

from dotenv import load_dotenv

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

load_dotenv()


def get_activity_text(msg) -> str | None:
    """从消息中提取活动文本"""
    try:
        if "Assistant" in msg.__class__.__name__:
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
    """向控制台打印活动信息"""
    activity = get_activity_text(msg)
    if activity:
        print(activity)


# 预配置的GitHub MCP服务器
GITHUB_MCP_SERVER = {
    "github": {
        "command": "docker",
        "args": [
            "run",
            "-i",
            "--rm",
            "-e",
            "GITHUB_PERSONAL_ACCESS_TOKEN",
            "ghcr.io/github/github-mcp-server",
        ],
        "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": os.environ.get("GITHUB_TOKEN")},
    }
}


async def send_query(
    prompt: str,
    activity_handler: Callable[[Any], None | Any] = print_activity,
    continue_conversation: bool = False,
    mcp_servers: dict[str, Any] | None = None,
    use_github: bool = True,
) -> str | None:
    """
    向可观测性代理发送查询请求，支持MCP服务器。

    Args:
        prompt: 要发送的查询
        activity_handler: 活动更新回调函数
        continue_conversation: 如果为True则继续之前的对话
        mcp_servers: 自定义MCP服务器配置
        use_github: 包含GitHub MCP服务器（默认：True）

    Returns:
        最终结果文本或None（如果没有结果）
    """
    # 构建MCP服务器配置
    servers = {}
    if use_github and os.environ.get("GITHUB_TOKEN"):
        servers.update(GITHUB_MCP_SERVER)
    if mcp_servers:
        servers.update(mcp_servers)

    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5",
        allowed_tools=["mcp__github", "WebSearch", "Read"],
        continue_conversation=continue_conversation,
        system_prompt="你是一个专门监控GitHub仓库和CI/CD工作流的可观测性代理",
        mcp_servers=servers if servers else None,
        permission_mode="acceptEdits",
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
