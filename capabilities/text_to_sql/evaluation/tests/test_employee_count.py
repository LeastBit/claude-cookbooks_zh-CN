from utils import extract_sql, execute_sql


def get_assert(output, context):
    sql = extract_sql(output)

    try:
        results = execute_sql(sql)
        count = results[0][0] if results else 0
        execution_success = True
    except Exception as e:
        execution_success = False
        count = 0
        print(f"SQL执行错误: {e}")

    expected_count = 20

    return {
        "pass": execution_success and count == expected_count,
        "score": 1 if (execution_success and count == expected_count) else 0,
        "reason": f"SQL{'成功执行' if execution_success else '执行失败'}。"
        f"返回计数: {count}, 预期计数: {expected_count}。",
    }
