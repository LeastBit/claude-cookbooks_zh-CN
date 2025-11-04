"""
财务比率解释模块。
提供行业基准和背景分析。
"""

from typing import Dict, Any, List, Optional


class RatioInterpreter:
    """使用行业背景解释财务比率。"""

    # 行业基准范围（为演示简化）
    BENCHMARKS = {
        "technology": {
            "current_ratio": {"excellent": 2.5, "good": 1.8, "acceptable": 1.2, "poor": 1.0},
            "debt_to_equity": {"excellent": 0.3, "good": 0.5, "acceptable": 1.0, "poor": 2.0},
            "roe": {"excellent": 0.25, "good": 0.18, "acceptable": 0.12, "poor": 0.08},
            "gross_margin": {"excellent": 0.70, "good": 0.50, "acceptable": 0.35, "poor": 0.20},
            "pe_ratio": {"undervalued": 15, "fair": 25, "growth": 35, "expensive": 50},
        },
        "retail": {
            "current_ratio": {"excellent": 2.0, "good": 1.5, "acceptable": 1.0, "poor": 0.8},
            "debt_to_equity": {"excellent": 0.5, "good": 0.8, "acceptable": 1.5, "poor": 2.5},
            "roe": {"excellent": 0.20, "good": 0.15, "acceptable": 0.10, "poor": 0.05},
            "gross_margin": {"excellent": 0.40, "good": 0.30, "acceptable": 0.20, "poor": 0.10},
            "pe_ratio": {"undervalued": 12, "fair": 18, "growth": 25, "expensive": 35},
        },
        "financial": {
            "current_ratio": {"excellent": 1.5, "good": 1.2, "acceptable": 1.0, "poor": 0.8},
            "debt_to_equity": {"excellent": 1.0, "good": 2.0, "acceptable": 4.0, "poor": 6.0},
            "roe": {"excellent": 0.15, "good": 0.12, "acceptable": 0.08, "poor": 0.05},
            "pe_ratio": {"undervalued": 10, "fair": 15, "growth": 20, "expensive": 30},
        },
        "manufacturing": {
            "current_ratio": {"excellent": 2.2, "good": 1.7, "acceptable": 1.3, "poor": 1.0},
            "debt_to_equity": {"excellent": 0.4, "good": 0.7, "acceptable": 1.2, "poor": 2.0},
            "roe": {"excellent": 0.18, "good": 0.14, "acceptable": 0.10, "poor": 0.06},
            "gross_margin": {"excellent": 0.35, "good": 0.25, "acceptable": 0.18, "poor": 0.12},
            "pe_ratio": {"undervalued": 14, "fair": 20, "growth": 28, "expensive": 40},
        },
        "healthcare": {
            "current_ratio": {"excellent": 2.3, "good": 1.8, "acceptable": 1.4, "poor": 1.0},
            "debt_to_equity": {"excellent": 0.3, "good": 0.6, "acceptable": 1.0, "poor": 1.8},
            "roe": {"excellent": 0.22, "good": 0.16, "acceptable": 0.11, "poor": 0.07},
            "gross_margin": {"excellent": 0.65, "good": 0.45, "acceptable": 0.30, "poor": 0.20},
            "pe_ratio": {"undervalued": 18, "fair": 28, "growth": 40, "expensive": 55},
        },
    }

    def __init__(self, industry: str = "general"):
        """
        使用行业背景初始化解释器。

        Args:
            industry: 用于基准比较的行业部门
        """
        self.industry = industry.lower()
        self.benchmarks = self.BENCHMARKS.get(self.industry, self._get_general_benchmarks())

    def _get_general_benchmarks(self) -> Dict[str, Any]:
        """获取通用的行业无关基准。"""
        return {
            "current_ratio": {"excellent": 2.0, "good": 1.5, "acceptable": 1.0, "poor": 0.8},
            "debt_to_equity": {"excellent": 0.5, "good": 1.0, "acceptable": 1.5, "poor": 2.5},
            "roe": {"excellent": 0.20, "good": 0.15, "acceptable": 0.10, "poor": 0.05},
            "gross_margin": {"excellent": 0.40, "good": 0.30, "acceptable": 0.20, "poor": 0.10},
            "pe_ratio": {"undervalued": 15, "fair": 22, "growth": 30, "expensive": 45},
        }

    def interpret_ratio(self, ratio_name: str, value: float) -> Dict[str, Any]:
        """
        在背景下解释单个比率。

        Args:
            ratio_name: 比率的名称
            value: 计算的比率值

        Returns:
            包含解释详情的字典
        """
        interpretation = {
            "value": value,
            "rating": "N/A",
            "message": "",
            "recommendation": "",
            "benchmark_comparison": {},
        }

        if ratio_name in self.benchmarks:
            benchmark = self.benchmarks[ratio_name]
            interpretation["benchmark_comparison"] = benchmark

            # 基于基准确定评级
            if ratio_name in ["current_ratio", "roe", "gross_margin"]:
                # 越高越好
                if value >= benchmark["excellent"]:
                    interpretation["rating"] = "优秀"
                    interpretation["message"] = (
                        "业绩显著超过行业标准"
                    )
                elif value >= benchmark["good"]:
                    interpretation["rating"] = "良好"
                    interpretation["message"] = (
                        f"在{self.industry}行业中表现优于平均水平"
                    )
                elif value >= benchmark["acceptable"]:
                    interpretation["rating"] = "可接受"
                    interpretation["message"] = "符合行业标准"
                else:
                    interpretation["rating"] = "较差"
                    interpretation["message"] = "低于行业标准 - 需要关注"

            elif ratio_name == "debt_to_equity":
                # 越低越好
                if value <= benchmark["excellent"]:
                    interpretation["rating"] = "优秀"
                    interpretation["message"] = "非常保守的资本结构"
                elif value <= benchmark["good"]:
                    interpretation["rating"] = "良好"
                    interpretation["message"] = "健康的杠杆水平"
                elif value <= benchmark["acceptable"]:
                    interpretation["rating"] = "可接受"
                    interpretation["message"] = "适度杠杆"
                else:
                    interpretation["rating"] = "较差"
                    interpretation["message"] = "高杠杆 - 潜在风险"

            elif ratio_name == "pe_ratio":
                # 取决于背景
                if value > 0:
                    if value < benchmark["undervalued"]:
                        interpretation["rating"] = "可能被低估"
                        interpretation["message"] = (
                            f"交易低于典型的{self.industry}倍数"
                        )
                    elif value < benchmark["fair"]:
                        interpretation["rating"] = "公允价值"
                        interpretation["message"] = "与行业平均水平一致"
                    elif value < benchmark["growth"]:
                        interpretation["rating"] = "增长溢价"
                        interpretation["message"] = "市场定价包含增长预期"
                    else:
                        interpretation["rating"] = "昂贵"
                        interpretation["message"] = "相对于行业估值较高"

        # 添加具体建议
        interpretation["recommendation"] = self._get_recommendation(
            ratio_name, interpretation["rating"]
        )

        return interpretation

    def _get_recommendation(self, ratio_name: str, rating: str) -> str:
        """基于比率和评级生成可操作的建议。"""
        recommendations = {
            "current_ratio": {
                "较差": "考虑改善营运资本管理，减少短期债务或增加流动资产",
                "可接受": "密切监控流动性并考虑建立额外现金储备",
                "良好": "维持当前的流动性管理实践",
                "优秀": "强劲的流动性状况 - 考虑有效利用多余现金",
            },
            "debt_to_equity": {
                "较差": "高杠杆增加财务风险 - 考虑债务减少策略",
                "可接受": "监控债务水平并确保足够的利息覆盖率",
                "良好": "平衡的资本结构 - 维持当前方法",
                "优秀": "保守杠杆 - 可考虑战略性使用债务促进增长",
            },
            "roe": {
                "较差": "专注于提高运营效率和盈利能力",
                "可接受": "探索通过运营改进增强回报的机会",
                "良好": "稳健回报 - 继续当前策略",
                "优秀": "杰出表现 - 确保高回报的可持续性",
            },
            "pe_ratio": {
                "可能被低估": "如果基本面坚实，可能呈现买入机会",
                "公允价值": "相对于同行同业定价合理",
                "增长溢价": "确保增长前景支撑溢价估值",
                "昂贵": "考虑估值风险 - 确保基本面支撑高倍数",
            },
        }

        if ratio_name in recommendations and rating in recommendations[ratio_name]:
            return recommendations[ratio_name][rating]

        return "继续监控该指标"

    def analyze_trend(
        self, ratio_name: str, values: List[float], periods: List[str]
    ) -> Dict[str, Any]:
        """
        分析比率随时间变化的趋势。

        Args:
            ratio_name: 比率的名称
            values: 比率值列表
            periods: 期间标签列表

        Returns:
            趋势分析字典
        """
        if len(values) < 2:
            return {
                "trend": "数据不足",
                "message": "趋势分析至少需要2个期间",
            }

        # 计算趋势
        first_value = values[0]
        last_value = values[-1]
        change = last_value - first_value
        pct_change = (change / abs(first_value)) * 100 if first_value != 0 else 0

        # 确定趋势方向
        if abs(pct_change) < 5:
            trend = "稳定"
        elif pct_change > 0:
            trend = "改善" if ratio_name != "debt_to_equity" else "恶化"
        else:
            trend = "恶化" if ratio_name != "debt_to_equity" else "改善"

        return {
            "trend": trend,
            "change": change,
            "pct_change": pct_change,
            "message": f"{ratio_name}从{periods[0]}到{periods[-1]}{'增加' if change > 0 else '减少'}了{abs(pct_change):.1f}%",
            "values": list(zip(periods, values)),
        }

    def generate_report(self, ratios: Dict[str, Any]) -> str:
        """
        生成全面的解释报告。

        Args:
            ratios: 计算比率的字典

        Returns:
            格式化报告字符串
        """
        report_lines = [
            f"财务分析报告 - {self.industry.title()}行业背景",
            "=" * 70,
            "",
        ]

        for category, category_ratios in ratios.items():
            report_lines.append(f"\n{category.upper()}分析")
            report_lines.append("-" * 40)

            for ratio_name, value in category_ratios.items():
                if isinstance(value, (int, float)):
                    interpretation = self.interpret_ratio(ratio_name, value)
                    report_lines.append(f"\n{ratio_name.replace('_', ' ').title()}:")
                    report_lines.append(f"  数值: {value:.2f}")
                    report_lines.append(f"  评级: {interpretation['rating']}")
                    report_lines.append(f"  分析: {interpretation['message']}")
                    report_lines.append(f"  建议: {interpretation['recommendation']}")

        return "\n".join(report_lines)


