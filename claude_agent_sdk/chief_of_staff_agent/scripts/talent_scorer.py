#!/usr/bin/env python3
"""
人才评分工具 - 基于多个标准评估和排名候选人
招聘子代理的自定义Python工具
"""

import argparse
import json


def score_candidate(candidate: dict) -> dict:
    """基于加权标准给候选人评分"""

    weights = {
        "technical_skills": 0.30,
        "experience_years": 0.20,
        "startup_experience": 0.15,
        "education": 0.10,
        "culture_fit": 0.15,
        "salary_fit": 0.10,
    }

    scores = {}

    # 技术技能 (0-100)
    tech_match = candidate.get("tech_skills_match", 70)
    scores["technical_skills"] = min(100, tech_match)

    # 经验 (0-100，8年时达到峰值)
    years = candidate.get("years_experience", 5)
    if years <= 2:
        scores["experience_years"] = 40
    elif years <= 5:
        scores["experience_years"] = 70
    elif years <= 8:
        scores["experience_years"] = 90
    else:
        scores["experience_years"] = 85  # 对于资历过高者略降

    # 初创公司经验 (0-100)
    scores["startup_experience"] = 100 if candidate.get("has_startup_exp", False) else 50

    # 教育背景 (0-100)
    education = candidate.get("education", "bachelors")
    edu_scores = {"high_school": 40, "bachelors": 70, "masters": 85, "phd": 90}
    scores["education"] = edu_scores.get(education, 70)

    # 文化契合度 (0-100)
    scores["culture_fit"] = candidate.get("culture_score", 75)

    # 薪资匹配度 (0-100，过高或过低都扣分)
    salary = candidate.get("salary_expectation", 150000)
    target = candidate.get("target_salary", 160000)
    diff_pct = abs(salary - target) / target
    scores["salary_fit"] = max(0, 100 - (diff_pct * 200))

    # 计算加权总分
    total = sum(scores[k] * weights[k] for k in weights)

    return {
        "name": candidate.get("name", "Unknown"),
        "total_score": round(total, 1),
        "scores": scores,
        "recommendation": get_recommendation(total),
        "risk_factors": identify_risks(candidate, scores),
    }


def get_recommendation(score: float) -> str:
    """根据分数生成招聘建议"""
    if score >= 85:
        return "强烈推荐 - 立即发放offer"
    elif score >= 75:
        return "推荐 - 不错的候选人，可以发放offer"
    elif score >= 65:
        return "考虑 - 如果没有更好选择可考虑"
    elif score >= 50:
        return "不推荐 - 存在重大担忧，可能拒绝"
    else:
        return "不招聘 - 不符合要求"


def identify_risks(candidate: dict, scores: dict) -> list[str]:
    """识别潜在风险因素"""
    risks = []

    if scores["technical_skills"] < 60:
        risks.append("技术技能低于要求")

    if candidate.get("years_experience", 0) < 2:
        risks.append("经验有限，需要指导")

    if not candidate.get("has_startup_exp", False):
        risks.append("无初创公司经验，可能难以应对不确定性")

    if scores["salary_fit"] < 50:
        risks.append("薪资期望不匹配")

    if candidate.get("notice_period_days", 14) > 30:
        risks.append(f"通知期过长: {candidate.get('notice_period_days')} 天")

    return risks


def rank_candidates(candidates: list[dict]) -> list[dict]:
    """对多个候选人排名"""
    scored = [score_candidate(c) for c in candidates]
    return sorted(scored, key=lambda x: x["total_score"], reverse=True)


def main():
    parser = argparse.ArgumentParser(description="候选人评分工具")
    parser.add_argument("--input", type=str, help="包含候选人数据的JSON文件")
    parser.add_argument("--name", type=str, help="候选人姓名")
    parser.add_argument("--years", type=int, default=5, help="工作年限")
    parser.add_argument("--tech-match", type=int, default=70, help="技术技能匹配度 (0-100)")
    parser.add_argument("--salary", type=int, default=150000, help="薪资期望")
    parser.add_argument("--startup", action="store_true", help="有初创公司经验")
    parser.add_argument("--format", choices=["json", "text"], default="text")

    args = parser.parse_args()

    if args.input:
        # 从文件对多个候选人评分
        with open(args.input) as f:
            candidates = json.load(f)
        results = rank_candidates(candidates)
    else:
        # 从参数对单个候选人评分
        candidate = {
            "name": args.name or "候选人",
            "years_experience": args.years,
            "tech_skills_match": args.tech_match,
            "salary_expectation": args.salary,
            "has_startup_exp": args.startup,
            "target_salary": 160000,
            "culture_score": 75,
            "education": "bachelors",
        }
        results = [score_candidate(candidate)]

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        # 文本输出
        print("🎯 候选人评估")
        print("=" * 50)

        for i, result in enumerate(results, 1):
            print(f"\n#{i}. {result['name']}")
            print("-" * 30)
            print(f"总分: {result['total_score']}/100")
            print(f"建议: {result['recommendation']}")

            print("\n各项评分:")
            for category, score in result["scores"].items():
                category_map = {
                    "technical_skills": "技术技能",
                    "experience_years": "工作年限",
                    "startup_experience": "初创经验",
                    "education": "教育背景",
                    "culture_fit": "文化契合",
                    "salary_fit": "薪资匹配"
                }
                print(f"  {category_map.get(category, category)}: {score:.0f}/100")

            if result["risk_factors"]:
                print("\n⚠️  风险因素:")
                for risk in result["risk_factors"]:
                    print(f"  - {risk}")

        if len(results) > 1:
            print("\n" + "=" * 50)
            print("排名摘要:")
            for i, r in enumerate(results[:3], 1):
                print(
                    f"{i}. {r['name']}: {r['total_score']:.1f} - {r['recommendation'].split(' - ')[0]}"
                )


if __name__ == "__main__":
    main()
