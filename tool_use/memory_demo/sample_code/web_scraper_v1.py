"""
带有竞态条件错误的多线程网络爬虫。
多个线程在没有同步的情况下修改共享状态。
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

import requests


class WebScraper:
    """并发获取多个 URL 的网络爬虫。"""

    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.results = []  # 错误: 多个线程访问的共享可变状态!
        self.failed_urls = []  # 错误: 另一个竞态条件!

    def fetch_url(self, url: str) -> Dict[str, Any]:
        """获取单个 URL 并返回结果。"""
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return {
                "url": url,
                "status": response.status_code,
                "content_length": len(response.content),
            }
        except requests.exceptions.RequestException as e:
            return {"url": url, "error": str(e)}

    def scrape_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        并发抓取多个 URL。

        错误: self.results 在没有锁的情况下被多个线程访问!
        这会导致结果丢失或损坏的竞态条件。
        """
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.fetch_url, url) for url in urls]

            for future in as_completed(futures):
                result = future.result()

                # 竞态条件: 多个线程同时追加到 self.results
                if "error" in result:
                    self.failed_urls.append(result["url"])  # 竞态条件
                else:
                    self.results.append(result)  # 竞态条件

        return self.results

    def get_stats(self) -> Dict[str, int]:
        """获取抓取统计。"""
        return {
            "total_results": len(self.results),
            "failed_urls": len(self.failed_urls),
            "success_rate": (
                len(self.results) / (len(self.results) + len(self.failed_urls))
                if (len(self.results) + len(self.failed_urls)) > 0
                else 0
            ),
        }


if __name__ == "__main__":
    # 使用多个 URL 进行测试
    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/status/200",
        "https://httpbin.org/status/404",
        "https://httpbin.org/delay/2",
        "https://httpbin.org/status/500",
    ] * 10  # 总共 50 个 URL 以增加竞态条件的概率

    scraper = WebScraper(max_workers=10)
    results = scraper.scrape_urls(urls)

    print("预期: 50 个结果")
    print(f"得到: {len(results)} 个结果")
    print(f"统计: {scraper.get_stats()}")
    print("\n注意: 由于竞态条件，结果数量可能少于预期!")
