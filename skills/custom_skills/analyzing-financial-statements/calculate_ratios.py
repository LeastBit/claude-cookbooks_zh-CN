"""
财务比率计算模块。
提供计算关键财务指标和比率的函数。
"""

import json
from typing import Dict, Any


class FinancialRatioCalculator:
    """从财务报表数据计算财务比率。"""

    def __init__(self, financial_data: Dict[str, Any]):
        """
        使用财务报表数据初始化。

        Args:
            financial_data: 包含损益表、资产负债表、现金流量表和市场数据的字典
        """
        self.income_statement = financial_data.get("income_statement", {})
        self.balance_sheet = financial_data.get("balance_sheet", {})
        self.cash_flow = financial_data.get("cash_flow", {})
        self.market_data = financial_data.get("market_data", {})
        self.ratios = {}

    def safe_divide(self, numerator: float, denominator: float, default: float = 0.0) -> float:
        """安全地除两个数，如果分母为零则返回默认值。"""
        if denominator == 0:
            return default
        return numerator / denominator

    def calculate_profitability_ratios(self) -> Dict[str, float]:
        """计算盈利能力比率。"""
        ratios = {}

        # ROE（净资产收益率）
        net_income = self.income_statement.get("net_income", 0)
        shareholders_equity = self.balance_sheet.get("shareholders_equity", 0)
        ratios["roe"] = self.safe_divide(net_income, shareholders_equity)

        # ROA（总资产收益率）
        total_assets = self.balance_sheet.get("total_assets", 0)
        ratios["roa"] = self.safe_divide(net_income, total_assets)

        # 毛利率
        revenue = self.income_statement.get("revenue", 0)
        cogs = self.income_statement.get("cost_of_goods_sold", 0)
        gross_profit = revenue - cogs
        ratios["gross_margin"] = self.safe_divide(gross_profit, revenue)

        # 营业利润率
        operating_income = self.income_statement.get("operating_income", 0)
        ratios["operating_margin"] = self.safe_divide(operating_income, revenue)

        # 净利润率
        ratios["net_margin"] = self.safe_divide(net_income, revenue)

        return ratios

    def calculate_liquidity_ratios(self) -> Dict[str, float]:
        """计算流动性比率。"""
        ratios = {}

        current_assets = self.balance_sheet.get("current_assets", 0)
        current_liabilities = self.balance_sheet.get("current_liabilities", 0)

        # 流动比率
        ratios["current_ratio"] = self.safe_divide(current_assets, current_liabilities)

        # 速动比率（酸性测试）
        inventory = self.balance_sheet.get("inventory", 0)
        quick_assets = current_assets - inventory
        ratios["quick_ratio"] = self.safe_divide(quick_assets, current_liabilities)

        # 现金比率
        cash = self.balance_sheet.get("cash_and_equivalents", 0)
        ratios["cash_ratio"] = self.safe_divide(cash, current_liabilities)

        return ratios

    def calculate_leverage_ratios(self) -> Dict[str, float]:
        """计算杠杆/偿债能力比率。"""
        ratios = {}

        total_debt = self.balance_sheet.get("total_debt", 0)
        shareholders_equity = self.balance_sheet.get("shareholders_equity", 0)

        # 负债权益比
        ratios["debt_to_equity"] = self.safe_divide(total_debt, shareholders_equity)

        # 利息覆盖率
        ebit = self.income_statement.get("ebit", 0)
        interest_expense = self.income_statement.get("interest_expense", 0)
        ratios["interest_coverage"] = self.safe_divide(ebit, interest_expense)

        # 债务服务覆盖率
        net_operating_income = self.income_statement.get("operating_income", 0)
        total_debt_service = interest_expense + self.balance_sheet.get(
            "current_portion_long_term_debt", 0
        )
        ratios["debt_service_coverage"] = self.safe_divide(net_operating_income, total_debt_service)

        return ratios

    def calculate_efficiency_ratios(self) -> Dict[str, float]:
        """计算效率/活动比率。"""
        ratios = {}

        revenue = self.income_statement.get("revenue", 0)
        total_assets = self.balance_sheet.get("total_assets", 0)

        # 资产周转率
        ratios["asset_turnover"] = self.safe_divide(revenue, total_assets)

        # 存货周转率
        cogs = self.income_statement.get("cost_of_goods_sold", 0)
        inventory = self.balance_sheet.get("inventory", 0)
        ratios["inventory_turnover"] = self.safe_divide(cogs, inventory)

        # 应收账款周转率
        accounts_receivable = self.balance_sheet.get("accounts_receivable", 0)
        ratios["receivables_turnover"] = self.safe_divide(revenue, accounts_receivable)

        # 应收账款周转天数
        ratios["days_sales_outstanding"] = self.safe_divide(365, ratios["receivables_turnover"])

        return ratios

    def calculate_valuation_ratios(self) -> Dict[str, float]:
        """计算估值比率。"""
        ratios = {}

        share_price = self.market_data.get("share_price", 0)
        shares_outstanding = self.market_data.get("shares_outstanding", 0)
        market_cap = share_price * shares_outstanding

        # 市盈率
        net_income = self.income_statement.get("net_income", 0)
        eps = self.safe_divide(net_income, shares_outstanding)
        ratios["pe_ratio"] = self.safe_divide(share_price, eps)
        ratios["eps"] = eps

        # 市净率
        book_value = self.balance_sheet.get("shareholders_equity", 0)
        book_value_per_share = self.safe_divide(book_value, shares_outstanding)
        ratios["pb_ratio"] = self.safe_divide(share_price, book_value_per_share)
        ratios["book_value_per_share"] = book_value_per_share

        # 市销率
        revenue = self.income_statement.get("revenue", 0)
        ratios["ps_ratio"] = self.safe_divide(market_cap, revenue)

        # 企业价值倍数
        ebitda = self.income_statement.get("ebitda", 0)
        total_debt = self.balance_sheet.get("total_debt", 0)
        cash = self.balance_sheet.get("cash_and_equivalents", 0)
        enterprise_value = market_cap + total_debt - cash
        ratios["ev_to_ebitda"] = self.safe_divide(enterprise_value, ebitda)

        # PEG比率（如果增长率可用）
        earnings_growth = self.market_data.get("earnings_growth_rate", 0)
        if earnings_growth > 0:
            ratios["peg_ratio"] = self.safe_divide(ratios["pe_ratio"], earnings_growth * 100)

        return ratios

    def calculate_all_ratios(self) -> Dict[str, Any]:
        """计算所有财务比率。"""
        return {
            "profitability": self.calculate_profitability_ratios(),
            "liquidity": self.calculate_liquidity_ratios(),
            "leverage": self.calculate_leverage_ratios(),
            "efficiency": self.calculate_efficiency_ratios(),
            "valuation": self.calculate_valuation_ratios(),
        }

    def interpret_ratio(self, ratio_name: str, value: float) -> str:
        """为特定比率提供解释。"""
        interpretations = {
            "current_ratio": lambda v: (
                "流动性强劲"
                if v > 2
                else "流动性充足"
                if v > 1.5
                else "潜在流动性问题"
                if v > 1
                else "流动性问题"
            ),
            "debt_to_equity": lambda v: (
                "低杠杆"
                if v < 0.5
                else "适度杠杆"
                if v < 1
                else "高杠杆"
                if v < 2
                else "非常高杠杆"
            ),
            "roe": lambda v: (
                "出色的回报"
                if v > 0.20
                else "良好的回报"
                if v > 0.15
                else "平均回报"
                if v > 0.10
                else "低于平均回报"
                if v > 0
                else "负回报"
            ),
            "pe_ratio": lambda v: (
                "可能被低估"
                if 0 < v < 15
                else "公允价值"
                if 15 <= v < 25
                else "增长溢价"
                if 25 <= v < 40
                else "高估值"
                if v >= 40
                else "N/A（负收益）"
                if v <= 0
                else "N/A"
            ),
        }

        if ratio_name in interpretations:
            return interpretations[ratio_name](value)
        return "没有可用的解释"

    def format_ratio(self, name: str, value: float, format_type: str = "ratio") -> str:
        """格式化比率值以便显示。"""
        if format_type == "percentage":
            return f"{value * 100:.2f}%"
        elif format_type == "times":
            return f"{value:.2f}倍"
        elif format_type == "days":
            return f"{value:.1f}天"
        elif format_type == "currency":
            return f"${value:.2f}"
        else:
            return f"{value:.2f}"


