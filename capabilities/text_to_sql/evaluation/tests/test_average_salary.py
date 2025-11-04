from utils import extract_sql, execute_sql


def get_assert(output, context):
    sql = extract_sql(output)

    try:
        results = execute_sql(sql)
        execution_success = True
        result_valid = len(results) > 0 and 40000 < results[0][0] < 200000
    except Exception as e:
        execution_success = False
        result_valid = False
        print(f"SQL执行错误: {e}")

    return {
        "pass": execution_success and result_valid,
        "score": 1 if (execution_success and result_valid) else 0,
        "reason": f"SQL{'成功执行并返回有效结果' if (execution_success and result_valid) else '失败或返回无效结果'}。",
    }
