from utils import extract_sql, execute_sql


def get_assert(output, context):
    sql = extract_sql(output)

    try:
        results = execute_sql(sql)
        row = results[0] if results else None
        execution_success = True
    except Exception as e:
        execution_success = False
        row = None
        print(f"SQL执行错误: {e}")

    expected_result = {"name": "Julia Clark", "age": 64, "salary": 103699.17}

    if row:
        actual_result = {"name": row[0], "age": row[1], "salary": row[2]}
        data_match = actual_result == expected_result
    else:
        data_match = False

    return {
        "pass": execution_success and data_match,
        "score": 1 if (execution_success and data_match) else 0,
        "reason": f"SQL{'成功执行' if execution_success else '执行失败'}。"
        f"数据{'匹配' if data_match else '不匹配'}预期结果。"
        f"实际: {actual_result if row else '无数据'}, 预期: {expected_result}",
    }
