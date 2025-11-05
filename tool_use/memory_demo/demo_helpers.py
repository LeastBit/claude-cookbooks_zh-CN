"""
记忆演示手册的帮助函数。

此模块提供可重用的函数，用于运行与 Claude 的对话循环、
处理工具执行和管理上下文。
"""

from typing import Any

from anthropic import Anthropic
from memory_tool import MemoryToolHandler


def execute_tool(tool_use: Any, memory_handler: MemoryToolHandler) -> str:
    """
    执行工具使用并返回结果。

    Args:
        tool_use: 来自 Claude 响应的工具使用对象
        memory_handler: 记忆工具处理器实例

    Returns:
        str: 工具执行的结果
    """
    if tool_use.name == "memory":
        result = memory_handler.execute(**tool_use.input)
        return result.get("success") or result.get("error", "未知错误")
    return f"未知工具: {tool_use.name}"


def run_conversation_turn(
    client: Anthropic,
    model: str,
    messages: list[dict[str, Any]],
    memory_handler: MemoryToolHandler,
    system: str,
    context_management: dict[str, Any] | None = None,
    max_tokens: int = 1024,
    verbose: bool = False,
) -> tuple[Any, list[dict[str, Any]], list[dict[str, Any]]]:
    """
    运行单次对话轮次，处理工具使用。

    Args:
        client: Anthropic 客户端实例
        model: 要使用的模型
        messages: 当前对话消息
        memory_handler: 记忆工具处理器实例
        system: 系统提示
        context_management: 可选的上下文管理配置
        max_tokens: 响应的最大令牌数
        verbose: 是否打印工具操作

    Returns:
        (响应, 助手内容, 工具结果) 的元组
    """
    memory_tool: dict[str, Any] = {"type": "memory_20250818", "name": "memory"}

    request_params: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": messages,
        "tools": [memory_tool],
        "betas": ["context-management-2025-06-27"],
    }

    if context_management:
        request_params["context_management"] = context_management

    response = client.beta.messages.create(**request_params)

    assistant_content = []
    tool_results = []

    for content in response.content:
        if content.type == "text":
            if verbose:
                print(f"💬 Claude: {content.text}\n")
            assistant_content.append({"type": "text", "text": content.text})
        elif content.type == "tool_use":
            if verbose:
                cmd = content.input.get("command")
                path = content.input.get("path", "")
                print(f"  🔧 记忆工具: {cmd} {path}")

            result = execute_tool(content, memory_handler)

            if verbose:
                result_preview = result[:80] + "..." if len(result) > 80 else result
                print(f"  ✓ 结果: {result_preview}")

            assistant_content.append(
                {"type": "tool_use", "id": content.id, "name": content.name, "input": content.input}
            )
            tool_results.append(
                {"type": "tool_result", "tool_use_id": content.id, "content": result}
            )

    return response, assistant_content, tool_results


def run_conversation_loop(
    client: Anthropic,
    model: str,
    messages: list[dict[str, Any]],
    memory_handler: MemoryToolHandler,
    system: str,
    context_management: dict[str, Any] | None = None,
    max_tokens: int = 1024,
    max_turns: int = 5,
    verbose: bool = False,
) -> Any:
    """
    运行完整的对话循环，直到 Claude 停止使用工具。

    Args:
        client: Anthropic 客户端实例
        model: 要使用的模型
        messages: 当前对话消息（将进行就地修改）
        memory_handler: 记忆工具处理器实例
        system: 系统提示
        context_management: 可选的上下文管理配置
        max_tokens: 响应的最大令牌数
        max_turns: 最大轮次数，以防止无限循环
        verbose: 是否打印进度

    Returns:
        最终的 API 响应
    """
    turn = 1
    response = None

    while turn <= max_turns:
        if verbose:
            print(f"\n🔄 轮次 {turn}:")

        response, assistant_content, tool_results = run_conversation_turn(
            client=client,
            model=model,
            messages=messages,
            memory_handler=memory_handler,
            system=system,
            context_management=context_management,
            max_tokens=max_tokens,
            verbose=verbose,
        )

        messages.append({"role": "assistant", "content": assistant_content})

        if tool_results:
            messages.append({"role": "user", "content": tool_results})
            turn += 1
        else:
            # 没有更多工具使用，对话完成
            break

    return response


def print_context_management_info(response: Any) -> tuple[bool, int]:
    """
    打印响应中的上下文管理信息。

    Args:
        response: 要分析的 API 响应

    Returns:
        (上下文是否清除, 保存的令牌数) 的元组
    """
    context_cleared = False
    saved_tokens = 0

    if hasattr(response, "context_management") and response.context_management:
        edits = getattr(response.context_management, "applied_edits", [])
        if edits:
            context_cleared = True
            cleared_uses = getattr(edits[0], "cleared_tool_uses", 0)
            saved_tokens = getattr(edits[0], "cleared_input_tokens", 0)
            print("  ✂️  触发了上下文编辑!")
            print(f"      • 清除了 {cleared_uses} 次工具使用")
            print(f"      • 节省了 {saved_tokens:,} 个令牌")
            print(f"      • 清除后: {response.usage.input_tokens:,} 个令牌")
        else:
            # 检查我们是否能看到它未触发的原因
            skipped_edits = getattr(response.context_management, "skipped_edits", [])
            if skipped_edits:
                print("  ℹ️  跳过了上下文清除:")
                for skip in skipped_edits:
                    reason = getattr(skip, "reason", "unknown")
                    print(f"      • 原因: {reason}")
            else:
                print("  ℹ️  上下文低于阈值 - 未触发清除")
    else:
        print("  ℹ️  未应用上下文管理")

    return context_cleared, saved_tokens
