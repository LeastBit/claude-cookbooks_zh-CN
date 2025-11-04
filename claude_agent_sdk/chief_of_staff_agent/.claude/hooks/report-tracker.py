#!/usr/bin/env python3
"""
PostToolUse 钩子：跟踪所有文件写入和编辑
维护所有文档更改历史以供合规性使用
"""

import json
import os
import sys
from datetime import datetime


def track_report(tool_name, tool_input, tool_response):
    """记录所有文件创建/修改以供审计跟踪"""

    # 调试：记录调用了钩子
    print(f"🔍 钩子被调用用于工具: {tool_name}", file=sys.stderr)

    # 从工具输入获取文件路径
    file_path = tool_input.get("file_path", "")

    if not file_path:
        print("⚠️ tool_input中没有file_path", file=sys.stderr)
        return

    print(f"📝 跟踪文件: {file_path}", file=sys.stderr)

    # 跟踪所有文件写入/编辑（无过滤）

    # 准备历史文件路径
    history_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../../audit/report_history.json"
    )

    try:
        # 加载现有历史或创建新历史
        if os.path.exists(history_file):
            with open(history_file) as f:
                history = json.load(f)
        else:
            history = {"reports": []}

        # 确定操作类型
        action = "created" if tool_name == "Write" else "modified"

        # 如果有内容则计算字数
        content = tool_input.get("content", "") or tool_input.get("new_string", "")
        word_count = len(content.split()) if content else 0

        # 创建历史条目
        entry = {
            "timestamp": datetime.now().isoformat(),
            "file": os.path.basename(file_path),
            "path": file_path,
            "action": action,
            "word_count": word_count,
            "tool": tool_name,
        }

        # 添加到历史
        history["reports"].append(entry)

        # 只保留最后50条记录
        history["reports"] = history["reports"][-50:]

        # 保存更新的历史
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        with open(history_file, "w") as f:
            json.dump(history, f, indent=2)

        print(f"📊 文件已跟踪: {os.path.basename(file_path)} ({action})")

    except Exception as e:
        print(f"报告跟踪错误: {e}", file=sys.stderr)


# 主执行
if __name__ == "__main__":
    try:
        # 从标准输入读取输入
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        tool_response = input_data.get("tool_response", {})

        # 跟踪报告
        track_report(tool_name, tool_input, tool_response)

        # 始终成功退出
        sys.exit(0)

    except Exception as e:
        print(f"钩子错误: {e}", file=sys.stderr)
        sys.exit(0)