def calculate_ratios_from_data(financial_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    从财务数据计算所有比率的主要函数。

    Args:
        financial_data: 包含财务报表数据的字典

    Returns:
        包含计算比率和解释的字典
    """
    calculator = FinancialRatioCalculator(financial_data)
    ratios = calculator.calculate_all_ratios()

    # 添加解释
    interpretations = {}
    for category, category_ratios in ratios.items():
        interpretations[category] = {}
        for ratio_name, value in category_ratios.items():
            interpretations[category][ratio_name] = {
                "value": value,
                "formatted": calculator.format_ratio(ratio_name, value),
                "interpretation": calculator.interpret_ratio(ratio_name, value),
            }

    return {
        "ratios": ratios,
        "interpretations": interpretations,
        "summary": generate_summary(ratios),
    }


def generate_summary(ratios: Dict[str, Any]) -> str:
    """生成财务分析的文本摘要。"""
    summary_parts = []

    # 盈利能力摘要
    prof = ratios.get("profitability", {})
    if prof.get("roe", 0) > 0:
        summary_parts.append(
            f"ROE为{prof['roe'] * 100:.1f}%，表明股东回报{'强劲' if prof['roe'] > 0.15 else '适中'}。"
        )

    # 流动性摘要
    liq = ratios.get("liquidity", {})
    if liq.get("current_ratio", 0) > 0:
        summary_parts.append(
            f"流动比率为{liq['current_ratio']:.2f}，表明流动性{'良好' if liq['current_ratio'] > 1.5 else '存在潜在'}问题。"
        )

    # 杠杆摘要
    lev = ratios.get("leverage", {})
    if lev.get("debt_to_equity", 0) >= 0:
        summary_parts.append(
            f"负债权益比为{lev['debt_to_equity']:.2f}，表明{'保守' if lev['debt_to_equity'] < 0.5 else '适度' if lev['debt_to_equity'] < 1 else '高'}杠杆。"
        )

    # 估值摘要
    val = ratios.get("valuation", {})
    if val.get("pe_ratio", 0) > 0:
        summary_parts.append(
            f"市盈率为{val['pe_ratio']:.1f}，表明该股票交易{'折价' if val['pe_ratio'] < 15 else '公允价值' if val['pe_ratio'] < 25 else '溢价'}。"
        )

    return " ".join(summary_parts) if summary_parts else "数据不足，无法生成摘要。"


# 使用示例
if __name__ == "__main__":
    # 示例财务数据
    sample_data = {
        "income_statement": {
            "revenue": 1000000,
            "cost_of_goods_sold": 600000,
            "operating_income": 200000,
            "ebit": 180000,
            "ebitda": 250000,
            "interest_expense": 20000,
            "net_income": 150000,
        },
        "balance_sheet": {
            "total_assets": 2000000,
            "current_assets": 800000,
            "cash_and_equivalents": 200000,
            "accounts_receivable": 150000,
            "inventory": 250000,
            "current_liabilities": 400000,
            "total_debt": 500000,
            "current_portion_long_term_debt": 50000,
            "shareholders_equity": 1500000,
        },
        "cash_flow": {
            "operating_cash_flow": 180000,
            "investing_cash_flow": -100000,
            "financing_cash_flow": -50000,
        },
        "market_data": {
            "share_price": 50,
            "shares_outstanding": 100000,
            "earnings_growth_rate": 0.10,
        },
    }

    results = calculate_ratios_from_data(sample_data)
    print(json.dumps(results, indent=2))
