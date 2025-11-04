import sqlite3

DATABASE_PATH = "../data/data.db"


def get_schema_info():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    schema_info = []

    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for (table_name,) in tables:
        # 获取此表的列
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        table_info = f"表: {table_name}\n"
        table_info += "\n".join(f"  - {col[1]} ({col[2]})" for col in columns)
        schema_info.append(table_info)

    conn.close()
    return "\n\n".join(schema_info)


def generate_prompt(context):
    user_query = context["vars"]["user_query"]
    schema = get_schema_info()
    return f"""
    您是一个将自然语言查询转换为SQL的AI助手。
    给定以下SQL数据库架构：

    {schema}

    将以下自然语言查询转换为SQL：

    {user_query}

    请在回复中仅提供SQL查询，并使用<sql>标签括起来。
    """


def generate_prompt_with_examples(context):
    user_query = context["vars"]["user_query"]
    examples = """
        示例1:
        <query>列出人力资源部门的所有员工。</query>
        <output>SELECT e.name FROM employees e JOIN departments d ON e.department_id = d.id WHERE d.name = 'HR';</output>

        示例2:
        用户：工程部门员工的平均工资是多少？
        SQL: SELECT AVG(e.salary) FROM employees e JOIN departments d ON e.department_id = d.id WHERE d.name = 'Engineering';

        示例3:
        用户：谁是最年长的员工？
        SQL: SELECT name, age FROM employees ORDER BY age DESC LIMIT 1;
    """

    schema = get_schema_info()

    return f"""
        您是一个将自然语言查询转换为SQL的AI助手。
        给定以下SQL数据库架构：

        <schema>
        {schema}
        </schema>

        以下是一些自然语言查询及其对应的SQL的示例：

        <examples>
        {examples}
        </examples>

        现在，将以下自然语言查询转换为SQL：
        <query>
        {user_query}
        </query>

        请在回复中仅提供SQL查询，并使用<sql>标签括起来。
    """


def generate_prompt_with_cot(context):
    user_query = context["vars"]["user_query"]
    schema = get_schema_info()
    examples = """
    <example>
    <query>列出人力资源部门的所有员工。</query>
    <thought_process>
    1. 我们需要连接employees和departments表。
    2. 我们将employees.department_id与departments.id匹配。
    3. 我们将过滤人力资源部门。
    4. 我们只需要返回员工姓名。
    </thought_process>
    <sql>SELECT e.name FROM employees e JOIN departments d ON e.department_id = d.id WHERE d.name = 'HR';</sql>
    </example>

    <example>
    <query>2022年雇用的员工平均工资是多少？</query>
    <thought_process>
    1. 我们需要使用employees表。
    2. 我们需要过滤2022年雇用的员工。
    3. 我们将使用YEAR函数从hire_date中提取年份。
    4. 我们将计算过滤行的salary列的平均值。
    </thought_process>
    <sql>SELECT AVG(salary) FROM employees WHERE YEAR(hire_date) = 2022;</sql>
    </example>
    """

    return f"""您是一个将自然语言查询转换为SQL的AI助手。
    给定以下SQL数据库架构：

    <schema>
    {schema}
    </schema>

    以下是一些自然语言查询、思考过程及其对应的SQL的示例：

    <examples>
    {examples}
    </examples>

    现在，将以下自然语言查询转换为SQL：
    <query>
    {user_query}
    </query>

    在<thought_process>标签内，解释您创建SQL查询的思考过程。
    然后，在<sql>标签内，提供您的输出SQL查询。
    """


def generate_prompt_with_rag(context):
    from vectordb import VectorDB

    # 加载向量数据库
    vectordb = VectorDB()
    vectordb.load_db()

    user_query = context["vars"]["user_query"]

    if not vectordb.embeddings:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            schema_data = [
                {
                    "text": f"表: {table[0]}, 列: {col[1]}, 类型: {col[2]}",
                    "metadata": {"table": table[0], "column": col[1], "type": col[2]},
                }
                for table in cursor.fetchall()
                for col in cursor.execute(f"PRAGMA table_info({table[0]})").fetchall()
            ]
        vectordb.load_data(schema_data)

    relevant_schema = vectordb.search(user_query, k=10, similarity_threshold=0.3)
    schema_info = "\n".join(
        [
            f"表: {item['metadata']['table']}, 列: {item['metadata']['column']}, 类型: {item['metadata']['type']}"
            for item in relevant_schema
        ]
    )

    examples = """
    <example>
    <query>列出人力资源部门的所有员工。</query>
    <thought_process>
    1. 我们需要连接employees和departments表。
    2. 我们将employees.department_id与departments.id匹配。
    3. 我们将过滤人力资源部门。
    4. 我们只需要返回员工姓名。
    </thought_process>
    <sql>SELECT e.name FROM employees e JOIN departments d ON e.department_id = d.id WHERE d.name = 'HR';</sql>
    </example>

    <example>
    <query>2022年雇用的员工平均工资是多少？</query>
    <thought_process>
    1. 我们需要使用employees表。
    2. 我们需要过滤2022年雇用的员工。
    3. 我们将使用YEAR函数从hire_date中提取年份。
    4. 我们将计算过滤行的salary列的平均值。
    </thought_process>
    <sql>SELECT AVG(salary) FROM employees WHERE YEAR(hire_date) = 2022;</sql>
    </example>
    """

    return f"""您是一个将自然语言查询转换为SQL的AI助手。
    给定以下SQL数据库架构的相关列：

    <schema>
    {schema_info}
    </schema>

    以下是一些自然语言查询、思考过程及其对应的SQL的示例：

    <examples>
    {examples}
    </examples>

    现在，将以下自然语言查询转换为SQL：
    <query>
    {user_query}
    </query>

    首先，在<thought_process>标签内提供您的思考过程，解释您将如何创建SQL查询。考虑以下步骤：
    1. 从提供的架构中识别相关的表和列。
    2. 确定表之间任何必要的连接。
    3. 识别任何过滤条件。
    4. 确定适当的聚合或计算。
    5. 逻辑地构建查询。

    然后，在<sql>标签内，提供您的输出SQL查询。

    确保您的SQL查询与SQLite语法兼容，并且仅使用架构中提供的表和列。
    如果您对特定表或列不确定，请使用提供的架构中可用的信息。
    """
