"""
首席助理代理
"""

import asyncio
import json
import os
from collections.abc import Callable
from typing import Any, Literal

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
                    return f"🤖 使用中: {first_content.name}()"
            return "🤖 思考中..."
        elif "User" in msg.__class__.__name__:
            return "✓ 工具执行完成"
    except (AttributeError, IndexError):
        pass
    return None


def print_activity(msg) -> None:
    """向控制台打印活动信息"""
    activity = get_activity_text(msg)
    if activity:
        print(activity)


async def send_query(
    prompt: str,
    continue_conversation: bool = False,
    permission_mode: Literal["default", "plan", "acceptEdits"] = "default",
    output_style: str | None = None,
    activity_handler: Callable[[Any], None | Any] = print_activity,
) -> tuple[str | None, list]:
    """
    向首席助理代理发送查询，集成了所有功能。

    Args:
        prompt: 要发送的查询（可以包含斜杠命令如 /budget-impact）
        activity_handler: 活动更新回调（默认：print_activity）
        continue_conversation: 如果为True则继续之前的对话
        permission_mode: "default"（执行）、"plan"（仅思考）或 "acceptEdits"
        output_style: 覆盖输出样式（例如："executive"、"technical"、"board-report"）

    Returns:
        (result, messages) 的元组 - result是最终文本，messages是完整对话

    自动包含/利用的功能：
        - 内存：从 chief_of_staff/CLAUDE.md 加载的 CLAUDE.md 上下文
        - 子代理：通过 Task 工具的 financial-analyst 和 recruiter（定义在 .claude/agents 中）
        - 自定义脚本：通过 Bash 运行的 tools/ 中的 Python 脚本
        - 斜杠命令：从 .claude/commands/ 展开
        - 输出样式：定义在 .claude/output-styles 中的自定义输出样式
        - 钩子：基于 settings.local.json 触发，定义在 .claude/hooks 中
    """

    system_prompt = """你是 TechStart Inc 的首席助理，这是一家50人的初创公司。

        除了你的工具和两个子代理外，你还有 scripts/ 目录中的自定义 Python 脚本可以通过 Bash 运行：
        - python scripts/financial_forecast.py: 高级财务建模
        - python scripts/talent_scorer.py: 候选人评分算法
        - python scripts/decision_matrix.py: 战略决策框架

        你可以访问 financial_data/ 目录中的公司数据。
        """

    # 构建带有可选输出样式的选项
    options_dict = {
        "model": "claude-sonnet-4-5",
        "allowed_tools": [
            "Task",  # 启用子代理委派
            "Read",
            "Write",
            "Edit",
            "Bash",
            "WebSearch",
        ],
        "continue_conversation": continue_conversation,
        "system_prompt": system_prompt,
        "permission_mode": permission_mode,
        "cwd": os.path.dirname(os.path.abspath(__file__)),
    }

    # 如果指定了输出样式则添加
    if output_style:
        options_dict["settings"] = json.dumps({"outputStyle": output_style})

    options = ClaudeAgentOptions(**options_dict)

    result = None
    messages = []  # 这是仅用于此代理轮次的附加消息

    try:
        async with ClaudeSDKClient(options=options) as agent:
            await agent.query(prompt=prompt)
            async for msg in agent.receive_response():
                messages.append(msg)
                if asyncio.iscoroutinefunction(activity_handler):
                    await activity_handler(msg)
                else:
                    activity_handler(msg)

                if hasattr(msg, "result"):
                    result = msg.result
    except Exception as e:
        print(f"❌ 查询错误: {e}")
        raise

    return result, messages
