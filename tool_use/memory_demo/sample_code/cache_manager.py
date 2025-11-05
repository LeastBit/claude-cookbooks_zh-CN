"""
带有可变默认参数错误的缓存管理器。
这是 Python 最常见的陷阱之一。
"""

from datetime import datetime
from typing import Dict, List, Optional, Any


class CacheManager:
    """管理带有 TTL 支持的缓存数据。"""

    def __init__(self):
        self.cache = {}

    def add_items(
        self,
        key: str,
        items: List[str] = [],  # 错误: 可变默认参数!
    ) -> None:
        """
        向缓存添加项目。

        错误: 使用 [] 作为默认值会在所有调用中创建共享列表!
        这是 Python 的经典陷阱之一。
        """
        # items 列表在所有不提供 items 的调用之间共享
        items.append(f"Added at {datetime.now()}")
        self.cache[key] = items

    def add_items_fixed(self, key: str, items: Optional[List[str]] = None) -> None:
        """使用适当的默认处理添加项目。"""
        if items is None:
            items = []
        items = items.copy()  # 同时创建副本以避免变更
        items.append(f"Added at {datetime.now()}")
        self.cache[key] = items

    def merge_configs(
        self,
        name: str,
        overrides: Dict[str, Any] = {},  # 错误: 可变默认值!
    ) -> Dict[str, Any]:
        """
        合并配置与覆盖值。

        错误: 默认字典在所有调用之间共享!
        """
        defaults = {"timeout": 30, "retries": 3, "cache_enabled": True}

        # 这会修改共享的 overrides 字典
        overrides.update(defaults)
        return overrides

    def merge_configs_fixed(
        self, name: str, overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """正确地合并配置。"""
        if overrides is None:
            overrides = {}

        defaults = {"timeout": 30, "retries": 3, "cache_enabled": True}

        # 创建新字典以避免变更
        result = {**defaults, **overrides}
        return result


class DataProcessor:
    """可变默认错误的另一个示例。"""

    def process_batch(
        self,
        data: List[int],
        filters: List[str] = [],  # 错误: 可变默认值!
    ) -> List[int]:
        """
        使用可选过滤器处理数据。

        错误: filters 列表在调用之间共享!
        """
        filters.append("default_filter")  # 修改共享列表!

        result = []
        for item in data:
            if "positive" in filters and item < 0:
                continue
            result.append(item * 2)
        return result


if __name__ == "__main__":
    cache = CacheManager()

    # 演示错误
    print("=== 演示可变默认参数错误 ===\n")

    # 第一次调用，没有项目
    cache.add_items("key1")
    print(f"key1: {cache.cache['key1']}")

    # 第二次调用，没有项目 - 惊喜! 得到相同的列表
    cache.add_items("key2")
    print(f"key2: {cache.cache['key2']}")  # 会有两个时间戳!

    # 第三次调用 - 更糟!
    cache.add_items("key3")
    print(f"key3: {cache.cache['key3']}")  # 会有三个时间戳!

    print("\n所有键共享同一个列表对象!")
    print(f"key1 is key2: {cache.cache['key1'] is cache.cache['key2']}")

    print("\n=== 使用修复版本 ===\n")
    cache2 = CacheManager()
    cache2.add_items_fixed("key1")
    cache2.add_items_fixed("key2")
    cache2.add_items_fixed("key3")
    print(f"key1: {cache2.cache['key1']}")
    print(f"key2: {cache2.cache['key2']}")
    print(f"key3: {cache2.cache['key3']}")
    print(f"\nkey1 is key2: {cache2.cache['key1'] is cache2.cache['key2']}")