def perform_comprehensive_analysis(
    ratios: Dict[str, Any],
    industry: str = "general",
    historical_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    执行包含解释的综合比率分析。

    Args:
        ratios: 计算的财务比率
        industry: 用于基准比较的行业部门
        historical_data: 用于趋势分析的可选历史比率数据

    Returns:
        包含解释和建议的完整分析
    """
    interpreter = RatioInterpreter(industry)
    analysis = {
        "current_analysis": {},
        "trend_analysis": {},
        "overall_health": {},
        "recommendations": [],
    }

    # 分析当前比率
    for category, category_ratios in ratios.items():
        analysis["current_analysis"][category] = {}
        for ratio_name, value in category_ratios.items():
            if isinstance(value, (int, float)):
                analysis["current_analysis"][category][ratio_name] = interpreter.interpret_ratio(
                    ratio_name, value
                )

    # 如果提供历史数据，执行趋势分析
    if historical_data:
        for ratio_name, historical_values in historical_data.items():
            if "values" in historical_values and "periods" in historical_values:
                analysis["trend_analysis"][ratio_name] = interpreter.analyze_trend(
                    ratio_name, historical_values["values"], historical_values["periods"]
                )

        # 生成整体健康状况评估
    analysis["overall_health"] = _assess_overall_health(analysis["current_analysis"])

    # 生成关键建议
    analysis["recommendations"] = _generate_key_recommendations(analysis)

    # 添加格式化报告
    analysis["report"] = interpreter.generate_report(ratios)

    return analysis


def _assess_overall_health(current_analysis: Dict[str, Any]) -> Dict[str, str]:
    """基于比率分析评估整体财务健康状况。"""
    ratings = []
    for category, category_analysis in current_analysis.items():
        for ratio_name, ratio_analysis in category_analysis.items():
            if "rating" in ratio_analysis:
                ratings.append(ratio_analysis["rating"])

    # 简单评分系统
    score_map = {
        "优秀": 4,
        "良好": 3,
        "可接受": 2,
        "较差": 1,
        "公允价值": 3,
        "可能被低估": 3,
        "增长溢价": 2,
        "昂贵": 1,
    }

    scores = [score_map.get(rating, 2) for rating in ratings]
    avg_score = sum(scores) / len(scores) if scores else 0

    if avg_score >= 3.5:
        health = "优秀"
        message = "公司在大多数指标上显示出强劲的财务健康状况"
    elif avg_score >= 2.5:
        health = "良好"
        message = "整体财务状况健康，在某些方面还有改进空间"
    elif avg_score >= 1.5:
        health = "一般"
        message = "财务指标混合 - 在几个方面需要关注"
    else:
        health = "较差"
        message = "存在重大财务挑战，需要立即关注"

    return {"status": health, "message": message, "score": f"{avg_score:.1f}/4.0"}


def _generate_key_recommendations(analysis: Dict[str, Any]) -> List[str]:
    """基于分析生成优先建议。"""
    recommendations = []

    # 检查关键问题
    for category, category_analysis in analysis["current_analysis"].items():
        for ratio_name, ratio_analysis in category_analysis.items():
            if ratio_analysis.get("rating") == "较差":
                recommendations.append(
                    f"优先事项：处理{ratio_name.replace('_', ' ')} - {ratio_analysis.get('recommendation', '')}"
                )

    # 添加基于趋势的建议
    for ratio_name, trend in analysis.get("trend_analysis", {}).items():
        if trend.get("trend") == "恶化":
            recommendations.append(
                f"监控：{ratio_name.replace('_', ' ')}呈现负面趋势"
            )

    # 如果健康状况良好，添加一般建议
    if not recommendations:
        recommendations.append("继续当前的财务管理实践")
        recommendations.append("考虑战略性增长机会")

    return recommendations[:5]  # 返回前5条建议
