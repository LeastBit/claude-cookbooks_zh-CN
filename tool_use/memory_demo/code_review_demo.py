"""
代码审查助手演示 - 三个会话的演示。

本演示展示：
1. 会话 1：Claude 学习调试模式
2. 会话 2：Claude 应用学习到的模式（更快！）
3. 会话 3：带有上下文编辑的长会话

需要：
- 包含 ANTHROPIC_API_KEY 和 ANTHROPIC_MODEL 的 .env 文件
- 同目录下的 memory_tool.py 文件
"""

import os
from typing import Any, Dict, List

from anthropic import Anthropic
from dotenv import load_dotenv

import sys
from pathlib import Path

# 添加父目录到路径以导入 memory_tool
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory_tool import MemoryToolHandler


# 加载环境变量
load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = os.getenv("ANTHROPIC_MODEL")

if not API_KEY:
    raise ValueError("未找到 ANTHROPIC_API_KEY。请将 .env.example 复制为 .env 并添加您的 API 密钥。")

if not MODEL:
    raise ValueError("未找到 ANTHROPIC_MODEL。请将 .env.example 复制为 .env 并设置模型。")


# 上下文管理配置
CONTEXT_MANAGEMENT = {
    "edits": [
        {
            "type": "clear_tool_uses_20250919",
            "trigger": {"type": "input_tokens", "value": 30000},
            "keep": {"type": "tool_uses", "value": 3},
            "clear_at_least": {"type": "input_tokens", "value": 5000},
        }
    ]
}


class CodeReviewAssistant:
    """
    带有记忆和上下文编辑功能的代码审查助手。

    此助手：
    - 在审查代码前检查记忆中的调试模式
    - 存储学习到的模式以供未来会话使用
    - 当上下文过大时自动清除旧工具结果
    """

    def __init__(self, memory_storage_path: str = "./memory_storage"):
        """
        初始化代码审查助手。

        Args:
            memory_storage_path: 记忆存储路径
        """
        self.client = Anthropic(api_key=API_KEY)
        self.memory_handler = MemoryToolHandler(base_path=memory_storage_path)
        self.messages: List[Dict[str, Any]] = []

    def _create_system_prompt(self) -> str:
        """创建带有记忆指令的系统提示。"""
        return """您是专注于发现错误和提出改进建议的专家代码审查员。

记忆协议：
1. 检查您的 /memories 目录中是否有相关的调试模式或见解
2. 当您发现错误或模式时，用您学到的内容更新您的记忆
3. 保持记忆的有序性 - 使用描述性的文件名和清晰的内容

审查代码时：
- 识别错误、安全问题和代码质量问题
- 清楚地解释问题
- 提供修正版本
- 在记忆中存储重要的模式以供将来参考

记住：您的记忆在对话之间持续存在。明智地使用它。"""

    def _execute_tool_use(self, tool_use: Any) -> str:
        """执行工具使用并返回结果。"""
        if tool_use.name == "memory":
            result = self.memory_handler.execute(**tool_use.input)
            return result.get("success") or result.get("error", "未知错误")
        return f"未知工具: {tool_use.name}"

    def review_code(self, code: str, filename: str, description: str = "") -> Dict[str, Any]:
        """
        使用记忆增强分析审查代码。

        Args:
            code: 要审查的代码
            filename: 被审查文件的名称
            description: 可选的查找内容描述

        Returns:
            包含审查结果和元数据的字典
        """
        # 构建用户消息
        user_message = f"请审查来自 {filename} 的这段代码"
        if description:
            user_message += f"\n\n上下文: {description}"
        user_message += f"\n\n```python\n{code}\n```"

        self.messages.append({"role": "user", "content": user_message})

        # 跟踪令牌使用情况和上下文管理
        total_input_tokens = 0
        context_edits_applied = []

        # 对话循环
        turn = 1
        while True:
            print(f"  🔄 轮次 {turn}: 正在调用 Claude API...", end="", flush=True)
            response = self.client.beta.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=self._create_system_prompt(),
                messages=self.messages,
                tools=[{"type": "memory_20250818", "name": "memory"}],
                betas=["context-management-2025-06-27"],
                context_management=CONTEXT_MANAGEMENT,
            )

            print(" ✓")

            # 跟踪使用情况
            total_input_tokens = response.usage.input_tokens

            # 检查上下文管理
            if hasattr(response, "context_management") and response.context_management:
                applied = getattr(response.context_management, "applied_edits", [])
                if applied:
                    context_edits_applied.extend(applied)

            # 处理响应内容
            assistant_content = []
            tool_results = []
            final_text = []

            for content in response.content:
                if content.type == "text":
                    assistant_content.append({"type": "text", "text": content.text})
                    final_text.append(content.text)
                elif content.type == "tool_use":
                    cmd = content.input.get("command", "unknown")
                    path = content.input.get("path", "")
                    print(f"    🔧 记忆: {cmd} {path}")

                    # 执行工具
                    result = self._execute_tool_use(content)

                    assistant_content.append(
                        {
                            "type": "tool_use",
                            "id": content.id,
                            "name": content.name,
                            "input": content.input,
                        }
                    )

                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": result,
                        }
                    )

            # 添加助手消息
            self.messages.append({"role": "assistant", "content": assistant_content})

            # 如果有工具结果，添加它们并继续
            if tool_results:
                self.messages.append({"role": "user", "content": tool_results})
                turn += 1
            else:
                # 没有更多工具使用，完成
                print()
                break

        return {
            "review": "\n".join(final_text),
            "input_tokens": total_input_tokens,
            "context_edits": context_edits_applied,
        }

    def start_new_session(self) -> None:
        """开始新的对话会话（记忆持续）。"""
        self.messages = []


