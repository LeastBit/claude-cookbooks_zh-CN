#!/usr/bin/env python3
"""
PostToolUse 钩子：通过Bash工具执行Python脚本时记录日志
区分：
- 工具：Claude SDK工具（Bash、Write、Edit等）
- 脚本：通过Bash工具执行的Python脚本
"""

import json
import os
import sys
from datetime import datetime


def log_script_usage(tool_name, tool_input, tool_response):
    """通过Bash工具记录Python脚本的执行"""

    # 只跟踪Bash工具（用于执行脚本）
    if tool_name != "Bash":
        return

    # 从工具输入获取命令
    command = tool_input.get("command", "")

    # 检查是否正在执行scripts/目录中的Python脚本
    # 支持两种格式："python scripts/file.py" 和 "./scripts/file.py"
    import re

    # 尝试匹配任一模式：python scripts/... 或 ./scripts/... 或 scripts/...
    script_match = re.search(r"(?:python\s+)?(?:\./)?scripts/(\w+\.py)", command)
    if not script_match:
        return

    # 仅当是scripts/目录执行时才继续
    if "scripts/" not in command:
        return

    script_file = script_match.group(1)

    # 准备日志文件路径
    log_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../../audit/script_usage_log.json"
    )

    try:
        # 加载现有日志或创建新日志
        if os.path.exists(log_file):
            with open(log_file) as f:
                log_data = json.load(f)
        else:
            log_data = {"script_executions": []}

        # 创建日志条目
        entry = {
            "timestamp": datetime.now().isoformat(),
            "script": script_file,
            "command": command,
            "description": tool_input.get("description", "无描述"),
            "tool_used": "Bash",  # 用于执行脚本的工具
            "success": tool_response.get("success", True) if tool_response else True,
        }

        # 添加到日志
        log_data["script_executions"].append(entry)

        # 只保留最后100条记录
        log_data["script_executions"] = log_data["script_executions"][-100:]

        # 保存更新的日志
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "w") as f:
            json.dump(log_data, f, indent=2)

        print(f"📜 脚本已执行: {script_file}")

    except Exception as e:
        print(f"脚本日志记录错误: {e}", file=sys.stderr)


# 主执行
if __name__ == "__main__":
    try:
        # 从标准输入读取输入
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        tool_response = input_data.get("tool_response", {})

        # 记录脚本使用情况（通过Bash工具执行时）
        log_script_usage(tool_name, tool_input, tool_response)

        # 始终成功退出
        sys.exit(0)

    except Exception as e:
        print(f"钩子错误: {e}", file=sys.stderr)
        sys.exit(0)
