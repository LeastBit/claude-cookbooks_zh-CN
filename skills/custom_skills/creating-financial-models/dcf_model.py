"""
现金流折现（DCF）估值模型。
使用自由现金流预测实现企业估值。
"""

import numpy as np
from typing import Dict, List, Any, Optional


class DCFModel:
    """构建和计算DCF估值模型。"""

    def __init__(self, company_name: str = "公司"):
        """
        初始化DCF模型。

        Args:
            company_name: 被估值公司的名称
        """
        self.company_name = company_name
        self.historical_financials = {}
        self.projections = {}
        self.assumptions = {}
        self.wacc_components = {}
        self.valuation_results = {}

    def set_historical_financials(
        self,
        revenue: List[float],
        ebitda: List[float],
        capex: List[float],
        nwc: List[float],
        years: List[int],
    ):
        """
        设置历史财务数据。

        Args:
            revenue: 历史收入
            ebitda: 历史EBITDA
            capex: 历史资本支出
            nwc: 历史营运资本
            years: 历史年份
        """
        self.historical_financials = {
            "years": years,
            "revenue": revenue,
            "ebitda": ebitda,
            "capex": capex,
            "nwc": nwc,
            "ebitda_margin": [ebitda[i] / revenue[i] for i in range(len(revenue))],
            "capex_percent": [capex[i] / revenue[i] for i in range(len(revenue))],
        }

    def set_assumptions(
        self,
        projection_years: int = 5,
        revenue_growth: List[float] = None,
        ebitda_margin: List[float] = None,
        tax_rate: float = 0.25,
        capex_percent: List[float] = None,
        nwc_percent: List[float] = None,
        terminal_growth: float = 0.03,
    ):
        """
        设置预测假设。

        Args:
            projection_years: 预测年数
            revenue_growth: 年度收入增长率
            ebitda_margin: 各年EBITDA利润率
            tax_rate: 企业税率
            capex_percent: 资本支出占收入百分比
            nwc_percent: 营运资本占收入百分比
            terminal_growth: 终值增长率
        """
        if revenue_growth is None:
            revenue_growth = [0.10] * projection_years  # 默认10%增长

        if ebitda_margin is None:
            # 如果可用，使用历史平均值
            if self.historical_financials:
                avg_margin = np.mean(self.historical_financials["ebitda_margin"])
                ebitda_margin = [avg_margin] * projection_years
            else:
                ebitda_margin = [0.20] * projection_years  # 默认20%利润率

        if capex_percent is None:
            capex_percent = [0.05] * projection_years  # 默认收入的5%

        if nwc_percent is None:
            nwc_percent = [0.10] * projection_years  # 默认收入的10%

        self.assumptions = {
            "projection_years": projection_years,
            "revenue_growth": revenue_growth,
            "ebitda_margin": ebitda_margin,
            "tax_rate": tax_rate,
            "capex_percent": capex_percent,
            "nwc_percent": nwc_percent,
            "terminal_growth": terminal_growth,
        }

    def calculate_wacc(
        self,
        risk_free_rate: float,
        beta: float,
        market_premium: float,
        cost_of_debt: float,
        debt_to_equity: float,
        tax_rate: Optional[float] = None,
    ) -> float:
        """
        计算加权平均资本成本（WACC）。

        Args:
            risk_free_rate: 无风险利率（例如，10年期国债）
            beta: 权益贝塔
            market_premium: 权益市场风险溢价
            cost_of_debt: 税前债务成本
            debt_to_equity: 债务股权比
            tax_rate: 税率（如果未提供则使用假设值）

        Returns:
            WACC（小数形式）
        """
        if tax_rate is None:
            tax_rate = self.assumptions.get("tax_rate", 0.25)

        # 使用CAPM计算权益成本
        cost_of_equity = risk_free_rate + beta * market_premium

        # 计算权重
        equity_weight = 1 / (1 + debt_to_equity)
        debt_weight = debt_to_equity / (1 + debt_to_equity)

        # 计算WACC
        wacc = equity_weight * cost_of_equity + debt_weight * cost_of_debt * (1 - tax_rate)

        self.wacc_components = {
            "risk_free_rate": risk_free_rate,
            "beta": beta,
            "market_premium": market_premium,
            "cost_of_equity": cost_of_equity,
            "cost_of_debt": cost_of_debt,
            "debt_to_equity": debt_to_equity,
            "equity_weight": equity_weight,
            "debt_weight": debt_weight,
            "tax_rate": tax_rate,
            "wacc": wacc,
        }

        return wacc

    def project_cash_flows(self) -> Dict[str, List[float]]:
        """
        基于假设预测未来现金流。

        Returns:
            包含预测财务数据的字典
        """
        years = self.assumptions["projection_years"]

        # 如果可用，从最后的历史收入开始
        if self.historical_financials and "revenue" in self.historical_financials:
            base_revenue = self.historical_financials["revenue"][-1]
        else:
            base_revenue = 1000  # 默认基准

        projections = {
            "year": list(range(1, years + 1)),
            "revenue": [],
            "ebitda": [],
            "ebit": [],
            "tax": [],
            "nopat": [],
            "capex": [],
            "nwc_change": [],
            "fcf": [],
        }

        prev_revenue = base_revenue
        prev_nwc = base_revenue * 0.10  # 初始营运资本假设

        for i in range(years):
            # 收入
            revenue = prev_revenue * (1 + self.assumptions["revenue_growth"][i])
            projections["revenue"].append(revenue)

            # EBITDA
            ebitda = revenue * self.assumptions["ebitda_margin"][i]
            projections["ebitda"].append(ebitda)

            # EBIT（为简单起见，假设折旧=资本支出）
            depreciation = revenue * self.assumptions["capex_percent"][i]
            ebit = ebitda - depreciation
            projections["ebit"].append(ebit)

            # 税费
            tax = ebit * self.assumptions["tax_rate"]
            projections["tax"].append(tax)

            # NOPAT
            nopat = ebit - tax
            projections["nopat"].append(nopat)

            # 资本支出
            capex = revenue * self.assumptions["capex_percent"][i]
            projections["capex"].append(capex)

            # 营运资本变化
            nwc = revenue * self.assumptions["nwc_percent"][i]
            nwc_change = nwc - prev_nwc
            projections["nwc_change"].append(nwc_change)

            # 自由现金流
            fcf = nopat + depreciation - capex - nwc_change
            projections["fcf"].append(fcf)

            prev_revenue = revenue
            prev_nwc = nwc

        self.projections = projections
        return projections

    def calculate_terminal_value(
        self, method: str = "growth", exit_multiple: Optional[float] = None
    ) -> float:
        """
        使用永续增长法或退出倍数法计算终值。

        Args:
            method: 'growth'表示永续增长法，'multiple'表示退出倍数法
            exit_multiple: EV/EBITDA退出倍数（如果使用倍数法）

        Returns:
            终值
        """
        if not self.projections:
            raise ValueError("必须先预测现金流")

        if method == "growth":
            # 戈登增长模型
            final_fcf = self.projections["fcf"][-1]
            terminal_growth = self.assumptions["terminal_growth"]
            wacc = self.wacc_components["wacc"]

            # 终值年度的FCF
            terminal_fcf = final_fcf * (1 + terminal_growth)

            # 终值
            terminal_value = terminal_fcf / (wacc - terminal_growth)

        elif method == "multiple":
            if exit_multiple is None:
                exit_multiple = 10  # 默认EV/EBITDA倍数

            final_ebitda = self.projections["ebitda"][-1]
            terminal_value = final_ebitda * exit_multiple

        else:
            raise ValueError("方法必须为'growth'或'multiple'")

        return terminal_value

    def calculate_enterprise_value(
        self, terminal_method: str = "growth", exit_multiple: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        通过贴现现金流计算企业价值。

        Args:
            terminal_method: 终值计算方法
            exit_multiple: 使用倍数法时的退出倍数

        Returns:
            估值结果字典
        """
        if not self.projections:
            self.project_cash_flows()

        if "wacc" not in self.wacc_components:
            raise ValueError("必须先计算WACC")

        wacc = self.wacc_components["wacc"]
        years = self.assumptions["projection_years"]

        # 计算预测现金流的现值
        pv_fcf = []
        for i, fcf in enumerate(self.projections["fcf"]):
            discount_factor = (1 + wacc) ** (i + 1)
            pv = fcf / discount_factor
            pv_fcf.append(pv)

        total_pv_fcf = sum(pv_fcf)

        # 计算终值
        terminal_value = self.calculate_terminal_value(terminal_method, exit_multiple)

        # 贴现终值
        terminal_discount = (1 + wacc) ** years
        pv_terminal = terminal_value / terminal_discount

        # 企业价值
        enterprise_value = total_pv_fcf + pv_terminal

        self.valuation_results = {
            "enterprise_value": enterprise_value,
            "pv_fcf": total_pv_fcf,
            "pv_terminal": pv_terminal,
            "terminal_value": terminal_value,
            "terminal_method": terminal_method,
            "pv_fcf_detail": pv_fcf,
            "terminal_percent": pv_terminal / enterprise_value * 100,
        }

        return self.valuation_results

    def calculate_equity_value(
        self, net_debt: float, cash: float = 0, shares_outstanding: float = 100
    ) -> Dict[str, Any]:
        """
        从企业价值计算股权价值。

        Args:
            net_debt: 债务总额减去现金
            cash: 现金及等价物（如果不是净额）
            shares_outstanding: 发行股数（百万股）

        Returns:
            股权估值指标
        """
        if "enterprise_value" not in self.valuation_results:
            raise ValueError("必须先计算企业价值")

        ev = self.valuation_results["enterprise_value"]

        # 股权价值 = EV - 净债务
        equity_value = ev - net_debt + cash

        # 每股价值
        value_per_share = equity_value / shares_outstanding if shares_outstanding > 0 else 0

        equity_results = {
            "equity_value": equity_value,
            "shares_outstanding": shares_outstanding,
            "value_per_share": value_per_share,
            "net_debt": net_debt,
            "cash": cash,
        }

        self.valuation_results.update(equity_results)
        return equity_results

    def sensitivity_analysis(
        self, variable1: str, range1: List[float], variable2: str, range2: List[float]
    ) -> np.ndarray:
        """
        对估值进行双向敏感性分析。

        Args:
            variable1: 要测试的第一个变量（'wacc'、'growth'、'margin'）
            range1: 第一个变量的数值范围
            variable2: 要测试的第二个变量
            range2: 第二个变量的数值范围

        Returns:
            估值的二维数组
        """
        results = np.zeros((len(range1), len(range2)))

        # 存储原始值
        orig_wacc = self.wacc_components.get("wacc", 0.10)
        orig_growth = self.assumptions.get("terminal_growth", 0.03)
        orig_margin = self.assumptions.get("ebitda_margin", [0.20] * 5)

        for i, val1 in enumerate(range1):
            for j, val2 in enumerate(range2):
                # 更新第一个变量
                if variable1 == "wacc":
                    self.wacc_components["wacc"] = val1
                elif variable1 == "growth":
                    self.assumptions["terminal_growth"] = val1
                elif variable1 == "margin":
                    self.assumptions["ebitda_margin"] = [val1] * len(orig_margin)

                # 更新第二个变量
                if variable2 == "wacc":
                    self.wacc_components["wacc"] = val2
                elif variable2 == "growth":
                    self.assumptions["terminal_growth"] = val2
                elif variable2 == "margin":
                    self.assumptions["ebitda_margin"] = [val2] * len(orig_margin)

                # 重新计算
                self.project_cash_flows()
                valuation = self.calculate_enterprise_value()
                results[i, j] = valuation["enterprise_value"]

        # 恢复原始值
        self.wacc_components["wacc"] = orig_wacc
        self.assumptions["terminal_growth"] = orig_growth
        self.assumptions["ebitda_margin"] = orig_margin

        return results

    def generate_summary(self) -> str:
        """
        生成估值结果的文本摘要。

        Returns:
            格式化的摘要字符串
        """
        if not self.valuation_results:
            return "没有可用的估值结果。请先运行估值。"

        summary = [
            f"DCF估值摘要 - {self.company_name}",
            "=" * 50,
            "",
            "关键假设:",
            f"  预测期: {self.assumptions['projection_years']} 年",
            f"  收入增长: {np.mean(self.assumptions['revenue_growth']) * 100:.1f}% 平均",
            f"  EBITDA利润率: {np.mean(self.assumptions['ebitda_margin']) * 100:.1f}% 平均",
            f"  终值增长: {self.assumptions['terminal_growth'] * 100:.1f}%",
            f"  WACC: {self.wacc_components['wacc'] * 100:.1f}%",
            "",
            "估值结果:",
            f"  企业价值: ${self.valuation_results['enterprise_value']:,.0f}百万",
            f"    FCF现值: ${self.valuation_results['pv_fcf']:,.0f}百万",
            f"    终值现值: ${self.valuation_results['pv_terminal']:,.0f}百万",
            f"    终值占比: {self.valuation_results['terminal_percent']:.1f}%",
            "",
        ]

        if "equity_value" in self.valuation_results:
            summary.extend(
                [
                    "股权估值:",
                    f"  股权价值: ${self.valuation_results['equity_value']:,.0f}百万",
                    f"  发行股数: {self.valuation_results['shares_outstanding']:.0f}百万",
                    f"  每股价值: ${self.valuation_results['value_per_share']:.2f}",
                    "",
                ]
            )

        return "\n".join(summary)


# 常见计算的辅助函数


def calculate_beta(stock_returns: List[float], market_returns: List[float]) -> float:
    """
    从收益序列计算贝塔。

    Args:
        stock_returns: 历史股票收益
        market_returns: 历史市场收益

    Returns:
        贝塔系数
    """
    covariance = np.cov(stock_returns, market_returns)[0, 1]
    market_variance = np.var(market_returns)
    beta = covariance / market_variance if market_variance != 0 else 1.0
    return beta


def calculate_fcf_cagr(fcf_series: List[float]) -> float:
    """
    计算FCF的复合年增长率。

    Args:
        fcf_series: 自由现金流时间序列

    Returns:
        CAGR（小数形式）
    """
    if len(fcf_series) < 2:
        return 0

    years = len(fcf_series) - 1
    if fcf_series[0] <= 0 or fcf_series[-1] <= 0:
        return 0

    cagr = (fcf_series[-1] / fcf_series[0]) ** (1 / years) - 1
    return cagr


# 使用示例
if __name__ == "__main__":
    # 创建模型
    model = DCFModel("科技公司")

    # 设置历史数据
    model.set_historical_financials(
        revenue=[800, 900, 1000],
        ebitda=[160, 189, 220],
        capex=[40, 45, 50],
        nwc=[80, 90, 100],
        years=[2022, 2023, 2024],
    )

    # 设置假设
    model.set_assumptions(
        projection_years=5,
        revenue_growth=[0.15, 0.12, 0.10, 0.08, 0.06],
        ebitda_margin=[0.23, 0.24, 0.25, 0.25, 0.25],
        tax_rate=0.25,
        terminal_growth=0.03,
    )

    # 计算WACC
    model.calculate_wacc(
        risk_free_rate=0.04, beta=1.2, market_premium=0.07, cost_of_debt=0.05, debt_to_equity=0.5
    )

    # 预测现金流
    model.project_cash_flows()

    # 计算估值
    model.calculate_enterprise_value()

    # 计算股权价值
    model.calculate_equity_value(net_debt=200, shares_outstanding=50)

    # 打印摘要
    print(model.generate_summary())
