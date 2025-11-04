#!/usr/bin/env python3
"""
品牌验证脚本
根据品牌指南验证内容，包括颜色、字体、语调和消息。
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict


@dataclass
class BrandGuidelines:
    """品牌指南配置"""

    brand_name: str
    primary_colors: List[str]
    secondary_colors: List[str]
    fonts: List[str]
    tone_keywords: List[str]
    prohibited_words: List[str]
    tagline: Optional[str] = None
    logo_usage_rules: Optional[Dict] = None


@dataclass
class ValidationResult:
    """品牌验证结果"""

    passed: bool
    score: float
    violations: List[str]
    warnings: List[str]
    suggestions: List[str]


class BrandValidator:
    """根据品牌指南验证内容"""

    def __init__(self, guidelines: BrandGuidelines):
        self.guidelines = guidelines

    def validate_colors(self, content: str) -> Tuple[List[str], List[str]]:
        """
        验证内容中的颜色使用（十六进制代码、RGB、颜色名称）
        Returns: (violations, warnings)
        """
        violations = []
        warnings = []

        # 查找十六进制颜色
        hex_pattern = r"#[0-9A-Fa-f]{6}|#[0-9A-Fa-f]{3}"
        found_colors = re.findall(hex_pattern, content)

        # 查找RGB颜色
        rgb_pattern = r"rgb\s*\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*\)"
        found_colors.extend(re.findall(rgb_pattern, content, re.IGNORECASE))

        approved_colors = self.guidelines.primary_colors + self.guidelines.secondary_colors

        for color in found_colors:
            if color.upper() not in [c.upper() for c in approved_colors]:
                violations.append(f"使用了未批准的颜色: {color}")

        return violations, warnings

    def validate_fonts(self, content: str) -> Tuple[List[str], List[str]]:
        """
        验证内容中的字体使用
        Returns: (violations, warnings)
        """
        violations = []
        warnings = []

        # 常见字体规范模式
        font_patterns = [
            r'font-family\s*:\s*["\']?([^;"\']+)["\']?',
            r"font:\s*[^;]*\s+([A-Za-z][A-Za-z\s]+)(?:,|;|\s+\d)",
        ]

        found_fonts = []
        for pattern in font_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            found_fonts.extend(matches)

        for font in found_fonts:
            font_clean = font.strip().lower()
            # 检查发现的字体字符串中是否包含任何批准的字体
            if not any(approved.lower() in font_clean for approved in self.guidelines.fonts):
                violations.append(f"使用了未批准的字体: {font}")

        return violations, warnings

    def validate_tone(self, content: str) -> Tuple[List[str], List[str]]:
        """
        验证语调和消息
        Returns: (violations, warnings)
        """
        violations = []
        warnings = []

        # 检查禁用词
        content_lower = content.lower()
        for word in self.guidelines.prohibited_words:
            if word.lower() in content_lower:
                violations.append(f"使用了禁用词/短语: '{word}'")

        # 检查语调关键词（应至少包含一些）
        tone_matches = sum(
            1 for keyword in self.guidelines.tone_keywords if keyword.lower() in content_lower
        )

        if tone_matches == 0 and len(content) > 100:
            warnings.append(
                f"内容可能不符合品牌语调。 "
                f"考虑使用这样的术语: {', '.join(self.guidelines.tone_keywords[:5])}"
            )

        return violations, warnings

    def validate_brand_name(self, content: str) -> Tuple[List[str], List[str]]:
        """
        验证品牌名称的使用和大写
        Returns: (violations, warnings)
        """
        violations = []
        warnings = []

        # 查找品牌名称的所有变体
        brand_pattern = re.compile(re.escape(self.guidelines.brand_name), re.IGNORECASE)
        matches = brand_pattern.findall(content)

        for match in matches:
            if match != self.guidelines.brand_name:
                violations.append(
                    f"品牌名称大写不正确: '{match}' "
                    f"应为 '{self.guidelines.brand_name}'"
                )

        return violations, warnings

    def calculate_score(self, violations: List[str], warnings: List[str]) -> float:
        """计算合规分数 (0-100)"""
        violation_penalty = len(violations) * 10
        warning_penalty = len(warnings) * 3

        score = max(0, 100 - violation_penalty - warning_penalty)
        return round(score, 2)

    def generate_suggestions(self, violations: List[str], warnings: List[str]) -> List[str]:
        """根据违规和警告生成有用的建议"""
        suggestions = []

        if any("color" in v.lower() for v in violations):
            suggestions.append(
                f"使用批准的颜色: 主要: {', '.join(self.guidelines.primary_colors[:3])}"
            )

        if any("font" in v.lower() for v in violations):
            suggestions.append(f"使用批准的字体: {', '.join(self.guidelines.fonts)}")

        if any("tone" in w.lower() for w in warnings):
            suggestions.append(
                f"融入品牌语调关键词: {', '.join(self.guidelines.tone_keywords[:5])}"
            )

        if any("brand name" in v.lower() for v in violations):
            suggestions.append(f"始终将品牌名称大写为: {self.guidelines.brand_name}")

        return suggestions

    def validate(self, content: str) -> ValidationResult:
        """
        执行完整的品牌验证
        Returns: ValidationResult
        """
        all_violations = []
        all_warnings = []

        # 运行所有验证检查
        color_v, color_w = self.validate_colors(content)
        all_violations.extend(color_v)
        all_warnings.extend(color_w)

        font_v, font_w = self.validate_fonts(content)
        all_violations.extend(font_v)
        all_warnings.extend(font_w)

        tone_v, tone_w = self.validate_tone(content)
        all_violations.extend(tone_v)
        all_warnings.extend(tone_w)

        brand_v, brand_w = self.validate_brand_name(content)
        all_violations.extend(brand_v)
        all_warnings.extend(brand_w)

        # 计算分数并生成建议
        score = self.calculate_score(all_violations, all_warnings)
        suggestions = self.generate_suggestions(all_violations, all_warnings)

        return ValidationResult(
            passed=len(all_violations) == 0,
            score=score,
            violations=all_violations,
            warnings=all_warnings,
            suggestions=suggestions,
        )


def load_guidelines_from_json(filepath: str) -> BrandGuidelines:
    """
    从JSON文件加载品牌指南

    Args:
        filepath: 包含品牌指南的JSON文件路径

    Returns:
        BrandGuidelines 对象

    Raises:
        FileNotFoundError: 如果文件不存在
        json.JSONDecodeError: 如果文件包含无效JSON
        TypeError: 如果缺少必需字段
    """
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        return BrandGuidelines(**data)
    except FileNotFoundError:
        raise FileNotFoundError(f"找不到品牌指南文件: {filepath}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"品牌指南文件中的JSON无效: {e.msg}", e.doc, e.pos)
    except TypeError as e:
        raise TypeError(f"品牌指南中缺少必需字段: {e}")


def get_acme_corporation_guidelines() -> BrandGuidelines:
    """
    获取默认的Acme Corporation品牌指南。

    这些指南与SKILL.md参考中定义的标准相匹配。
    用户应为其自己的组织自定义这些。

    Returns:
    """
    return BrandGuidelines(
        brand_name="Acme Corporation",
        primary_colors=["#0066CC", "#003366", "#FFFFFF"],  # Acme 蓝、Acme 海军蓝、白色
        secondary_colors=[
            "#28A745",
            "#FFC107",
            "#DC3545",
            "#6C757D",
            "#F8F9FA",
        ],  # 成功绿、警告琥珀、错误红、中性灰、浅灰
        fonts=["Segoe UI", "system-ui", "-apple-system", "sans-serif"],
        tone_keywords=[
            "创新",
            "卓越",
            "专业",
            "解决方案",
            "值得信赖",
            "可靠",
        ],
        prohibited_words=["廉价", "过时", "劣质", "不专业", "草率"],
        tagline="卓越创新",
    )


def main():
    """演示品牌验证的示例用法"""
    # 加载Acme Corporation品牌指南
    # 用户应为其自己的组织自定义这个
    guidelines = get_acme_corporation_guidelines()

    # 要验证的示例内容（故意包含违规以供演示）
    test_content = """
    欢迎来到acme corporation！

    我们是一家提供过时技术的廉价解决方案提供商。

    我们在专业解决方案方面的创新和卓越值得信赖。

    联系我们：font-family: 'Comic Sans MS'
    配色方案：#FF0000
    背景：rgb(255, 0, 0)
    """

    # 验证
    validator = BrandValidator(guidelines)
    result = validator.validate(test_content)

    # 打印结果
    print("=" * 60)
    print("品牌验证报告")
    print("=" * 60)
    print(f"\n总体状态: {'✓ 通过' if result.passed else '✗ 失败'}")
    print(f"合规分数: {result.score}/100")

    if result.violations:
        print(f"\n❌ 违规 ({len(result.violations)}):")
        for i, violation in enumerate(result.violations, 1):
            print(f"  {i}. {violation}")

    if result.warnings:
        print(f"\n⚠️  警告 ({len(result.warnings)}):")
        for i, warning in enumerate(result.warnings, 1):
            print(f"  {i}. {warning}")

    if result.suggestions:
        print("\n💡 建议:")
        for i, suggestion in enumerate(result.suggestions, 1):
            print(f"  {i}. {suggestion}")

    print("\n" + "=" * 60)

    # 返回JSON以供程序化使用
    return asdict(result)


if __name__ == "__main__":
    main()
