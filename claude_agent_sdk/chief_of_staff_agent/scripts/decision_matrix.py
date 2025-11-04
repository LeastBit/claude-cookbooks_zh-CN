#!/usr/bin/env python3
"""
决策矩阵工具 - 用于复杂选择的战略决策框架
首席助理代理的自定义Python脚本
"""

import argparse
import json


def create_decision_matrix(options: list[dict], criteria: list[dict]) -> dict:
    """为战略选择创建加权决策矩阵"""

    results = {"options": [], "winner": None, "analysis": {}}

    for option in options:
        option_scores = {
            "name": option["name"],
            "scores": {},
            "weighted_scores": {},
            "total": 0,
            "pros": [],
            "cons": [],
            "verdict": "",
        }

        # 为每个标准计算分数
        for criterion in criteria:
            crit_name = criterion["name"]
            weight = criterion["weight"]

            # 获得此选项在此标准上的分数 (1-10)
            score = option.get(crit_name, 5)
            weighted = score * weight

            option_scores["scores"][crit_name] = score
            option_scores["weighted_scores"][crit_name] = round(weighted, 2)
            option_scores["total"] += weighted

            # 跟踪优缺点
            if score >= 8:
                option_scores["pros"].append(f"优秀的{crit_name}")
            elif score >= 6:
                option_scores["pros"].append(f"良好的{crit_name}")
            elif score <= 3:
                option_scores["cons"].append(f"较差的{crit_name}")
            elif score <= 5:
                option_scores["cons"].append(f"较弱的{crit_name}")

        option_scores["total"] = round(option_scores["total"], 2)

        # 生成结论
        if option_scores["total"] >= 8:
            option_scores["verdict"] = "强烈推荐"
        elif option_scores["total"] >= 6.5:
            option_scores["verdict"] = "推荐"
        elif option_scores["total"] >= 5:
            option_scores["verdict"] = "可接受"
        else:
            option_scores["verdict"] = "不推荐"

        results["options"].append(option_scores)

    # 找到获胜者
    results["options"].sort(key=lambda x: x["total"], reverse=True)
    results["winner"] = results["options"][0]["name"]

    # 生成分析
    results["analysis"] = generate_analysis(results["options"])

    return results


def generate_analysis(options: list[dict]) -> dict:
    """生成决策的战略分析"""

    analysis = {
        "clear_winner": False,
        "margin": 0,
        "recommendation": "",
        "key_differentiators": [],
        "risks": [],
    }

    if len(options) >= 2:
        margin = options[0]["total"] - options[1]["total"]
        analysis["margin"] = round(margin, 2)
        analysis["clear_winner"] = margin > 1.5

        if analysis["clear_winner"]:
            analysis["recommendation"] = (
                f"强烈推荐{options[0]['name']}，领先{margin:.1f}分"
            )
        elif margin > 0.5:
            analysis["recommendation"] = (
                f"推荐{options[0]['name']}，但可考虑{options[1]['name']}作为可行替代方案"
            )
        else:
            analysis["recommendation"] = (
                f"{options[0]['name']}和{options[1]['name']}之间难分伯仲 - 需考虑其他因素"
            )

        # 找到关键差异化因素
        top = options[0]
        for criterion in top["scores"]:
            if top["scores"][criterion] >= 8:
                analysis["key_differentiators"].append(criterion)

        # 识别风险
        if top["total"] < 6:
            analysis["risks"].append("总分低于推荐阈值")
        if len(top["cons"]) > len(top["pros"]):
            analysis["risks"].append("缺点多于优点")

    return analysis


def main():
    parser = argparse.ArgumentParser(description="战略决策矩阵工具")
    parser.add_argument("--scenario", type=str, help="预定义场景")
    parser.add_argument("--input", type=str, help="包含选项和标准的JSON文件")
    parser.add_argument("--format", choices=["json", "text"], default="text")

    args = parser.parse_args()

    # 默认场景：自主开发 vs 购买 vs 合作
    if args.scenario == "build-buy-partner":
        options = [
            {
                "name": "自主开发",
                "cost": 3,  # 1-10，分数越高越好（所以3 = 高成本）
                "time_to_market": 2,  # 2 = 慢
                "control": 10,  # 10 = 完全控制
                "quality": 8,  # 8 = 高质量潜力
                "scalability": 9,  # 9 = 非常可扩展
                "risk": 3,  # 3 = 高风险
            },
            {
                "name": "购买解决方案",
                "cost": 5,
                "time_to_market": 9,
                "control": 4,
                "quality": 7,
                "scalability": 6,
                "risk": 7,
            },
            {
                "name": "战略合作",
                "cost": 7,
                "time_to_market": 7,
                "control": 6,
                "quality": 7,
                "scalability": 8,
                "risk": 5,
            },
        ]

        criteria = [
            {"name": "cost", "weight": 0.20},
            {"name": "time_to_market", "weight": 0.25},
            {"name": "control", "weight": 0.15},
            {"name": "quality", "weight": 0.20},
            {"name": "scalability", "weight": 0.10},
            {"name": "risk", "weight": 0.10},
        ]
    elif args.input:
        with open(args.input) as f:
            data = json.load(f)
            options = data["options"]
            criteria = data["criteria"]
    else:
        # 默认招聘场景
        options = [
            {
                "name": "招聘3名高级工程师",
                "cost": 4,
                "productivity": 9,
                "time_to_impact": 8,
                "team_growth": 7,
                "runway_impact": 3,
            },
            {
                "name": "招聘5名初级工程师",
                "cost": 7,
                "productivity": 5,
                "time_to_impact": 4,
                "team_growth": 9,
                "runway_impact": 5,
            },
        ]
        criteria = [
            {"name": "cost", "weight": 0.25},
            {"name": "productivity", "weight": 0.30},
            {"name": "time_to_impact", "weight": 0.20},
            {"name": "team_growth", "weight": 0.15},
            {"name": "runway_impact", "weight": 0.10},
        ]

    matrix = create_decision_matrix(options, criteria)

    if args.format == "json":
        print(json.dumps(matrix, indent=2))
    else:
        # 文本输出
        print("🎯 战略决策矩阵")
        print("=" * 60)

        print("\n评估的选项:")
        for i, opt in enumerate(matrix["options"], 1):
            print(f"\n{i}. {opt['name']}")
            print("-" * 40)
            print(f"   总分: {opt['total']}/10 - {opt['verdict']}")

            print("   优势:")
            for pro in opt["pros"][:3]:
                print(f"   ✓ {pro}")

            if opt["cons"]:
                print("   劣势:")
                for con in opt["cons"][:3]:
                    print(f"   ✗ {con}")

        print("\n" + "=" * 60)
        print("建议:")
        print("-" * 40)
        analysis = matrix["analysis"]
        print(f"获胜者: {matrix['winner']}")
        print(f"领先分数: {analysis['margin']} 分")
        print(f"\n{analysis['recommendation']}")

        if analysis["key_differentiators"]:
            print(f"\n关键优势: {', '.join(analysis['key_differentiators'])}")

        if analysis["risks"]:
            print("\n⚠️  需要考虑的风险:")
            for risk in analysis["risks"]:
                print(f"   - {risk}")


if __name__ == "__main__":
    main()
