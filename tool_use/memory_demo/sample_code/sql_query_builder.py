"""
带有 SQL 注入漏洞的 SQL 查询构建器。
演示 SQL 查询中的危险字符串格式化。
"""

from typing import List, Optional


class UserDatabase:
    """简单的数据库接口（模拟）。"""

    def execute(self, query: str) -> List[dict]:
        """模拟执行 - 仅返回查询以供检查。"""
        print(f"正在执行: {query}")
        return []


class QueryBuilder:
    """构建用户操作的 SQL 查询。"""

    def __init__(self, db: UserDatabase):
        self.db = db

    def get_user_by_name(self, username: str) -> Optional[dict]:
        """
        通过用户名获取用户。

        错误: SQL 注入漏洞!
        使用用户输入的字符串格式化允许 SQL 注入。
        """
        # 危险: 绝不在用户输入中使用 f 字符串或 % 格式化!
        query = f"SELECT * FROM users WHERE username = '{username}'"
        results = self.db.execute(query)
        return results[0] if results else None

    def get_user_by_name_safe(self, username: str) -> Optional[dict]:
        """使用参数化查询的安全版本。"""
        # 使用参数化查询（这是概念的伪代码）
        query = "SELECT * FROM users WHERE username = ?"
        # 在真实代码中: self.db.execute(query, (username,))
        print(f"带有参数的安全查询: {query}, 参数: ({username},)")
        return None

    def search_users(self, search_term: str, limit: int = 10) -> List[dict]:
        """
        通过术语搜索用户。

        错误: 通过 LIKE 子句的 SQL 注入!
        """
        # 危险: 用户输入直接在 LIKE 子句中
        query = f"SELECT * FROM users WHERE name LIKE '%{search_term}%' LIMIT {limit}"
        return self.db.execute(query)

    def delete_user(self, user_id: str) -> bool:
        """
        删除用户。

        错误: DELETE 语句中的 SQL 注入!
        这特别危险，可能导致数据丢失。
        """
        # 危险: DELETE 中未经验证的用户输入
        query = f"DELETE FROM users WHERE id = {user_id}"
        self.db.execute(query)
        return True

    def get_users_by_role(self, role: str, order_by: str = "name") -> List[dict]:
        """
        通过角色获取用户。

        错误: ORDER BY 子句中的 SQL 注入!
        即使 ORDER BY 子句也可能被利用。
        """
        # 危险: 用户控制的 ORDER BY
        query = f"SELECT * FROM users WHERE role = '{role}' ORDER BY {order_by}"
        return self.db.execute(query)


if __name__ == "__main__":
    db = UserDatabase()
    qb = QueryBuilder(db)

    print("=== 演示 SQL 注入漏洞 ===\n")

    # 示例 1: 基本注入
    print("1. 基本用户名注入:")
    qb.get_user_by_name("admin' OR '1'='1")
    # 执行: SELECT * FROM users WHERE username = 'admin' OR '1'='1'
    # 返回所有用户!

    print("\n2. 搜索术语注入:")
    qb.search_users("test%' OR 1=1--")
    # 可以绕过 LIKE 并返回所有内容

    print("\n3. DELETE 注入:")
    qb.delete_user("1 OR 1=1")
    # 执行: DELETE FROM users WHERE id = 1 OR 1=1
    # 删除所有用户!

    print("\n4. ORDER BY 注入:")
    qb.get_users_by_role("admin", "name; DROP TABLE users--")
    # 可以执行任意 SQL 命令!

    print("\n=== 安全版本 ===")
    qb.get_user_by_name_safe("admin' OR '1'='1")
    # 参数被正确转义
