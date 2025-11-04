"""
企业文档品牌应用模块。
为Excel、PowerPoint和PDF文档应用一致的品牌。
"""

from typing import Dict, Any, List


class BrandFormatter:
    """将企业品牌指南应用于文档。"""

    # 品牌颜色定义
    COLORS = {
        "primary": {
            "acme_blue": {"hex": "#0066CC", "rgb": (0, 102, 204)},
            "acme_navy": {"hex": "#003366", "rgb": (0, 51, 102)},
            "white": {"hex": "#FFFFFF", "rgb": (255, 255, 255)},
        },
        "secondary": {
            "success_green": {"hex": "#28A745", "rgb": (40, 167, 69)},
            "warning_amber": {"hex": "#FFC107", "rgb": (255, 193, 7)},
            "error_red": {"hex": "#DC3545", "rgb": (220, 53, 69)},
            "neutral_gray": {"hex": "#6C757D", "rgb": (108, 117, 125)},
            "light_gray": {"hex": "#F8F9FA", "rgb": (248, 249, 250)},
        },
    }

    # 字体定义
    FONTS = {
        "primary": "Segoe UI",
        "fallback": ["system-ui", "-apple-system", "sans-serif"],
        "sizes": {"h1": 32, "h2": 24, "h3": 18, "body": 11, "caption": 9},
        "weights": {"regular": 400, "semibold": 600, "bold": 700},
    }

    # 公司信息
    COMPANY = {
        "name": "Acme Corporation",
        "tagline": "卓越创新",
        "copyright": "© 2025 Acme Corporation. 保留所有权利。",
        "website": "www.acmecorp.example",
        "logo_path": "assets/acme_logo.png",
    }

    def __init__(self):
        """使用标准设置初始化品牌格式化器。"""
        self.colors = self.COLORS
        self.fonts = self.FONTS
        self.company = self.COMPANY

    def format_excel(self, workbook_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        将品牌格式应用于Excel工作簿配置。

        Args:
            workbook_config: Excel工作簿配置字典

        Returns:
            品牌化的工作簿配置
        """
        branded_config = workbook_config.copy()

        # 应用表头格式化
        branded_config["header_style"] = {
            "font": {
                "name": self.fonts["primary"],
                "size": self.fonts["sizes"]["body"],
                "bold": True,
                "color": self.colors["primary"]["white"]["hex"],
            },
            "fill": {"type": "solid", "color": self.colors["primary"]["acme_blue"]["hex"]},
            "alignment": {"horizontal": "center", "vertical": "center"},
            "border": {"style": "thin", "color": self.colors["secondary"]["neutral_gray"]["hex"]},
        }

        # 应用数据单元格格式化
        branded_config["cell_style"] = {
            "font": {
                "name": self.fonts["primary"],
                "size": self.fonts["sizes"]["body"],
                "color": self.colors["primary"]["acme_navy"]["hex"],
            },
            "alignment": {"horizontal": "left", "vertical": "center"},
        }

        # 应用交替行颜色
        branded_config["alternating_rows"] = {
            "enabled": True,
            "color": self.colors["secondary"]["light_gray"]["hex"],
        }

        # 图表配色方案
        branded_config["chart_colors"] = [
            self.colors["primary"]["acme_blue"]["hex"],
            self.colors["secondary"]["success_green"]["hex"],
            self.colors["secondary"]["warning_amber"]["hex"],
            self.colors["secondary"]["neutral_gray"]["hex"],
        ]

        return branded_config

    def format_powerpoint(self, presentation_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        将品牌格式应用于PowerPoint演示文稿配置。

        Args:
            presentation_config: PowerPoint配置字典

        Returns:
            品牌化的演示文稿配置
        """
        branded_config = presentation_config.copy()

        # 幻灯片母版设置
        branded_config["master"] = {
            "background_color": self.colors["primary"]["white"]["hex"],
            "title_area": {
                "font": self.fonts["primary"],
                "size": self.fonts["sizes"]["h1"],
                "color": self.colors["primary"]["acme_blue"]["hex"],
                "bold": True,
                "position": {"x": 0.5, "y": 0.15, "width": 9, "height": 1},
            },
            "content_area": {
                "font": self.fonts["primary"],
                "size": self.fonts["sizes"]["body"],
                "color": self.colors["primary"]["acme_navy"]["hex"],
                "position": {"x": 0.5, "y": 2, "width": 9, "height": 5},
            },
            "footer": {
                "show_slide_number": True,
                "show_date": True,
                "company_name": self.company["name"],
            },
        }

        # 标题幻灯片模板
        branded_config["title_slide"] = {
            "background": self.colors["primary"]["acme_blue"]["hex"],
            "title_color": self.colors["primary"]["white"]["hex"],
            "subtitle_color": self.colors["primary"]["white"]["hex"],
            "include_logo": True,
            "logo_position": {"x": 0.5, "y": 0.5, "width": 2},
        }

        # 内容幻灯片模板
        branded_config["content_slide"] = {
            "title_bar": {
                "background": self.colors["primary"]["acme_blue"]["hex"],
                "text_color": self.colors["primary"]["white"]["hex"],
                "height": 1,
            },
            "bullet_style": {"level1": "•", "level2": "○", "level3": "▪", "indent": 0.25},
        }

        # 图表默认设置
        branded_config["charts"] = {
            "color_scheme": [
                self.colors["primary"]["acme_blue"]["hex"],
                self.colors["secondary"]["success_green"]["hex"],
                self.colors["secondary"]["warning_amber"]["hex"],
                self.colors["secondary"]["neutral_gray"]["hex"],
            ],
            "gridlines": {"color": self.colors["secondary"]["neutral_gray"]["hex"], "width": 0.5},
            "font": {"name": self.fonts["primary"], "size": self.fonts["sizes"]["caption"]},
        }

        return branded_config

    def format_pdf(self, document_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        将品牌格式应用于PDF文档配置。

        Args:
            document_config: PDF文档配置字典

        Returns:
            品牌化的文档配置
        """
        branded_config = document_config.copy()

        # 页面布局
        branded_config["page"] = {
            "margins": {"top": 1, "bottom": 1, "left": 1, "right": 1},
            "size": "letter",
            "orientation": "portrait",
        }

        # 页眉配置
        branded_config["header"] = {
            "height": 0.75,
            "content": {
                "left": {"type": "logo", "width": 1.5},
                "center": {
                    "type": "text",
                    "content": document_config.get("title", "Document"),
                    "font": self.fonts["primary"],
                    "size": self.fonts["sizes"]["body"],
                    "color": self.colors["primary"]["acme_navy"]["hex"],
                },
                "right": {"type": "page_number", "format": "Page {page} of {total}"},
            },
        }

        # 页脚配置
        branded_config["footer"] = {
            "height": 0.5,
            "content": {
                "left": {
                    "type": "text",
                    "content": self.company["copyright"],
                    "font": self.fonts["primary"],
                    "size": self.fonts["sizes"]["caption"],
                    "color": self.colors["secondary"]["neutral_gray"]["hex"],
                },
                "center": {"type": "date", "format": "%Y年%m月%d日"},
                "right": {"type": "text", "content": "机密"},
            },
        }

        # 文本样式
        branded_config["styles"] = {
            "heading1": {
                "font": self.fonts["primary"],
                "size": self.fonts["sizes"]["h1"],
                "color": self.colors["primary"]["acme_blue"]["hex"],
                "bold": True,
                "spacing_after": 12,
            },
            "heading2": {
                "font": self.fonts["primary"],
                "size": self.fonts["sizes"]["h2"],
                "color": self.colors["primary"]["acme_navy"]["hex"],
                "bold": True,
                "spacing_after": 10,
            },
            "heading3": {
                "font": self.fonts["primary"],
                "size": self.fonts["sizes"]["h3"],
                "color": self.colors["primary"]["acme_navy"]["hex"],
                "bold": False,
                "spacing_after": 8,
            },
            "body": {
                "font": self.fonts["primary"],
                "size": self.fonts["sizes"]["body"],
                "color": self.colors["primary"]["acme_navy"]["hex"],
                "line_spacing": 1.15,
                "paragraph_spacing": 12,
            },
            "caption": {
                "font": self.fonts["primary"],
                "size": self.fonts["sizes"]["caption"],
                "color": self.colors["secondary"]["neutral_gray"]["hex"],
                "italic": True,
            },
        }

        # 表格格式化
        branded_config["table_style"] = {
            "header": {
                "background": self.colors["primary"]["acme_blue"]["hex"],
                "text_color": self.colors["primary"]["white"]["hex"],
                "bold": True,
            },
            "rows": {
                "alternating_color": self.colors["secondary"]["light_gray"]["hex"],
                "border_color": self.colors["secondary"]["neutral_gray"]["hex"],
            },
        }

        return branded_config

    def validate_colors(self, colors_used: List[str]) -> Dict[str, Any]:
        """
        验证颜色是否符合品牌指南。

        Args:
            colors_used: 文档中使用的颜色代码列表

        Returns:
            验证结果，如有需要则包含修正建议
        """
        results = {"valid": True, "corrections": [], "warnings": []}

        approved_colors = []
        for category in self.colors.values():
            for color in category.values():
                approved_colors.append(color["hex"].upper())

        for color in colors_used:
            color_upper = color.upper()
            if color_upper not in approved_colors:
                results["valid"] = False
                # 查找最接近的品牌颜色
                closest = self._find_closest_brand_color(color)
                results["corrections"].append(
                    {
                        "original": color,
                        "suggested": closest,
                        "message": f"非品牌颜色 {color} 应替换为 {closest}",
                    }
                )

        return results

    def _find_closest_brand_color(self, color: str) -> str:
        """查找与给定颜色最接近的品牌颜色。"""
        # 简化实现 - 实际中应计算颜色距离
        return self.colors["primary"]["acme_blue"]["hex"]

    def apply_watermark(self, document_type: str) -> Dict[str, Any]:
        """
        为文档生成水印配置。

        Args:
            document_type: 文档类型（草稿、机密等）

        Returns:
            水印配置
        """
        watermarks = {
            "draft": {
                "text": "DRAFT",
                "color": self.colors["secondary"]["neutral_gray"]["hex"],
                "opacity": 0.1,
                "angle": 45,
                "font_size": 72,
            },
            "confidential": {
                "text": "CONFIDENTIAL",
                "color": self.colors["secondary"]["error_red"]["hex"],
                "opacity": 0.1,
                "angle": 45,
                "font_size": 60,
            },
            "sample": {
                "text": "SAMPLE",
                "color": self.colors["secondary"]["warning_amber"]["hex"],
                "opacity": 0.15,
                "angle": 45,
                "font_size": 72,
            },
        }

        return watermarks.get(document_type, watermarks["draft"])

    def get_chart_palette(self, num_series: int = 4) -> List[str]:
        """
        获取图表配色。

        Args:
            num_series: 数据系列数量

        Returns:
            十六进制颜色代码列表
        """
        palette = [
            self.colors["primary"]["acme_blue"]["hex"],
            self.colors["secondary"]["success_green"]["hex"],
            self.colors["secondary"]["warning_amber"]["hex"],
            self.colors["secondary"]["neutral_gray"]["hex"],
            self.colors["primary"]["acme_navy"]["hex"],
            self.colors["secondary"]["error_red"]["hex"],
        ]

        return palette[:num_series]

    def format_number(self, value: float, format_type: str = "general") -> str:
        """
        根据品牌标准格式化数字。

        Args:
            value: 要格式化的数值
            format_type: 格式化类型（货币、百分比、通用）

        Returns:
            格式化后的字符串
        """
        if format_type == "currency":
            return f"${value:,.2f}"
        elif format_type == "percentage":
            return f"{value:.1f}%"
        elif format_type == "large_number":
            if value >= 1_000_000:
                return f"{value / 1_000_000:.1f}M"
            elif value >= 1_000:
                return f"{value / 1_000:.1f}K"
            else:
                return f"{value:.0f}"
        else:
            return f"{value:,.0f}" if value >= 1000 else f"{value:.2f}"


def apply_brand_to_document(document_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    将品牌应用于任何文档类型的主函数。

    Args:
        document_type: 文档类型（'excel', 'powerpoint', 'pdf'）
        config: 文档配置

    Returns:
        品牌化配置
    """
    formatter = BrandFormatter()

    if document_type.lower() == "excel":
        return formatter.format_excel(config)
    elif document_type.lower() in ["powerpoint", "pptx"]:
        return formatter.format_powerpoint(config)
    elif document_type.lower() == "pdf":
        return formatter.format_pdf(config)
    else:
        raise ValueError(f"不支持的文档类型: {document_type}")


# 示例用法
if __name__ == "__main__":
    # Excel 配置示例
    excel_config = {"title": "季度报告", "sheets": ["摘要", "详情"]}

    branded_excel = apply_brand_to_document("excel", excel_config)
    print("品牌化 Excel 配置:")
    print(branded_excel)

    # PowerPoint 配置示例
    ppt_config = {"title": "业务评审", "num_slides": 10}

    branded_ppt = apply_brand_to_document("powerpoint", ppt_config)
    print("\n品牌化 PowerPoint 配置:")
    print(branded_ppt)
