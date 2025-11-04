#!/usr/bin/env python3
"""
TechStart Inc 的招聘影响计算器
计算招聘工程师的财务影响
"""

import json
import sys


def calculate_hiring_impact(num_engineers, salary_per_engineer=200000):
    """
    计算招聘工程师的财务影响。

    Args:
        num_engineers: 要招聘的工程师数量
        salary_per_engineer: 每位工程师的年薪（默认：20万美元）

    Returns:
        包含财务影响指标的字典
    """
    # 当前财务数据（来自 CLAUDE.md）
    CURRENT_BURN_MONTHLY = 500000  # 每月50万美元
    CURRENT_RUNWAY_MONTHS = 20  # 20个月
    CASH_IN_BANK = 10000000  # 1000万美元

    # 计算总成本（工资 + 福利 + 税 = 工资 * 1.3）
    annual_loaded_cost_per_engineer = salary_per_engineer * 1.3
    monthly_cost_per_engineer = annual_loaded_cost_per_engineer / 12

    # 总月成本增加
    total_monthly_increase = monthly_cost_per_engineer * num_engineers

    # 新的消耗率
    new_burn_monthly = CURRENT_BURN_MONTHLY + total_monthly_increase

    # 新的剩余月份
    new_runway_months = CASH_IN_BANK / new_burn_monthly
    runway_reduction_months = CURRENT_RUNWAY_MONTHS - new_runway_months

    # 计算潜在收入影响（假设：工程师将速度提高15%）
    velocity_increase = 0.15 * num_engineers / 5  # 假设5名工程师 = 15%的提升

    # 建议
    if runway_reduction_months > 3:
        recommendation = "高风险：剩余月份显著减少。建议考虑分阶段招聘。"
    elif runway_reduction_months > 1.5:
        recommendation = "中等风险：如果收入增长加速则可控。"
    else:
        recommendation = "低风险：对剩余月份影响最小。如果有合适人才可继续。"

    return {
        "num_engineers": num_engineers,
        "salary_per_engineer": salary_per_engineer,
        "monthly_cost_per_engineer": round(monthly_cost_per_engineer, 2),
        "total_monthly_increase": round(total_monthly_increase, 2),
        "current_burn_monthly": CURRENT_BURN_MONTHLY,
        "new_burn_monthly": round(new_burn_monthly, 2),
        "current_runway_months": CURRENT_RUNWAY_MONTHS,
        "new_runway_months": round(new_runway_months, 2),
        "runway_reduction_months": round(runway_reduction_months, 2),
        "velocity_increase_percent": round(velocity_increase * 100, 1),
        "recommendation": recommendation,
    }


def main():
    # 解析命令行参数
    if len(sys.argv) < 2:
        print("用法: python hiring_impact.py <num_engineers> [salary_per_engineer]")
        sys.exit(1)

    num_engineers = int(sys.argv[1])
    salary = int(sys.argv[2]) if len(sys.argv) > 2 else 200000

    # 计算影响
    impact = calculate_hiring_impact(num_engineers, salary)

    # 输出为JSON以便于解析
    print(json.dumps(impact, indent=2))

    # 同时打印摘要
    print("\n=== 招聘影响摘要 ===")
    print(f"招聘 {impact['num_engineers']} 名工程师，年薪 ${impact['salary_per_engineer']:,}")
    print(f"月消耗增加: ${impact['total_monthly_increase']:,.0f}")
    print(f"新消耗率: ${impact['new_burn_monthly']:,.0f}/月")
    print(
        f"剩余月份变化: {impact['current_runway_months']:.1f} → {impact['new_runway_months']:.1f} 月"
    )
    print(f"速度提升: +{impact['velocity_increase_percent']}%")
    print(f"\n{impact['recommendation']}")


if __name__ == "__main__":
    main()
