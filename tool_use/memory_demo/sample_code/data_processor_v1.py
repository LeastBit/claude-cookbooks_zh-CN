"""
带有多个并发和线程安全问题的数据处理器。
用于会话 3，以演示带有多个错误的上下文编辑。
"""

import json
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Dict, Any


class DataProcessor:
    """并发处理数据文件，存在各种线程安全问题。"""

    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.processed_count = 0  # 错误: 计数器的竞态条件
        self.results = []  # 错误: 无锁的共享列表
        self.errors = {}  # 错误: 无锁的共享字典
        self.lock = threading.Lock()  # 可用但未使用!

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """处理单个文件。"""
        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            # 模拟一些处理
            processed = {
                "file": file_path,
                "record_count": len(data) if isinstance(data, list) else 1,
                "size_bytes": Path(file_path).stat().st_size,
            }

            return processed

        except Exception as e:
            return {"file": file_path, "error": str(e)}

    def process_batch(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        并发处理多个文件。

        多个错误:
        1. self.processed_count 在无锁的情况下递增
        2. self.results 从多个线程追加
        3. self.errors 从多个线程修改
        4. 我们有锁但不使用它!
        """
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.process_file, fp) for fp in file_paths]

            for future in futures:
                result = future.result()

                # 竞态条件: 无锁递增计数器
                self.processed_count += 1  # 错误!

                if "error" in result:
                    # 竞态条件: 无锁修改字典
                    self.errors[result["file"]] = result["error"]  # 错误!
                else:
                    # 竞态条件: 无锁追加到列表
                    self.results.append(result)  # 错误!

        return self.results

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取处理统计。

        错误: 访问共享状态而未确保线程安全。
        如果在处理过程中调用，可能得到不一致的值。
        """
        total_files = self.processed_count
        successful = len(self.results)
        failed = len(self.errors)

        # 错误: 由于竞态条件，这些计数可能不正确
        return {
            "total_processed": total_files,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total_files if total_files > 0 else 0,
        }

    def reset(self):
        """
        重置处理器状态。

        错误: 无锁 - 如果在处理过程中调用，会导致损坏。
        """
        self.processed_count = 0  # 竞态条件
        self.results = []  # 竞态条件
        self.errors = {}  # 竞态条件


class SharedCache:
    """
    一个带有线程安全问题的共享缓存。

    错误: 经典的读-修改-写竞态条件模式。
    """

    def __init__(self):
        self.cache = {}  # 错误: 无锁的共享字典
        self.hit_count = 0  # 错误: 竞态条件
        self.miss_count = 0  # 错误: 竞态条件

    def get(self, key: str) -> Any:
        """从缓存获取 - 命中/未命中计数的竞态条件。"""
        if key in self.cache:
            self.hit_count += 1  # 错误: 非原子操作!
            return self.cache[key]
        else:
            self.miss_count += 1  # 错误: 非原子操作!
            return None

    def set(self, key: str, value: Any):
        """在缓存中设置 - 字典修改的竞态条件。"""
        self.cache[key] = value  # 错误: 字典访问未同步!

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计 - 可能不一致。"""
        total = self.hit_count + self.miss_count
        return {
            "hits": self.hit_count,
            "misses": self.miss_count,
            "hit_rate": self.hit_count / total if total > 0 else 0,
        }


if __name__ == "__main__":
    # 创建一些测试文件（未包含）
    processor = DataProcessor(max_workers=10)

    # 模拟处理许多文件
    file_paths = [f"data/file_{i}.json" for i in range(100)]

    print("正在并发处理文件...")
    results = processor.process_batch(file_paths)

    print(f"\n统计: {processor.get_statistics()}")
    print("\n注意: 由于竞态条件，计数可能不一致!")
