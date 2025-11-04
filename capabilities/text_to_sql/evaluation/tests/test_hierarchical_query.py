from utils import extract_sql, execute_sql


def get_assert(output, context):
    sql = extract_sql(output)

    try:
        results = execute_sql(sql)
        execution_success = True
        result_valid = (
            len(results) > 0 and len(results[0]) == 4
        )  # 部门, 员工姓名, 工资, 百分比差异
        if result_valid:
            for row in results:
                if not (isinstance(row[2], (int, float)) and isinstance(row[3], (int, float))):
                    result_valid = False
                    break
    except Exception as e:
        execution_success = False
        result_valid = False
        print(f"SQL执行错误: {e}")

    return {
        "pass": execution_success and result_valid,
        "score": 1 if (execution_success and result_valid) else 0,
        "reason": f"SQL{'成功执行' if execution_success else '执行失败'}。{'获得有效结果' if result_valid else '无效或无结果'}",
    }