def run_session_1() -> None:
    """会话 1：学习调试模式。"""
    print("=" * 80)
    print("会话 1：从第一次代码审查中学习")
    print("=" * 80)

    assistant = CodeReviewAssistant()

    # 读取示例代码
    with open("memory_demo/sample_code/web_scraper_v1.py", "r") as f:
        code = f.read()

    print("\n📋 正在审查 web_scraper_v1.py...")
    print("\n有时会丢失结果的多线程网络爬虫。\n")

    result = assistant.review_code(
        code=code,
        filename="web_scraper_v1.py",
        description="此爬虫有时返回的结果比预期少。"
        "计数在不同的运行中不一致。您能找到问题吗？",
    )

    print("\n🤖 Claude 的审查:\n")
    print(result["review"])
    print(f"\n📊 使用的输入令牌: {result['input_tokens']:,}")

    if result["context_edits"]:
        print(f"\n🧹 应用的上下文编辑: {result['context_edits']}")

    print("\n✅ 会话 1 完成 - Claude 学到了调试模式！\n")


def run_session_2() -> None:
    """会话 2：应用学习到的模式。"""
    print("=" * 80)
    print("会话 2：应用学习到的模式（新对话）")
    print("=" * 80)

    # 新的助手实例（新对话，但记忆持续）
    assistant = CodeReviewAssistant()

    # 读取具有类似错误的不同示例代码
    with open("memory_demo/sample_code/api_client_v1.py", "r") as f:
        code = f.read()

    print("\n📋 正在审查 api_client_v1.py...")
    print("\n带有并发请求的异步 API 客户端。\n")

    result = assistant.review_code(
        code=code,
        filename="api_client_v1.py",
        description="审查此异步 API 客户端。"
        "它并发获取多个端点。有问题吗？",
    )

    print("\n🤖 Claude 的审查:\n")
    print(result["review"])
    print(f"\n📊 使用的输入令牌: {result['input_tokens']:,}")

    print("\n✅ 会话 2 完成 - Claude 更快地应用了学习到的模式！\n")


def run_session_3() -> None:
    """会话 3：带有上下文编辑的长会话。"""
    print("=" * 80)
    print("会话 3：带有上下文编辑的长会话")
    print("=" * 80)

    assistant = CodeReviewAssistant()

    # 读取数据处理代码（有多个问题）
    with open("memory_demo/sample_code/data_processor_v1.py", "r") as f:
        code = f.read()

    print("\n📋 正在审查 data_processor_v1.py...")
    print("\n包含多个并发处理类的大文件。\n")

    result = assistant.review_code(
        code=code,
        filename="data_processor_v1.py",
        description="此数据处理器并发处理文件。"
        "还有一个 SharedCache 类。审查所有组件是否有问题。",
    )

    print("\n🤖 Claude 的审查:\n")
    print(result["review"])
    print(f"\n📊 使用的输入令牌: {result['input_tokens']:,}")

    if result["context_edits"]:
        print("\n🧹 应用的上下文管理:")
        for edit in result["context_edits"]:
            print(f"  - 类型: {getattr(edit, 'type', 'unknown')}")
            print(f"  - 清除的工具使用: {getattr(edit, 'cleared_tool_uses', 0)}")
            print(f"  - 保存的令牌: {getattr(edit, 'cleared_input_tokens', 0):,}")

    print("\n✅ 会话 3 完成 - 上下文编辑保持了对话的可管理性！\n")


def main() -> None:
    """运行所有三个演示会话。"""
    print("\n🚀 代码审查助手演示\n")
    print("本演示展示:")
    print("1. 会话 1：Claude 学习调试模式")
    print("2. 会话 2：Claude 应用学习到的模式（新对话）")
    print("3. 会话 3：带有上下文编辑的长会话\n")

    input("按 Enter 键开始会话 1...")
    run_session_1()

    input("按 Enter 键开始会话 2...")
    run_session_2()

    input("按 Enter 键开始会话 3...")
    run_session_3()

    print("=" * 80)
    print("🎉 演示完成!")
    print("=" * 80)
    print("\n关键要点:")
    print("- 记忆工具实现了跨对话学习")
    print("- Claude 在识别类似错误方面变得更快")
    print("- 上下文编辑优雅地处理了长会话")
    print("\n💡 对于生产环境的 GitHub PR 审查，请查看:")
    print("   https://github.com/anthropics/claude-code-action\n")


if __name__ == "__main__":
    main()
