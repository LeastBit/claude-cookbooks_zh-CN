#!/usr/bin/env python3
"""
全面的笔记本验证工具，带仪表板和报告功能。

功能：
- 带检查点的渐进式验证
- 问题分类和自动修复
- 带趋势的仪表板生成
- GitHub问题导出
- 幂等性状态持久化
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
import os
import argparse


class NotebookValidator:
    """验证Jupyter笔记本的常见问题。"""

    def __init__(self):
        self.state_file = Path(".notebook_validation_state.json")
        self.checkpoint_file = Path(".notebook_validation_checkpoint.json")
        self.state = self.load_state()

    def load_state(self) -> dict:
        """如果存在，加载之前的验证状态。"""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("警告：无法解析状态文件，将重新开始")

        return {
            "version": "1.0",
            "last_full_run": None,
            "notebooks": {},
            "history": [],
            "ignored": {},
        }

    def save_state(self):
        """保存当前状态到文件。"""
        # 更新历史记录
        total = len(self.state["notebooks"])
        passing = sum(1 for n in self.state["notebooks"].values() if n.get("status") == "pass")

        today = datetime.now().strftime("%Y-%m-%d")

        # 更新或添加今天的条目
        if self.state["history"] and self.state["history"][-1]["date"] == today:
            self.state["history"][-1] = {"date": today, "passing": passing, "total": total}
        else:
            self.state["history"].append({"date": today, "passing": passing, "total": total})

        # 只保留最近30天的历史记录
        self.state["history"] = self.state["history"][-30:]

        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2, default=str)

    def validate_notebook(self, notebook_path: Path, mode: str = "full") -> dict:
        """验证单个笔记本。"""
        result = {"status": "pass", "issues": [], "last_validated": datetime.now().isoformat()}

        # 快速结构检查
        try:
            with open(notebook_path) as f:
                nb = json.load(f)
        except Exception as e:
            result["status"] = "error"
            result["issues"].append(
                {"type": "invalid_json", "severity": "critical", "details": str(e)}
            )
            return result

        # 检查空单元格
        for i, cell in enumerate(nb.get("cells", [])):
            if not cell.get("source"):
                result["issues"].append(
                    {
                        "type": "empty_cell",
                        "severity": "info",
                        "cell": i,
                        "details": "发现空单元格",
                    }
                )

        # 检查错误输出
        for i, cell in enumerate(nb.get("cells", [])):
            if cell.get("cell_type") == "code":
                for output in cell.get("outputs", []):
                    if output.get("output_type") == "error":
                        result["status"] = (
                            "warning" if result["status"] == "pass" else result["status"]
                        )
                        result["issues"].append(
                            {
                                "type": "error_output",
                                "severity": "warning",
                                "cell": i,
                                "details": "单元格包含错误输出",
                            }
                        )

        # 检查过时的模型
        deprecated_models = {
            "claude-3-5-sonnet-20240620": "claude-sonnet-4-5",
            "claude-3-5-sonnet-20241022": "claude-sonnet-4-5",
            "claude-3-5-sonnet-latest": "claude-sonnet-4-5",
            "claude-3-haiku-20240307": "claude-haiku-4-5",
            "claude-3-5-haiku-20241022": "claude-haiku-4-5",
            "claude-3-opus-20240229": "claude-opus-4-1",
            "claude-3-opus-latest": "claude-opus-4-1",
            "claude-sonnet-4-20250514": "claude-sonnet-4-5",
            "claude-opus-4-20250514": "claude-opus-4-1",
        }

        for i, cell in enumerate(nb.get("cells", [])):
            if cell.get("cell_type") == "code":
                source = "".join(cell.get("source", []))

                # 检查过时的模型
                for old_model, new_model in deprecated_models.items():
                    if old_model in source:
                        result["status"] = (
                            "warning" if result["status"] == "pass" else result["status"]
                        )
                        result["issues"].append(
                            {
                                "type": "deprecated_model",
                                "severity": "warning",
                                "cell": i,
                                "details": {"current": old_model, "suggested": new_model},
                            }
                        )

                # 检查硬编码的API密钥
                if "sk-ant-" in source:
                    result["status"] = "error"
                    result["issues"].append(
                        {
                            "type": "hardcoded_api_key",
                            "severity": "critical",
                            "cell": i,
                            "details": "检测到硬编码的Claude API密钥",
                        }
                    )
                elif (
                    "api_key=" in source.lower()
                    and "os.environ" not in source
                    and "getenv" not in source
                ):
                    result["status"] = "error"
                    result["issues"].append(
                        {
                            "type": "api_key_not_env",
                            "severity": "critical",
                            "cell": i,
                            "details": "API密钥未使用环境变量",
                        }
                    )

        # 如果是全模式，执行笔记本
        if mode == "full" and result["status"] != "error":
            if os.environ.get("ANTHROPIC_API_KEY"):
                exec_result = self.execute_notebook(notebook_path)
                if not exec_result["success"]:
                    result["status"] = "error"
                    result["issues"].append(
                        {
                            "type": "execution_failure",
                            "severity": "error",
                            "details": exec_result["error"],
                        }
                    )

        return result

    def execute_notebook(self, notebook_path: Path) -> dict:
        """执行笔记本并返回成功状态。"""
        cmd = [
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            "--ExecutePreprocessor.timeout=120",
            "--output",
            "/dev/null",
            "--stdout",
            str(notebook_path),
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, timeout=130, text=True)
            if result.returncode == 0:
                return {"success": True}
            else:
                # 从stderr中提取错误
                error_lines = result.stderr.split("\n")
                error_msg = next(
                    (line for line in error_lines if "Error" in line or "error" in line),
                    "执行失败",
                )
                return {"success": False, "error": error_msg[:200]}  # Limit error message length
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "执行超时 (>120秒)"}
        except FileNotFoundError:
            return {"success": False, "error": "找不到jupyter命令"}
        except Exception as e:
            return {"success": False, "error": str(e)[:200]}

    def generate_dashboard(self) -> str:
        """生成验证结果的仪表板视图。"""
        if not self.state["notebooks"]:
            return "尚未验证任何笔记本。请先运行验证。"

        total = len(self.state["notebooks"])
        passing = sum(1 for n in self.state["notebooks"].values() if n.get("status") == "pass")

        # 计算百分比
        percentage = (passing / total * 100) if total > 0 else 0

        # 分类问题
        issues_by_type = {}
        for path, data in self.state["notebooks"].items():
            for issue in data.get("issues", []):
                issue_type = issue["type"]
                if issue_type not in issues_by_type:
                    issues_by_type[issue_type] = []
                issues_by_type[issue_type].append((path, issue))

        # 构建仪表板
        dashboard = f"""
