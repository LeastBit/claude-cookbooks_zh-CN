from utils import extract_sql, execute_sql


def get_assert(output, context):
    sql = extract_sql(output)

    try:
        results = execute_sql(sql)
        execution_success = True
        result_valid = (
            len(results) > 0 and len(results[0]) >= 5
        )  # 部门, 预算%, 前几名员工, 他们的工资%, 效率分数
        if result_valid:
            for row in results:
                if not (
                    isinstance(row[1], float) and 0 <= row[1] <= 100 and isinstance(row[-1], float)
                ):
                    result_valid = False
                    break
    except Exception as e:
        execution_success = False
        result_valid = False
        print(f"SQL执行错误: {e}")

    return {
        "pass": execution_success and result_valid,
        "score": 1 if (execution_success and result_valid) else 0,
        "reason": f"SQL{'成功执行' if execution_success else '执行失败'}。{'获得有效的预算分析结果' if result_valid else '无效或不完整的分析结果'}",
    }
