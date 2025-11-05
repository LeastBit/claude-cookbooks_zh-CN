"""
内存工具处理程序的单元测试。

测试安全验证、命令执行和错误处理。
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from memory_tool import MemoryToolHandler


class TestMemoryToolHandler(unittest.TestCase):
    """MemoryToolHandler 测试套件。"""

    def setUp(self):
        """为每个测试创建临时目录。"""
        self.test_dir = tempfile.mkdtemp()
        self.handler = MemoryToolHandler(base_path=self.test_dir)

    def tearDown(self):
        """在每个测试后清理临时目录。"""
        shutil.rmtree(self.test_dir)

    # 安全测试

    def test_path_validation_requires_memories_prefix(self):
        """测试路径必须以 /memories 开头。"""
        result = self.handler.execute(command="view", path="/etc/passwd")
        self.assertIn("error", result)
        self.assertIn("must start with /memories", result["error"])

    def test_path_validation_prevents_traversal_dotdot(self):
        """测试阻止 .. 路径遍历。"""
        result = self.handler.execute(command="view", path="/memories/../../../etc/passwd")
        self.assertIn("error", result)
        self.assertIn("escape", result["error"].lower())

    def test_path_validation_prevents_traversal_encoded(self):
        """测试阻止 URL 编码的路径遍历。"""
        result = self.handler.execute(command="view", path="/memories/%2e%2e/%2e%2e/etc/passwd")
        # 路径将被处理并应通过验证失败
        self.assertIn("error", result)

    def test_path_validation_allows_valid_paths(self):
        """测试接受有效的内存路径。"""
        result = self.handler.execute(command="create", path="/memories/test.txt", file_text="test")
        self.assertIn("success", result)

    # 查看命令测试

    def test_view_empty_directory(self):
        """测试查看空的 /memories 目录。"""
        result = self.handler.execute(command="view", path="/memories")
        self.assertIn("success", result)
        self.assertIn("empty", result["success"].lower())

    def test_view_directory_with_files(self):
        """测试查看包含文件的目录。"""
        # 创建一些测试文件
        self.handler.execute(command="create", path="/memories/file1.txt", file_text="content1")
        self.handler.execute(command="create", path="/memories/file2.txt", file_text="content2")

        result = self.handler.execute(command="view", path="/memories")
        self.assertIn("success", result)
        self.assertIn("file1.txt", result["success"])
        self.assertIn("file2.txt", result["success"])

    def test_view_file_with_line_numbers(self):
        """测试查看带行号的文件。"""
        content = "line 1\nline 2\nline 3"
        self.handler.execute(command="create", path="/memories/test.txt", file_text=content)

        result = self.handler.execute(command="view", path="/memories/test.txt")
        self.assertIn("success", result)
        self.assertIn("   1: line 1", result["success"])
        self.assertIn("   2: line 2", result["success"])
        self.assertIn("   3: line 3", result["success"])

    def test_view_file_with_range(self):
        """测试查看特定行范围。"""
        content = "line 1\nline 2\nline 3\nline 4"
        self.handler.execute(command="create", path="/memories/test.txt", file_text=content)

        result = self.handler.execute(command="view", path="/memories/test.txt", view_range=[2, 3])
        self.assertIn("success", result)
        self.assertIn("   2: line 2", result["success"])
        self.assertIn("   3: line 3", result["success"])
        self.assertNotIn("line 1", result["success"])
        self.assertNotIn("line 4", result["success"])

    def test_view_nonexistent_path(self):
        """测试查看不存在的路径。"""
        result = self.handler.execute(command="view", path="/memories/notfound.txt")
        self.assertIn("error", result)
        self.assertIn("not found", result["error"].lower())

    # 创建命令测试

    def test_create_file(self):
        """测试创建文件。"""
        result = self.handler.execute(
            command="create", path="/memories/test.txt", file_text="Hello, World!"
        )
        self.assertIn("success", result)

        # 验证文件存在
        file_path = Path(self.test_dir) / "memories" / "test.txt"
        self.assertTrue(file_path.exists())
        self.assertEqual(file_path.read_text(), "Hello, World!")

    def test_create_file_in_subdirectory(self):
        """测试在子目录中创建文件（自动创建目录）。"""
        result = self.handler.execute(
            command="create",
            path="/memories/subdir/test.txt",
            file_text="Nested content",
        )
        self.assertIn("success", result)

        file_path = Path(self.test_dir) / "memories" / "subdir" / "test.txt"
        self.assertTrue(file_path.exists())

    def test_create_requires_file_extension(self):
        """测试创建只允许文本文件扩展名。"""
        result = self.handler.execute(command="create", path="/memories/noext", file_text="content")
        self.assertIn("error", result)
        self.assertIn("text files are supported", result["error"])

    def test_create_overwrites_existing_file(self):
        """测试创建会覆盖现有文件。"""
        self.handler.execute(command="create", path="/memories/test.txt", file_text="original")
        result = self.handler.execute(
            command="create", path="/memories/test.txt", file_text="updated"
        )
        self.assertIn("success", result)

        file_path = Path(self.test_dir) / "memories" / "test.txt"
        self.assertEqual(file_path.read_text(), "updated")

    # 字符串替换命令测试

    def test_str_replace_success(self):
        """测试成功的字符串替换。"""
        self.handler.execute(
            command="create",
            path="/memories/test.txt",
            file_text="Hello World",
        )

        result = self.handler.execute(
            command="str_replace",
            path="/memories/test.txt",
            old_str="World",
            new_str="Universe",
        )
        self.assertIn("success", result)

        file_path = Path(self.test_dir) / "memories" / "test.txt"
        self.assertEqual(file_path.read_text(), "Hello Universe")

    def test_str_replace_string_not_found(self):
        """测试字符串不存在时的替换。"""
        self.handler.execute(command="create", path="/memories/test.txt", file_text="Hello World")

        result = self.handler.execute(
            command="str_replace",
            path="/memories/test.txt",
            old_str="Missing",
            new_str="Text",
        )
        self.assertIn("error", result)
        self.assertIn("not found", result["error"].lower())

    def test_str_replace_multiple_occurrences(self):
        """测试多个匹配时替换失败。"""
        self.handler.execute(
            command="create",
            path="/memories/test.txt",
            file_text="Hello World Hello World",
        )

        result = self.handler.execute(
            command="str_replace",
            path="/memories/test.txt",
            old_str="Hello",
            new_str="Hi",
        )
        self.assertIn("error", result)
        self.assertIn("appears 2 times", result["error"])

    def test_str_replace_file_not_found(self):
        """测试在不存在的文件上替换。"""
        result = self.handler.execute(
            command="str_replace",
            path="/memories/notfound.txt",
            old_str="old",
            new_str="new",
        )
        self.assertIn("error", result)
        self.assertIn("not found", result["error"].lower())

    # 插入命令测试

    def test_insert_at_beginning(self):
        """测试在第 0 行（开头）插入。"""
        self.handler.execute(
            command="create", path="/memories/test.txt", file_text="line 1\nline 2"
        )

        result = self.handler.execute(
            command="insert",
            path="/memories/test.txt",
            insert_line=0,
            insert_text="new line",
        )
        self.assertIn("success", result)

        file_path = Path(self.test_dir) / "memories" / "test.txt"
        self.assertEqual(file_path.read_text(), "new line\nline 1\nline 2\n")

    def test_insert_in_middle(self):
        """测试在中间插入。"""
        self.handler.execute(
            command="create", path="/memories/test.txt", file_text="line 1\nline 2"
        )

        result = self.handler.execute(
            command="insert",
            path="/memories/test.txt",
            insert_line=1,
            insert_text="inserted",
        )
        self.assertIn("success", result)

        file_path = Path(self.test_dir) / "memories" / "test.txt"
        self.assertEqual(file_path.read_text(), "line 1\ninserted\nline 2\n")

    def test_insert_at_end(self):
        """测试在末尾插入。"""
        self.handler.execute(
            command="create", path="/memories/test.txt", file_text="line 1\nline 2"
        )

        result = self.handler.execute(
            command="insert",
            path="/memories/test.txt",
            insert_line=2,
            insert_text="last line",
        )
        self.assertIn("success", result)

    def test_insert_invalid_line(self):
        """测试使用无效行号插入。"""
        self.handler.execute(command="create", path="/memories/test.txt", file_text="line 1")

        result = self.handler.execute(
            command="insert",
            path="/memories/test.txt",
            insert_line=99,
            insert_text="text",
        )
        self.assertIn("error", result)
        self.assertIn("invalid", result["error"].lower())

    # 删除命令测试

    def test_delete_file(self):
        """测试删除文件。"""
        self.handler.execute(command="create", path="/memories/test.txt", file_text="content")

        result = self.handler.execute(command="delete", path="/memories/test.txt")
        self.assertIn("success", result)

        file_path = Path(self.test_dir) / "memories" / "test.txt"
        self.assertFalse(file_path.exists())

    def test_delete_directory(self):
        """测试删除目录。"""
        self.handler.execute(
            command="create", path="/memories/subdir/test.txt", file_text="content"
        )

        result = self.handler.execute(command="delete", path="/memories/subdir")
        self.assertIn("success", result)

        dir_path = Path(self.test_dir) / "memories" / "subdir"
        self.assertFalse(dir_path.exists())

    def test_delete_cannot_delete_root(self):
        """测试根 /memories 目录不能被删除。"""
        result = self.handler.execute(command="delete", path="/memories")
        self.assertIn("error", result)
        self.assertIn("cannot delete", result["error"].lower())

    def test_delete_nonexistent_path(self):
        """测试删除不存在的路径。"""
        result = self.handler.execute(command="delete", path="/memories/notfound.txt")
        self.assertIn("error", result)
        self.assertIn("not found", result["error"].lower())

    # 重命名命令测试

    def test_rename_file(self):
        """测试重命名文件。"""
        self.handler.execute(command="create", path="/memories/old.txt", file_text="content")

        result = self.handler.execute(
            command="rename", old_path="/memories/old.txt", new_path="/memories/new.txt"
        )
        self.assertIn("success", result)

        old_path = Path(self.test_dir) / "memories" / "old.txt"
        new_path = Path(self.test_dir) / "memories" / "new.txt"
        self.assertFalse(old_path.exists())
        self.assertTrue(new_path.exists())

    def test_rename_to_subdirectory(self):
        """测试将文件移动到子目录。"""
        self.handler.execute(command="create", path="/memories/file.txt", file_text="content")

        result = self.handler.execute(
            command="rename",
            old_path="/memories/file.txt",
            new_path="/memories/subdir/file.txt",
        )
        self.assertIn("success", result)

        new_path = Path(self.test_dir) / "memories" / "subdir" / "file.txt"
        self.assertTrue(new_path.exists())

    def test_rename_source_not_found(self):
        """测试源文件不存在时重命名。"""
        result = self.handler.execute(
            command="rename",
            old_path="/memories/notfound.txt",
            new_path="/memories/new.txt",
        )
        self.assertIn("error", result)
        self.assertIn("not found", result["error"].lower())

    def test_rename_destination_exists(self):
        """测试目标已存在时重命名。"""
        self.handler.execute(command="create", path="/memories/file1.txt", file_text="content1")
        self.handler.execute(command="create", path="/memories/file2.txt", file_text="content2")

        result = self.handler.execute(
            command="rename",
            old_path="/memories/file1.txt",
            new_path="/memories/file2.txt",
        )
        self.assertIn("error", result)
        self.assertIn("already exists", result["error"].lower())

    # 错误处理测试

    def test_unknown_command(self):
        """测试处理未知命令。"""
        result = self.handler.execute(command="invalid", path="/memories")
        self.assertIn("error", result)
        self.assertIn("unknown command", result["error"].lower())

    def test_missing_required_parameters(self):
        """测试缺少参数时的错误处理。"""
        result = self.handler.execute(command="view")
        self.assertIn("error", result)

    # 工具测试

    def test_clear_all_memory(self):
        """测试清除所有内存。"""
        # 创建一些文件
        self.handler.execute(command="create", path="/memories/file1.txt", file_text="content1")
        self.handler.execute(command="create", path="/memories/file2.txt", file_text="content2")

        result = self.handler.clear_all_memory()
        self.assertIn("success", result)

        # 验证目录存在但为空
        memory_root = Path(self.test_dir) / "memories"
        self.assertTrue(memory_root.exists())
        self.assertEqual(len(list(memory_root.iterdir())), 0)


if __name__ == "__main__":
    unittest.main()
