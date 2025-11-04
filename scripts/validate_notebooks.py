#!/usr/bin/env python3
"""验证笔记本结构和内容。"""

import json
import sys
from pathlib import Path


def validate_notebook(path: Path) -> list:
    """验证单个笔记本。"""
    issues = []

    with open(path) as f:
        nb = json.load(f)

    # 检查空单元格
    for i, cell in enumerate(nb["cells"]):
        if not cell.get("source"):
            issues.append(f"单元格 {i}: 发现空单元格")

    # 检查错误输出
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] == "code":
            for output in cell.get("outputs", []):
                if output.get("output_type") == "error":
                    issues.append(f"单元格 {i}: 包含错误输出")

    return issues


def main():
    """检查作为参数传递的笔记本。"""
    has_issues = False

    # 从命令行参数获取笔记本路径
    notebooks = [Path(arg) for arg in sys.argv[1:] if arg.endswith(".ipynb")]

    if not notebooks:
        print("⚠️ 没有要验证的笔记本")
        sys.exit(0)

    for notebook in notebooks:
        issues = validate_notebook(notebook)
        if issues:
            has_issues = True
            print(f"\n❌ {notebook}:")
            for issue in issues:
                print(f"  - {issue}")

    if not has_issues:
        print(f"✅ 所有 {len(notebooks)} 个笔记本验证成功")
    else:
        print("\n❌ 发现必须在提交前修复的问题")

    # 如果在更改的文件中发现问题则退出并报错
    sys.exit(1 if has_issues else 0)


if __name__ == "__main__":
    main()