📊 笔记本验证仪表板
════════════════════════════════════════════

总体情况：{passing}/{total} 个笔记本通过验证 ({percentage:.1f}%)
"""

        # 添加进度条
        bar_length = 20
        filled = int(bar_length * passing / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)
        dashboard += f"进度：[{bar}]\n"

        # 如果有历史记录，添加趋势
        if len(self.state["history"]) > 1:
            prev = self.state["history"][-2]
            prev_pct = (prev["passing"] / prev["total"] * 100) if prev["total"] > 0 else 0
            change = percentage - prev_pct
            trend = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            dashboard += f"趋势：{trend} {change:+.1f}% 相比上次运行\n"

        dashboard += "\n" + "─" * 45 + "\n"

        # 按严重程度分组问题
        critical_issues = []
        error_issues = []
        warning_issues = []
        info_issues = []

        for issue_type, notebooks in issues_by_type.items():
            for path, issue in notebooks:
                if issue["severity"] == "critical":
                    critical_issues.append((path, issue))
                elif issue["severity"] == "error":
                    error_issues.append((path, issue))
                elif issue["severity"] == "warning":
                    warning_issues.append((path, issue))
                else:
                    info_issues.append((path, issue))

        # 按严重程度显示
        if critical_issues:
            dashboard += f"\n🔴 严重问题 ({len(critical_issues)})\n"
            dashboard += "必须立即修复：\n"
            for path, issue in critical_issues[:5]:
                dashboard += f"  • {Path(path).name}: {issue['type'].replace('_', ' ')}\n"
            if len(critical_issues) > 5:
                dashboard += f"  ...以及另外 {len(critical_issues) - 5} 个\n"

        if error_issues:
            dashboard += f"\n🟠 错误 ({len(error_issues)})\n"
            for path, issue in error_issues[:5]:
                dashboard += f"  • {Path(path).name}: {issue.get('details', issue['type'])[:50]}\n"
            if len(error_issues) > 5:
                dashboard += f"  ...以及另外 {len(error_issues) - 5} 个\n"

        if warning_issues:
            dashboard += f"\n🟡 警告 ({len(warning_issues)})\n"
            # 按类型分组警告
            warning_types = {}
            for path, issue in warning_issues:
                wtype = issue["type"]
                if wtype not in warning_types:
                    warning_types[wtype] = 0
                warning_types[wtype] += 1

            for wtype, count in warning_types.items():
                dashboard += f"  • {wtype.replace('_', ' ').title()}: {count} 个笔记本\n"

        # 添加快速操作
        dashboard += "\n" + "─" * 45 + "\n"
        dashboard += "快速操作：\n"

        if any(i[1]["type"] == "deprecated_model" for i in warning_issues):
            dashboard += "  → 运行 --auto-fix 更新过时模型\n"
        if critical_issues:
            dashboard += "  → 首先修复严重安全问题\n"
        if not os.environ.get("ANTHROPIC_API_KEY"):
            dashboard += "  → 设置 ANTHROPIC_API_KEY 启用执行测试\n"

        return dashboard

    def export_github_issue(self) -> str:
        """将结果导出为GitHub问题markdown。"""
        if not self.state["notebooks"]:
            return "没有可导出的验证结果。请先运行验证。"

        total = len(self.state["notebooks"])
        passing = sum(1 for n in self.state["notebooks"].values() if n.get("status") == "pass")
        percentage = (passing / total * 100) if total > 0 else 0

        # 分组问题
        critical = []
        errors = []
        warnings = []

        for path, data in self.state["notebooks"].items():
            for issue in data.get("issues", []):
                if issue["severity"] == "critical":
                    critical.append((path, issue))
                elif issue["severity"] == "error":
                    errors.append((path, issue))
                elif issue["severity"] == "warning":
                    warnings.append((path, issue))

        # 构建markdown
        markdown = f"""## 📊 笔记本验证报告

