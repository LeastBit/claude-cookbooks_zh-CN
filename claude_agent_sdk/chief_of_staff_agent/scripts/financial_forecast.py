#!/usr/bin/env python3
"""
财务预测工具 - 用于战略决策的高级财务建模
由首席助理代理通过Bash执行的自定义Python工具
"""

import argparse
import json


def forecast_financials(current_arr, growth_rate, months, burn_rate):
    """生成多场景财务预测"""

    forecasts = {"base_case": [], "optimistic": [], "pessimistic": [], "metrics": {}}

    # 基础情况
    arr = current_arr
    for month in range(1, months + 1):
        arr = arr * (1 + growth_rate)
        monthly_revenue = arr / 12
        net_burn = burn_rate - monthly_revenue
        runway = -1 if net_burn <= 0 else (10_000_000 / net_burn)  # 假设银行有1000万美元

        forecasts["base_case"].append(
            {
                "month": month,
                "arr": round(arr),
                "monthly_revenue": round(monthly_revenue),
                "net_burn": round(net_burn),
                "runway_months": round(runway, 1) if runway > 0 else "infinite",
            }
        )

    # 乐观情况（1.5倍增长）
    arr = current_arr
    for month in range(1, months + 1):
        arr = arr * (1 + growth_rate * 1.5)
        forecasts["optimistic"].append({"month": month, "arr": round(arr)})

    # 悲观情况（0.5倍增长）
    arr = current_arr
    for month in range(1, months + 1):
        arr = arr * (1 + growth_rate * 0.5)
        forecasts["pessimistic"].append({"month": month, "arr": round(arr)})

    # 关键指标
    forecasts["metrics"] = {
        "months_to_profitability": calculate_profitability_date(forecasts["base_case"]),
        "cash_required": calculate_cash_needed(forecasts["base_case"]),
        "break_even_arr": burn_rate * 12,
        "current_burn_multiple": round(burn_rate / (current_arr / 12), 2),
    }

    return forecasts


def calculate_profitability_date(forecast):
    """查找公司何时盈利"""
    for entry in forecast:
        if entry["net_burn"] <= 0:
            return entry["month"]
    return -1  # 在预测期内未盈利


def calculate_cash_needed(forecast):
    """计算到盈利为止所需的现金总额"""
    total_burn = 0
    for entry in forecast:
        if entry["net_burn"] > 0:
            total_burn += entry["net_burn"]
        else:
            break
    return round(total_burn)


def main():
    parser = argparse.ArgumentParser(description="财务预测工具")
    parser.add_argument("--arr", type=float, default=2400000, help="当前ARR")
    parser.add_argument("--growth", type=float, default=0.15, help="月增长率")
    parser.add_argument("--months", type=int, default=12, help="预测期")
    parser.add_argument("--burn", type=float, default=500000, help="月消耗率")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="输出格式")

    args = parser.parse_args()

    forecast = forecast_financials(args.arr, args.growth, args.months, args.burn)

    if args.format == "json":
        print(json.dumps(forecast, indent=2))
    else:
        # 文本输出供人阅读
        print("📊 财务预测")
        print("=" * 50)
        print(f"当前 ARR: ${args.arr:,.0f}")
        print(f"增长率: {args.growth * 100:.1f}% 月度")
        print(f"消耗率: ${args.burn:,.0f}/月")
        print()

        print("基础情况预测:")
        print("-" * 30)
        for i in [2, 5, 11]:  # 显示第3、6、12月
            if i < len(forecast["base_case"]):
                m = forecast["base_case"][i]
                print(f"第{m['month']:2}月: ARR ${m['arr']:,} | 剩余月份 {m['runway_months']}")

        print()
        print("关键指标:")
        print("-" * 30)
        metrics = forecast["metrics"]
        if metrics["months_to_profitability"] > 0:
            print(f"盈利时间: 第{metrics['months_to_profitability']}月")
        else:
            print("盈利时间: 预测期内未实现")
        print(f"所需现金: ${metrics['cash_required']:,}")
        print(f"消耗倍数: {metrics['current_burn_multiple']}x")

        print()
        print("场景分析:")
        print("-" * 30)
        last_base = forecast["base_case"][-1]["arr"]
        last_opt = forecast["optimistic"][-1]["arr"]
        last_pess = forecast["pessimistic"][-1]["arr"]
        print(f"12个月ARR: ${last_pess:,} 到 ${last_opt:,}")
        print(f"范围: {((last_opt - last_pess) / last_base * 100):.0f}% 偏差")


if __name__ == "__main__":
    main()
