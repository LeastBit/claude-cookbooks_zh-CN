#!/usr/bin/env python3
"""
简单的脚本，用于演示代理如何使用Bash工具。
计算AI首席助理可能需要的基本指标。
"""

import json
import sys


def calculate_metrics(total_runway, monthly_burn):
    """计算关键财务指标。"""
    runway_months = total_runway / monthly_burn
    quarterly_burn = monthly_burn * 3

    metrics = {
        "monthly_burn": monthly_burn,
        "runway_months": runway_months,
        "total_runway_dollars": total_runway,
        "quarterly_burn": quarterly_burn,
        "burn_rate_daily": round(monthly_burn / 30, 2),
    }

    return metrics


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python simple_calculation.py <total_runway> <monthly_burn>")
        sys.exit(1)

    try:
        runway = float(sys.argv[1])
        burn = float(sys.argv[2])

        results = calculate_metrics(runway, burn)

        print(json.dumps(results, indent=2))

    except ValueError:
        print("错误: 参数必须是数字")
        sys.exit(1)
