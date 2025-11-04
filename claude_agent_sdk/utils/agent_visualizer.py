def print_activity(msg):
    if "Assistant" in msg.__class__.__name__:
        print(
            f"🤖 {'使用中: ' + msg.content[0].name + '()' if hasattr(msg.content[0], 'name') else '思考中...'}"
        )
    elif "User" in msg.__class__.__name__:
        print("✓ 工具执行完成")


def print_final_result(messages):
    """打印最终智能体结果和成本信息"""
    # 获取结果消息（最后一条消息）
    result_msg = messages[-1]

    # 找到最后一条带有实际内容的助手消息
    for msg in reversed(messages):
        if msg.__class__.__name__ == "AssistantMessage" and msg.content:
            # 检查是否有文本内容（不仅仅是工具使用）
            for block in msg.content:
                if hasattr(block, "text"):
                    print(f"\n📝 最终结果:\n{block.text}")
                    break
            break

    # 如果可用，打印成本
    if hasattr(result_msg, "total_cost_usd"):
        print(f"\n📊 成本: ${result_msg.total_cost_usd:.2f}")

    # 如果可用，打印持续时间
    if hasattr(result_msg, "duration_ms"):
        print(f"⏱️  持续时间: {result_msg.duration_ms / 1000:.2f}秒")


def visualize_conversation(messages):
    """创建整个智能体对话的可视化表示"""
    print("\n" + "=" * 60)
    print("🤖 智能体对话时间线")
    print("=" * 60 + "\n")

    for i, msg in enumerate(messages):
        msg_type = msg.__class__.__name__

        if msg_type == "SystemMessage":
            print("⚙️  系统已初始化")
            if hasattr(msg, "data") and "session_id" in msg.data:
                print(f"   会话: {msg.data['session_id'][:8]}...")
            print()

        elif msg_type == "AssistantMessage":
            print("🤖 助手:")
            if msg.content:
                for block in msg.content:
                    if hasattr(block, "text"):
                        # 文本响应
                        text = block.text[:500] + "..." if len(block.text) > 500 else block.text
                        print(f"   💬 {text}")
                    elif hasattr(block, "name"):
                        # 工具使用
                        tool_name = block.name
                        print(f"   🔧 使用工具: {tool_name}")

                        # 显示某些工具的关键参数
                        if hasattr(block, "input") and block.input:
                            if tool_name == "WebSearch" and "query" in block.input:
                                print(f'      查询: "{block.input["query"]}"')
                            elif tool_name == "TodoWrite" and "todos" in block.input:
                                todos = block.input["todos"]
                                in_progress = [t for t in todos if t["status"] == "in_progress"]
                                completed = [t for t in todos if t["status"] == "completed"]
                                print(
                                    f"      📋 {len(completed)} 已完成, {len(in_progress)} 进行中"
                                )
            print()

        elif msg_type == "UserMessage":
            if msg.content and isinstance(msg.content, list):
                for result in msg.content:
                    if isinstance(result, dict) and result.get("type") == "tool_result":
                        print("👤 工具结果已接收")
                        tool_id = result.get("tool_use_id", "unknown")[:8]
                        print(f"   ID: {tool_id}...")

                        # 显示结果摘要
                        if "content" in result:
                            content = result["content"]
                            if isinstance(content, str):
                                # 显示更多内容
                                summary = content[:500] + "..." if len(content) > 500 else content
                                print(f"   📥 {summary}")
            print()

        elif msg_type == "ResultMessage":
            print("✅ 对话完成")
            if hasattr(msg, "num_turns"):
                print(f"   轮数: {msg.num_turns}")
            if hasattr(msg, "total_cost_usd"):
                print(f"   成本: ${msg.total_cost_usd:.2f}")
            if hasattr(msg, "duration_ms"):
                print(f"   持续时间: {msg.duration_ms / 1000:.2f}秒")
            if hasattr(msg, "usage"):
                usage = msg.usage
                total_tokens = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
                print(f"   令牌数: {total_tokens:,}")
            print()

    print("=" * 60 + "\n")
