"""
金融模型敏感性分析模块。
测试变量变化对关键输出的影响。
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Callable


class SensitivityAnalyzer:
    """对金融模型执行敏感性分析。"""

    def __init__(self, base_model: Any):
        """
        初始化敏感性分析器。

        Args:
            base_model: 要分析的基准金融模型
        """
        self.base_model = base_model
        self.base_output = None
        self.sensitivity_results = {}

    def one_way_sensitivity(
        self,
        variable_name: str,
        base_value: float,
        range_pct: float,
        steps: int,
        output_func: Callable,
        model_update_func: Callable,
    ) -> pd.DataFrame:
        """
        执行单向敏感性分析。

        Args:
            variable_name: 要测试的变量名称
            base_value: 基准情况值
            range_pct: +/-百分比测试范围
            steps: 范围内的步数
            output_func: 计算输出指标的函数
            model_update_func: 用新值更新模型的函数

        Returns:
            包含敏感性结果的DataFrame
        """
        # 计算范围
        min_val = base_value * (1 - range_pct)
        max_val = base_value * (1 + range_pct)
        test_values = np.linspace(min_val, max_val, steps)

        results = []
        for value in test_values:
            # 更新模型
            model_update_func(value)

            # 计算输出
            output = output_func()

            results.append(
                {
                    "variable": variable_name,
                    "value": value,
                    "pct_change": (value - base_value) / base_value * 100,
                    "output": output,
                    "output_change": output - self.base_output if self.base_output else 0,
                }
            )

        # 重置为基准值
        model_update_func(base_value)

        return pd.DataFrame(results)

    def two_way_sensitivity(
        self,
        var1_name: str,
        var1_base: float,
        var1_range: List[float],
        var2_name: str,
        var2_base: float,
        var2_range: List[float],
        output_func: Callable,
        model_update_func: Callable,
    ) -> pd.DataFrame:
        """
        执行双向敏感性分析。

        Args:
            var1_name: 第一个变量名称
            var1_base: 第一个变量基准值
            var1_range: 第一个变量的数值范围
            var2_name: 第二个变量名称
            var2_base: 第二个变量基准值
            var2_range: 第二个变量的数值范围
            output_func: 计算输出的函数
            model_update_func: 更新模型的函数（接受var1, var2）

        Returns:
            包含双向敏感性表的DataFrame
        """
        results = np.zeros((len(var1_range), len(var2_range)))

        for i, val1 in enumerate(var1_range):
            for j, val2 in enumerate(var2_range):
                # 更新两个变量
                model_update_func(val1, val2)

                # 计算输出
                results[i, j] = output_func()

        # 重置为基准值
        model_update_func(var1_base, var2_base)

        # 创建DataFrame
        df = pd.DataFrame(
            results,
            index=[f"{var1_name}={v:.2%}" if v < 1 else f"{var1_name}={v:.1f}" for v in var1_range],
            columns=[
                f"{var2_name}={v:.2%}" if v < 1 else f"{var2_name}={v:.1f}" for v in var2_range
            ],
        )

        return df

    def tornado_analysis(
        self, variables: Dict[str, Dict[str, Any]], output_func: Callable
    ) -> pd.DataFrame:
        """
        创建龙卷风图数据，显示变量的相对影响。

        Args:
            variables: 包含基准、低值、高值的变量字典
            output_func: 计算输出的函数

        Returns:
            按影响幅度排序的DataFrame
        """
        # 存储基准输出
        self.base_output = output_func()

        tornado_data = []

        for var_name, var_info in variables.items():
            # 测试低值
            var_info["update_func"](var_info["low"])
            low_output = output_func()

            # 测试高值
            var_info["update_func"](var_info["high"])
            high_output = output_func()

            # 重置为基准值
            var_info["update_func"](var_info["base"])

            # 计算影响
            impact = high_output - low_output
            low_delta = low_output - self.base_output
            high_delta = high_output - self.base_output

            tornado_data.append(
                {
                    "variable": var_name,
                    "base_value": var_info["base"],
                    "low_value": var_info["low"],
                    "high_value": var_info["high"],
                    "low_output": low_output,
                    "high_output": high_output,
                    "low_delta": low_delta,
                    "high_delta": high_delta,
                    "impact": abs(impact),
                    "impact_pct": abs(impact) / self.base_output * 100,
                }
            )

        # 按影响排序
        df = pd.DataFrame(tornado_data)
        df = df.sort_values("impact", ascending=False)

        return df

    def scenario_analysis(
        self,
        scenarios: Dict[str, Dict[str, float]],
        variable_updates: Dict[str, Callable],
        output_func: Callable,
        probability_weights: Optional[Dict[str, float]] = None,
    ) -> pd.DataFrame:
        """
        分析具有不同变量组合的多个情景。

        Args:
            scenarios: 包含变量值的情景字典
            variable_updates: 更新每个变量的函数
            output_func: 计算输出的函数
            probability_weights: 每个情景的可选概率

        Returns:
            包含情景结果的DataFrame
        """
        results = []

        for scenario_name, variables in scenarios.items():
            # 更新此情景的所有变量
            for var_name, value in variables.items():
                if var_name in variable_updates:
                    variable_updates[var_name](value)

            # 计算输出
            output = output_func()

            # 如果提供，获取概率
            prob = (
                probability_weights.get(scenario_name, 1 / len(scenarios))
                if probability_weights
                else 1 / len(scenarios)
            )

            results.append(
                {
                    "scenario": scenario_name,
                    "probability": prob,
                    "output": output,
                    **variables,  # 包含所有变量值
                }
            )

            # 重置模型（简化版 - 应恢复所有基准值）

        df = pd.DataFrame(results)

        # 计算期望值
        df["weighted_output"] = df["output"] * df["probability"]
        expected_value = df["weighted_output"].sum()

        # 添加汇总行
        summary = pd.DataFrame(
            [
                {
                    "scenario": "期望值",
                    "probability": 1.0,
                    "output": expected_value,
                    "weighted_output": expected_value,
                }
            ]
        )

        df = pd.concat([df, summary], ignore_index=True)

        return df

    def breakeven_analysis(
        self,
        variable_name: str,
        variable_update: Callable,
        output_func: Callable,
        target_value: float,
        min_search: float,
        max_search: float,
        tolerance: float = 0.01,
    ) -> float:
        """
        找到输出等于目标的盈亏平衡点。

        Args:
            variable_name: 要调整的变量
            variable_update: 更新变量的函数
            output_func: 计算输出的函数
            target_value: 目标输出值
            min_search: 最小搜索范围
            max_search: 最大搜索范围
            tolerance: 收敛容差

        Returns:
            变量的盈亏平衡值
        """
        # 二分搜索求盈亏平衡点
        low = min_search
        high = max_search

        while (high - low) > tolerance:
            mid = (low + high) / 2
            variable_update(mid)
            output = output_func()

            if abs(output - target_value) < tolerance:
                return mid
            elif output < target_value:
                low = mid
            else:
                high = mid

        return (low + high) / 2


def create_data_table(
    row_variable: Tuple[str, List[float], Callable],
    col_variable: Tuple[str, List[float], Callable],
    output_func: Callable,
) -> pd.DataFrame:
    """
    为两个变量创建Excel风格的数据表。

    Args:
        row_variable: (名称, 值, 更新函数)
        col_variable: (名称, 值, 更新函数)
        output_func: 计算输出的函数

    Returns:
        格式化为数据表的DataFrame
    """
    row_name, row_values, row_update = row_variable
    col_name, col_values, col_update = col_variable

    results = np.zeros((len(row_values), len(col_values)))

    for i, row_val in enumerate(row_values):
        for j, col_val in enumerate(col_values):
            row_update(row_val)
            col_update(col_val)
            results[i, j] = output_func()

    df = pd.DataFrame(
        results,
        index=pd.Index(row_values, name=row_name),
        columns=pd.Index(col_values, name=col_name),
    )

    return df


# 使用示例
if __name__ == "__main__":
    # 用于演示的模拟模型
    class SimpleModel:
        def __init__(self):
            self.revenue = 1000
            self.margin = 0.20
            self.multiple = 10

        def calculate_value(self):
            ebitda = self.revenue * self.margin
            return ebitda * self.multiple

    # 创建模型和分析器
    model = SimpleModel()
    analyzer = SensitivityAnalyzer(model)

    # 单向敏感性
    results = analyzer.one_way_sensitivity(
        variable_name="收入",
        base_value=model.revenue,
        range_pct=0.20,
        steps=5,
        output_func=model.calculate_value,
        model_update_func=lambda x: setattr(model, "revenue", x),
    )

    print("单向敏感性分析:")
    print(results)

    # 龙卷风分析
    variables = {
        "收入": {
            "base": 1000,
            "low": 800,
            "high": 1200,
            "update_func": lambda x: setattr(model, "revenue", x),
        },
        "利润率": {
            "base": 0.20,
            "low": 0.15,
            "high": 0.25,
            "update_func": lambda x: setattr(model, "margin", x),
        },
        "倍数": {
            "base": 10,
            "low": 8,
            "high": 12,
            "update_func": lambda x: setattr(model, "multiple", x),
        },
    }

    tornado = analyzer.tornado_analysis(variables, model.calculate_value)
    print("\n龙卷风分析:")
    print(tornado[["variable", "impact", "impact_pct"]])
