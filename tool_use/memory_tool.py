"""
适用于Claude的memory_20250818工具的生产就绪记忆工具处理器。

此实现提供安全的客户端记忆操作执行，包括路径验证、错误处理和全面的安全措施。
"""

import shutil
from pathlib import Path
from typing import Any


class MemoryToolHandler:
    """
    处理Claude的记忆工具命令执行。

    记忆工具使Claude能够通过标准化工具接口在记忆系统中读取、写入和管理文件。
    此处理器提供带有安全控制的客户端实现。

    属性:
        base_path: 记忆存储的根目录
        memory_root: base_path内的/memories目录
    """

    def __init__(self, base_path: str = "./memory_storage"):
        """
        初始化记忆工具处理器。

        参数:
            base_path: 所有记忆操作的根目录
        """
        self.base_path = Path(base_path).resolve()
        self.memory_root = self.base_path / "memories"
        self.memory_root.mkdir(parents=True, exist_ok=True)

    def _validate_path(self, path: str) -> Path:
        """
        验证并解析记忆路径以防止目录遍历攻击。

        参数:
            path: 要验证的路径（必须以/memories开头）

        返回:
            memory_root内的解析绝对路径对象

        异常:
            ValueError: 如果路径无效或尝试逃逸记忆目录
        """
        if not path.startswith("/memories"):
            raise ValueError(
                f"Path must start with /memories, got: {path}. "
                "All memory operations must be confined to the /memories directory."
            )

        # 移除/memories前缀和任何前导斜杠
        relative_path = path[len("/memories") :].lstrip("/")

        # 解析为memory_root内的绝对路径
        if relative_path:
            full_path = (self.memory_root / relative_path).resolve()
        else:
            full_path = self.memory_root.resolve()

        # 验证解析的路径仍在memory_root内
        try:
            full_path.relative_to(self.memory_root.resolve())
        except ValueError as e:
            raise ValueError(
                f"Path '{path}' would escape /memories directory. "
                "Directory traversal attempts are not allowed."
            ) from e

        return full_path

    def execute(self, **params: Any) -> dict[str, str]:
        """
        执行记忆工具命令。

        参数:
            **params: 来自Claude工具使用的命令参数

        返回:
            包含'success'或'error'键的字典

        支持的命令:
            - view: 显示目录内容或文件内容
            - create: 创建或覆盖文件
            - str_replace: 替换文件中的文本
            - insert: 在特定行插入文本
            - delete: 删除文件或目录
            - rename: 重命名或移动文件/目录
        """
        command = params.get("command")

        try:
            if command == "view":
                return self._view(params)
            elif command == "create":
                return self._create(params)
            elif command == "str_replace":
                return self._str_replace(params)
            elif command == "insert":
                return self._insert(params)
            elif command == "delete":
                return self._delete(params)
            elif command == "rename":
                return self._rename(params)
            else:
                return {
                    "error": f"Unknown command: '{command}'. "
                    "Valid commands are: view, create, str_replace, insert, delete, rename"
                }
        except ValueError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": f"Unexpected error executing {command}: {e}"}

    def _view(self, params: dict[str, Any]) -> dict[str, str]:
        """查看目录内容或文件内容。"""
        path = params.get("path")
        view_range = params.get("view_range")

        if not path:
            return {"error": "Missing required parameter: path"}

        full_path = self._validate_path(path)

        # 处理目录列表
        if full_path.is_dir():
            try:
                items = []
                for item in sorted(full_path.iterdir()):
                    if item.name.startswith("."):
                        continue
                    items.append(f"{item.name}/" if item.is_dir() else item.name)

                if not items:
                    return {"success": f"Directory: {path}\n(empty)"}

                return {
                    "success": f"Directory: {path}\n" + "\n".join([f"- {item}" for item in items])
                }
            except Exception as e:
                return {"error": f"Cannot read directory {path}: {e}"}

        # 处理文件读取
        elif full_path.is_file():
            try:
                content = full_path.read_text(encoding="utf-8")
                lines = content.splitlines()

                # 如果指定了查看范围，则应用它
                if view_range:
                    start_line = max(1, view_range[0]) - 1  # 转换为0索引
                    end_line = len(lines) if view_range[1] == -1 else view_range[1]
                    lines = lines[start_line:end_line]
                    start_num = start_line + 1
                else:
                    start_num = 1

                # 格式化为带行号
                numbered_lines = [f"{i + start_num:4d}: {line}" for i, line in enumerate(lines)]
                return {"success": "\n".join(numbered_lines)}

            except UnicodeDecodeError:
                return {"error": f"Cannot read {path}: File is not valid UTF-8 text"}
            except Exception as e:
                return {"error": f"Cannot read file {path}: {e}"}

        else:
            return {"error": f"Path not found: {path}"}

    def _create(self, params: dict[str, Any]) -> dict[str, str]:
        """创建或覆盖文件。"""
        path = params.get("path")
        file_text = params.get("file_text", "")

        if not path:
            return {"error": "Missing required parameter: path"}

        full_path = self._validate_path(path)

        # 不允许直接创建目录
        if not path.endswith((".txt", ".md", ".json", ".py", ".yaml", ".yml")):
            return {
                "error": f"Cannot create {path}: Only text files are supported. "
                "Use file extensions: .txt, .md, .json, .py, .yaml, .yml"
            }

        try:
            # 如果需要，创建父目录
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # 写入文件
            full_path.write_text(file_text, encoding="utf-8")
            return {"success": f"File created successfully at {path}"}

        except Exception as e:
            return {"error": f"Cannot create file {path}: {e}"}

    def _str_replace(self, params: dict[str, Any]) -> dict[str, str]:
        """替换文件中的文本。"""
        path = params.get("path")
        old_str = params.get("old_str")
        new_str = params.get("new_str", "")

        if not path or old_str is None:
            return {"error": "Missing required parameters: path, old_str"}

        full_path = self._validate_path(path)

        if not full_path.is_file():
            return {"error": f"File not found: {path}"}

        try:
            content = full_path.read_text(encoding="utf-8")

            # 检查old_str是否存在
            count = content.count(old_str)
            if count == 0:
                return {
                    "error": f"String not found in {path}. The exact text must exist in the file."
                }
            elif count > 1:
                return {
                    "error": f"String appears {count} times in {path}. "
                    "The string must be unique. Use more specific context."
                }

            # 执行替换
            new_content = content.replace(old_str, new_str, 1)
            full_path.write_text(new_content, encoding="utf-8")

            return {"success": f"File {path} has been edited successfully"}

        except Exception as e:
            return {"error": f"Cannot edit file {path}: {e}"}

    def _insert(self, params: dict[str, Any]) -> dict[str, str]:
        """在特定行插入文本。"""
        path = params.get("path")
        insert_line = params.get("insert_line")
        insert_text = params.get("insert_text", "")

        if not path or insert_line is None:
            return {"error": "Missing required parameters: path, insert_line"}

        full_path = self._validate_path(path)

        if not full_path.is_file():
            return {"error": f"File not found: {path}"}

        try:
            lines = full_path.read_text(encoding="utf-8").splitlines()

            # 验证插入行
            if insert_line < 0 or insert_line > len(lines):
                return {
                    "error": f"Invalid insert_line {insert_line}. "
                    f"Must be between 0 and {len(lines)}"
                }

            # 插入文本
            lines.insert(insert_line, insert_text.rstrip("\n"))

            # 写回
            full_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

            return {"success": f"Text inserted at line {insert_line} in {path}"}

        except Exception as e:
            return {"error": f"Cannot insert into {path}: {e}"}

    def _delete(self, params: dict[str, Any]) -> dict[str, str]:
        """删除文件或目录。"""
        path = params.get("path")

        if not path:
            return {"error": "Missing required parameter: path"}

        # 防止删除根记忆目录
        if path == "/memories":
            return {"error": "Cannot delete the /memories directory itself"}

        full_path = self._validate_path(path)

        # 验证路径在/memories内，以防止在记忆目录外意外删除
        # 这提供了超出_validate_path的额外安全检查
        try:
            full_path.relative_to(self.memory_root.resolve())
        except ValueError:
            return {
                "error": f"Invalid operation: Path '{path}' is not within /memories directory. "
                "Only paths within /memories can be deleted."
            }

        if not full_path.exists():
            return {"error": f"Path not found: {path}"}

        try:
            if full_path.is_file():
                full_path.unlink()
                return {"success": f"File deleted: {path}"}
            elif full_path.is_dir():
                shutil.rmtree(full_path)
                return {"success": f"Directory deleted: {path}"}

        except Exception as e:
            return {"error": f"Cannot delete {path}: {e}"}

    def _rename(self, params: dict[str, Any]) -> dict[str, str]:
        """重命名或移动文件/目录。"""
        old_path = params.get("old_path")
        new_path = params.get("new_path")

        if not old_path or not new_path:
            return {"error": "Missing required parameters: old_path, new_path"}

        old_full_path = self._validate_path(old_path)
        new_full_path = self._validate_path(new_path)

        if not old_full_path.exists():
            return {"error": f"Source path not found: {old_path}"}

        if new_full_path.exists():
            return {
                "error": f"Destination already exists: {new_path}. "
                "Cannot overwrite existing files/directories."
            }

        try:
            # 如果需要，创建父目录
            new_full_path.parent.mkdir(parents=True, exist_ok=True)

            # 执行重命名/移动
            old_full_path.rename(new_full_path)

            return {"success": f"Renamed {old_path} to {new_path}"}

        except Exception as e:
            return {"error": f"Cannot rename {old_path} to {new_path}: {e}"}

    def clear_all_memory(self) -> dict[str, str]:
        """
        清除所有记忆文件（对测试或重新开始有用）。

        ⚠️ 警告：此方法仅用于演示和测试目的。
        在生产环境中，您应该仔细考虑是否需要删除
        所有记忆文件，因为这将永久删除所有学到的模式
        和存储的知识。考虑改用选择性删除。

        返回:
            带有成功消息的字典
        """
        try:
            if self.memory_root.exists():
                shutil.rmtree(self.memory_root)
            self.memory_root.mkdir(parents=True, exist_ok=True)
            return {"success": "All memory cleared successfully"}
        except Exception as e:
            return {"error": f"Cannot clear memory: {e}"}
