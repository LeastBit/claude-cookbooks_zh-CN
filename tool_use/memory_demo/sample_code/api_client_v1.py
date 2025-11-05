"""
带有类似并发问题的异步 API 客户端。
这展示了 Claude 将线程安全模式应用于异步代码。
"""

import asyncio
from typing import List, Dict, Any

import aiohttp


class AsyncAPIClient:
    """用于从多个端点获取数据的异步 API 客户端。"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.responses = []  # 错误: 从多个协程访问共享状态!
        self.error_count = 0  # 错误: 计数器递增的竞态条件!

    async def fetch_endpoint(self, session: aiohttp.ClientSession, endpoint: str) -> Dict[str, Any]:
        """获取单个端点。"""
        url = f"{self.base_url}/{endpoint}"
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                data = await response.json()
                return {
                    "endpoint": endpoint,
                    "status": response.status,
                    "data": data,
                }
        except Exception as e:
            return {
                "endpoint": endpoint,
                "error": str(e),
            }

    async def fetch_all(self, endpoints: List[str]) -> List[Dict[str, Any]]:
        """
        并发获取多个端点。

        错误: 与线程问题类似，多个协程在没有协调的情况下
        修改 self.responses 和 self.error_count!
        虽然 Python 的 GIL 防止了一些线程中的竞态条件，
        异步代码仍然可能有交错问题。
        """
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_endpoint(session, endpoint) for endpoint in endpoints]

            for coro in asyncio.as_completed(tasks):
                result = await coro

                # 竞态条件: 多个协程修改共享状态
                if "error" in result:
                    self.error_count += 1  # 非原子操作!
                else:
                    self.responses.append(result)  # 在异步上下文中非线程安全!

        return self.responses

    def get_summary(self) -> Dict[str, Any]:
        """获取汇总统计。"""
        return {
            "total_responses": len(self.responses),
            "errors": self.error_count,
            "success_rate": (
                len(self.responses) / (len(self.responses) + self.error_count)
                if (len(self.responses) + self.error_count) > 0
                else 0
            ),
        }


async def main():
    """测试异步 API 客户端。"""
    client = AsyncAPIClient("https://jsonplaceholder.typicode.com")

    endpoints = [
        "posts/1",
        "posts/2",
        "posts/3",
        "users/1",
        "users/2",
        "invalid/endpoint",  # 会出错
    ] * 20  # 总共 120 个请求

    results = await client.fetch_all(endpoints)

    print("预期: ~100 个成功响应")
    print(f"得到: {len(results)} 个响应")
    print(f"摘要: {client.get_summary()}")
    print("\n注意: 由于竞态条件，计数可能不正确!")


if __name__ == "__main__":
    asyncio.run(main())