**日期：** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**状态：** {passing}/{total} 个笔记本通过验证 ({percentage:.1f}%)
"""

        # Add progress bar
        bar_length = 30
        filled = int(bar_length * passing / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)
        markdown += f"**进度：** `[{bar}]`\n\n"

        # Add history chart if available
        if len(self.state["history"]) > 1:
            markdown += "<details>\n<summary>📈 趋势（最近7次运行）</summary>\n\n```\n"
            for entry in self.state["history"][-7:]:
                pct = (entry["passing"] / entry["total"] * 100) if entry["total"] > 0 else 0
                bar_len = int(pct / 5)  # Scale to 20 chars
                markdown += f"{entry['date']}: {'█' * bar_len:<20} {pct:.1f}% ({entry['passing']}/{entry['total']})\n"
            markdown += "```\n\n</details>\n\n"

        # 严重问题
        if critical:
            markdown += f"### 🔴 严重问题 ({len(critical)})\n"
            markdown += "**必须立即修复** - 安全风险：\n\n"

            for path, issue in critical:
                rel_path = Path(path).relative_to(".") if Path(path).is_absolute() else path
                markdown += f"- [ ] `{rel_path}`\n"
                markdown += f"  - **问题：** {issue['type'].replace('_', ' ').title()}\n"
                markdown += f"  - **单元格：** {issue.get('cell', 'N/A')}\n"
                markdown += f"  - **详情：** {issue.get('details', 'N/A')}\n\n"

        # 错误
        if errors:
            markdown += f"### 🟠 执行错误 ({len(errors)})\n"
            markdown += "无法运行的笔记本：\n\n"

            error_dict = {}
            for path, issue in errors:
                rel_path = str(Path(path).relative_to(".") if Path(path).is_absolute() else path)
                if rel_path not in error_dict:
                    error_dict[rel_path] = []
                error_dict[rel_path].append(issue)

            for path, issues in list(error_dict.items())[:10]:
                markdown += f"- [ ] `{path}`\n"
                for issue in issues:
                    details = issue.get("details", "")
                    if isinstance(details, str) and len(details) > 100:
                        details = details[:100] + "..."
                    markdown += f"  - {details}\n"
                markdown += "\n"

            if len(error_dict) > 10:
                markdown += f"\n*...以及另外 {len(error_dict) - 10} 个有错误的笔记本*\n\n"

        # 警告
        if warnings:
            markdown += f"### 🟡 警告 ({len(warnings)})\n"

            # 按类型分组
            warning_types = {}
            for path, issue in warnings:
                wtype = issue["type"]
                if wtype not in warning_types:
                    warning_types[wtype] = []
                warning_types[wtype].append((path, issue))

            for wtype, items in warning_types.items():
                markdown += f"\n**{wtype.replace('_', ' ').title()} ({len(items)} 个笔记本):**\n\n"

                for path, issue in items[:5]:
                    rel_path = Path(path).relative_to(".") if Path(path).is_absolute() else path
                    markdown += f"- [ ] `{rel_path}`"

                    details = issue.get("details", {})
                    if isinstance(details, dict) and "current" in details:
                        markdown += f" - `{details['current']}` → `{details['suggested']}`"
                    markdown += "\n"

                if len(items) > 5:
                    markdown += f"  - *...以及另外 {len(items) - 5} 个*\n"
                markdown += "\n"

        # 添加修复命令
        markdown += "### 🔧 快速修复命令\n\n```bash\n"
        markdown += "# 自动修复过时模型\n"
        markdown += "python scripts/validate_all_notebooks.py --auto-fix\n\n"
        markdown += "# 运行完整验证\n"
        markdown += "python scripts/validate_all_notebooks.py --full\n\n"
        markdown += "# 生成更新报告\n"
        markdown += "python scripts/validate_all_notebooks.py --export > report.md\n"
        markdown += "```\n"

        return markdown

    def run_validation(self, mode="quick", pattern="**/*.ipynb"):
        """对所有笔记本运行验证。"""
        notebooks = list(Path(".").glob(pattern))
        notebooks = [n for n in notebooks if ".ipynb_checkpoints" not in str(n)]

        if not notebooks:
            print(f"未找到匹配模式的笔记本：{pattern}")
            return

        print(f"\n🔍 在 {mode} 模式下验证 {len(notebooks)} 个笔记本...")
        print("─" * 50)

        failed = []
        warned = []

        for i, notebook in enumerate(notebooks, 1):
            # 检查是否需要重新验证
            nb_stat = notebook.stat()
            nb_mtime = datetime.fromtimestamp(nb_stat.st_mtime).isoformat()

            stored = self.state["notebooks"].get(str(notebook), {})

            # 如果未更改且未强制完整验证，则跳过
            if (
                stored.get("last_modified") == nb_mtime
                and mode == "quick"
                and stored.get("last_validated")
            ):
                status = stored.get("status", "unknown")
                icon = "✅" if status == "pass" else "⚠️" if status == "warning" else "❌"
                print(f"[{i:3}/{len(notebooks)}] {icon} {notebook} (已缓存)")
                if status == "error":
                    failed.append(notebook)
                elif status == "warning":
                    warned.append(notebook)
                continue

            # 验证
            print(f"[{i:3}/{len(notebooks)}] ", end="")
            result = self.validate_notebook(notebook, mode)

            # 存储结果
            self.state["notebooks"][str(notebook)] = {**result, "last_modified": nb_mtime}

            # 显示结果
            if result["status"] == "pass":
                print(f"✅ {notebook}")
            elif result["status"] == "warning":
                print(f"⚠️  {notebook}")
                warned.append(notebook)
                for issue in result["issues"][:2]:  # 显示前2个问题
                    details = issue.get("details", "")
                    if isinstance(details, dict):
                        details = str(details.get("current", details))
                    print(f"     → {issue['type']}: {str(details)[:60]}")
            else:
                print(f"❌ {notebook}")
                failed.append(notebook)
                for issue in result["issues"][:2]:
                    details = issue.get("details", "")
                    if isinstance(details, dict):
                        details = str(details.get("current", details))
                    print(f"     → {issue['type']}: {str(details)[:60]}")

            # 定期保存状态
            if i % 10 == 0:
                self.save_state()

        self.save_state()

        # 摘要
        print("\n" + "═" * 50)
        total = len(notebooks)
        passed = total - len(failed) - len(warned)
        print(f"✅ 通过：{passed}/{total}")
        if warned:
            print(f"⚠️  警告：{len(warned)}/{total}")
        if failed:
            print(f"❌ 失败：{len(failed)}/{total}")

        print(self.generate_dashboard())

    def run_progressive_validation(self):
        """在用户控制下分批运行验证。"""
        notebooks = list(Path(".").glob("**/*.ipynb"))
        notebooks = [n for n in notebooks if ".ipynb_checkpoints" not in str(n)]

        if not notebooks:
            print("未找到笔记本")
            return

        batch_size = 5
        total_batches = (len(notebooks) - 1) // batch_size + 1

        print("\n📚 渐进式验证")
        print(f"总计：{len(notebooks)} 个笔记本分为 {total_batches} 批")
        print("─" * 50)

        for batch_num, i in enumerate(range(0, len(notebooks), batch_size), 1):
            batch = notebooks[i : i + batch_size]
            print(f"\n📦 批次 {batch_num}/{total_batches}")

            batch_failed = []
            batch_warned = []

            for notebook in batch:
                print(f"  正在验证 {notebook}...", end=" ")
                result = self.validate_notebook(notebook, mode="quick")
                self.state["notebooks"][str(notebook)] = result

                if result["status"] == "pass":
                    print("✅")
                elif result["status"] == "warning":
                    print("⚠️")
                    batch_warned.append(notebook)
                    for issue in result["issues"][:1]:
                        print(f"    → {issue['type']}")
                else:
                    print("❌")
                    batch_failed.append(notebook)
                    for issue in result["issues"][:1]:
                        details = issue.get("details", issue["type"])
                        if isinstance(details, dict):
                            details = str(details)
                        print(f"    → {str(details)[:50]}")

            self.save_state()

            # 批次摘要
            if batch_failed or batch_warned:
                print(
                    f"\n  批次摘要：{len(batch_failed)} 个失败，{len(batch_warned)} 个警告"
                )

            # 询问是否继续
            if i + batch_size < len(notebooks):
                print("\n选项：")
                print("  [c] 继续下一批")
                print("  [d] 仪表板 - 显示当前统计")
                print("  [q] 退出并保存进度")

                choice = input("\n选择 (c/d/q): ").strip().lower()

                if choice == "d":
                    print(self.generate_dashboard())
                    input("\n按回车继续...")
                elif choice == "q":
                    print("进度已保存。使用 --resume 继续。")
                    break

    def auto_fix_issues(self):
        """自动修复安全问题，如过时的模型。"""
        print("\n🔧 正在自动修复安全问题...")
        print("─" * 50)

        fixable_notebooks = []

        # Find notebooks with fixable issues
        for path, data in self.state["notebooks"].items():
            if not Path(path).exists():
                continue

            has_deprecated = any(i["type"] == "deprecated_model" for i in data.get("issues", []))
            if has_deprecated:
                fixable_notebooks.append(Path(path))

        if not fixable_notebooks:
            print("未找到可自动修复的问题！")
            return

        print(f"找到 {len(fixable_notebooks)} 个有过时模型的笔记本\n")

        fixed_count = 0
        for notebook_path in fixable_notebooks:
            print(f"正在修复 {notebook_path}...", end=" ")
            if self.fix_deprecated_models(notebook_path):
                print("✅")
                fixed_count += 1
                # Re-validate
                result = self.validate_notebook(notebook_path, mode="quick")
                self.state["notebooks"][str(notebook_path)] = result
            else:
                print("❌ (失败)")

        self.save_state()

        print(f"\n✅ 成功修复了 {fixed_count}/{len(fixable_notebooks)} 个笔记本")

        if fixed_count > 0:
            print("\n重新运行验证以确认所有问题已解决。")

    def fix_deprecated_models(self, notebook_path: Path) -> bool:
        """修复笔记本中的过时模型。"""
        try:
            with open(notebook_path) as f:
                nb = json.load(f)

            replacements = {
                "claude-3-5-sonnet-20240620": "claude-sonnet-4-5",
                "claude-3-5-sonnet-20241022": "claude-sonnet-4-5",
                "claude-3-5-sonnet-latest": "claude-sonnet-4-5",
                "claude-3-haiku-20240307": "claude-haiku-4-5",
                "claude-3-5-haiku-20241022": "claude-haiku-4-5",
                "claude-3-opus-20240229": "claude-opus-4-1",
                "claude-3-opus-latest": "claude-opus-4-1",
                "claude-sonnet-4-20250514": "claude-sonnet-4-5",
                "claude-opus-4-20250514": "claude-opus-4-1",
            }

            modified = False
            for cell in nb.get("cells", []):
                if cell.get("cell_type") == "code":
                    source = cell.get("source", [])
                    new_source = []

                    for line in source:
                        new_line = line
                        for old, new in replacements.items():
                            if old in line:
                                new_line = new_line.replace(old, new)
                                modified = True
                        new_source.append(new_line)

                    if modified:
                        cell["source"] = new_source

            if modified:
                # Save with nice formatting
                with open(notebook_path, "w") as f:
                    json.dump(nb, f, indent=1, ensure_ascii=False)

            return modified

        except Exception as e:
            print(f"错误：{e}")
            return False

    def interactive_menu(self):
        """主交互菜单。"""
        while True:
            print("\n" + "═" * 50)
            print("📓 笔记本验证工具")
            print("═" * 50)
            print("1. 快速扫描（仅结构，已缓存）")
            print("2. 完整验证（包括执行）")
            print("3. 渐进式验证（交互式）")
            print("4. 显示仪表板")
            print("5. 导出GitHub问题")
            print("6. 自动修复过时模型")
            print("7. 验证特定目录")
            print("8. 清除缓存并重新验证")
            print("9. 退出")
            print("─" * 50)

            choice = input("选择选项 (1-9): ").strip()

            if choice == "1":
                self.run_validation(mode="quick")
            elif choice == "2":
                if not os.environ.get("ANTHROPIC_API_KEY"):
                    print(
                        "\n⚠️  警告：未设置 ANTHROPIC_API_KEY。将跳过执行测试。"
                    )
                    cont = input("仍然继续？(y/n): ")
                    if cont.lower() != "y":
                        continue
                self.run_validation(mode="full")
            elif choice == "3":
                self.run_progressive_validation()
            elif choice == "4":
                print(self.generate_dashboard())
            elif choice == "5":
                print("\n" + self.export_github_issue())
                save = input("\n保存到文件？(y/n): ")
                if save.lower() == "y":
                    filename = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
                    with open(filename, "w") as f:
                        f.write(self.export_github_issue())
                    print(f"✅ 已保存到 {filename}")
            elif choice == "6":
                self.auto_fix_issues()
            elif choice == "7":
                directory = input("输入目录路径（例如：skills/): ").strip()
                pattern = (
                    f"{directory}**/*.ipynb"
                    if directory.endswith("/")
                    else f"{directory}/**/*.ipynb"
                )
                self.run_validation(mode="quick", pattern=pattern)
            elif choice == "8":
                self.state = {
                    "version": "1.0",
                    "last_full_run": None,
                    "notebooks": {},
                    "history": self.state.get("history", []),
                    "ignored": {},
                }
                print("缓存已清除！")
                self.run_validation(mode="quick")
            elif choice == "9":
                print("👋 再见！")
                break
            else:
                print("无效选项。请再试一次。")


def main():
    """主入口点。"""
    parser = argparse.ArgumentParser(
        description="验证Jupyter笔记本的常见问题",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  %(prog)s                    # 交互模式
  %(prog)s --quick           # 快速验证（缓存）
  %(prog)s --full            # 完整验证（包括执行）
  %(prog)s --auto-fix        # 修复过时模型
  %(prog)s --export          # 导出GitHub问题markdown
  %(prog)s --dashboard       # 显示验证仪表板
        """,
    )

    parser.add_argument(
        "--quick", action="store_true", help="运行快速验证（仅结构）"
    )
    parser.add_argument("--full", action="store_true", help="运行完整验证（包括执行）")
    parser.add_argument("--dashboard", action="store_true", help="显示验证仪表板")
    parser.add_argument(
        "--export", action="store_true", help="将结果导出为GitHub问题markdown"
    )
    parser.add_argument("--auto-fix", action="store_true", help="自动修复过时模型")
    parser.add_argument("--dir", metavar="PATH", help="验证特定目录")

    args = parser.parse_args()

    validator = NotebookValidator()

    # 处理命令行参数
    if args.quick:
        validator.run_validation(mode="quick")
    elif args.full:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("⚠️  警告：未设置 ANTHROPIC_API_KEY。将跳过执行测试。")
        validator.run_validation(mode="full")
    elif args.dashboard:
        print(validator.generate_dashboard())
    elif args.export:
        print(validator.export_github_issue())
    elif args.auto_fix:
        validator.auto_fix_issues()
    elif args.dir:
        pattern = (
            f"{args.dir}/**/*.ipynb" if not args.dir.endswith("/") else f"{args.dir}**/*.ipynb"
        )
        validator.run_validation(mode="quick", pattern=pattern)
    else:
        # 交互模式
        validator.interactive_menu()


if __name__ == "__main__":
    main()
