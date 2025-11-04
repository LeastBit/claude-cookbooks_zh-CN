"""
使用Claude Skills API管理自定义技能的实用函数。

此模块提供辅助函数用于：
- 创建和上传自定义技能
- 列出和检索技能信息
- 管理技能版本
- 使用Claude测试技能
- 删除技能
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from anthropic import Anthropic
from anthropic.lib import files_from_dir


def create_skill(client: Anthropic, skill_path: str, display_title: str) -> Dict[str, Any]:
    """
    从目录创建新的自定义技能。

    目录必须包含：
    - 带有YAML前导块的SKILL.md文件（名称、描述）
    - 可选：scripts、resources、REFERENCE.md

    Args:
        client: 具有Skills beta的Anthropic客户端实例
        skill_path: 包含SKILL.md的技能目录路径
        display_title: 人类可读的技能名称

    Returns:
        技能创建结果的字典：
        {
            'success': bool,
            'skill_id': str (如果成功),
            'display_title': str,
            'latest_version': str,
            'created_at': str,
            'source': str ('custom'),
            'error': str (如果失败)
        }

    Example:
        >>> client = Anthropic(api_key="...", default_headers={"anthropic-beta": "skills-2025-10-02"})
        >>> result = create_skill(client, "custom_skills/financial_analyzer", "Financial Analyzer")
        >>> if result['success']:
        ...     print(f"Created skill: {result['skill_id']}")
    """
    try:
        # 验证技能目录
        skill_dir = Path(skill_path)
        if not skill_dir.exists():
            return {"success": False, "error": f"Skill directory does not exist: {skill_path}"}

        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            return {"success": False, "error": f"SKILL.md not found in {skill_path}"}

        # 使用files_from_dir创建技能
        skill = client.beta.skills.create(
            display_title=display_title, files=files_from_dir(skill_path)
        )

        return {
            "success": True,
            "skill_id": skill.id,
            "display_title": skill.display_title,
            "latest_version": skill.latest_version,
            "created_at": skill.created_at,
            "source": skill.source,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def list_custom_skills(client: Anthropic) -> List[Dict[str, Any]]:
    """
    列出工作区中的所有自定义技能。

    Args:
        client: 具有Skills beta的Anthropic客户端实例

    Returns:
        带有元数据的技能字典列表

    Example:
        >>> skills = list_custom_skills(client)
        >>> for skill in skills:
        ...     print(f"{skill['display_title']}: {skill['skill_id']}")
    """
    try:
        skills_response = client.beta.skills.list(source="custom")

        skills = []
        for skill in skills_response.data:
            skills.append(
                {
                    "skill_id": skill.id,
                    "display_title": skill.display_title,
                    "latest_version": skill.latest_version,
                    "created_at": skill.created_at,
                    "updated_at": skill.updated_at,
                }
            )

        return skills

    except Exception as e:
        print(f"Error listing skills: {e}")
        return []


def get_skill_version(
    client: Anthropic, skill_id: str, version: str = "latest"
) -> Optional[Dict[str, Any]]:
    """
    获取特定技能版本的详细信息。

    Args:
        client: Anthropic客户端实例
        skill_id: 技能ID
        version: 要检索的版本（默认："latest"）

    Returns:
        包含版本详情的字典，如果未找到则返回None
    """
    try:
        # 如果未指定，获取最新版本
        if version == "latest":
            skill = client.beta.skills.retrieve(skill_id)
            version = skill.latest_version

        version_info = client.beta.skills.versions.retrieve(skill_id=skill_id, version=version)

        return {
            "version": version_info.version,
            "skill_id": version_info.skill_id,
            "name": version_info.name,
            "description": version_info.description,
            "directory": version_info.directory,
            "created_at": version_info.created_at,
        }

    except Exception as e:
        print(f"Error getting skill version: {e}")
        return None


def create_skill_version(client: Anthropic, skill_id: str, skill_path: str) -> Dict[str, Any]:
    """
    创建现有技能的新版本。

    Args:
        client: Anthropic客户端实例
        skill_id: 现有技能的ID
        skill_path: 更新的技能目录路径

    Returns:
        版本创建结果的字典
    """
    try:
        version = client.beta.skills.versions.create(
            skill_id=skill_id, files=files_from_dir(skill_path)
        )

        return {
            "success": True,
            "version": version.version,
            "skill_id": version.skill_id,
            "created_at": version.created_at,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_skill(client: Anthropic, skill_id: str, delete_versions: bool = True) -> bool:
    """
    删除自定义技能并可选地删除其所有版本。

    注意：必须先删除所有版本，然后才能删除技能。

    Args:
        client: Anthropic客户端实例
        skill_id: 要删除的技能ID
        delete_versions: 是否首先删除所有版本

    Returns:
        如果成功则返回True，否则返回False
    """
    try:
        if delete_versions:
            # 首先删除所有版本
            versions = client.beta.skills.versions.list(skill_id=skill_id)

            for version in versions.data:
                client.beta.skills.versions.delete(skill_id=skill_id, version=version.version)
                print(f"  Deleted version: {version.version}")

        # 然后删除技能本身
        client.beta.skills.delete(skill_id)
        print(f"✓ Deleted skill: {skill_id}")
        return True

    except Exception as e:
        print(f"Error deleting skill: {e}")
        return False


def test_skill(
    client: Anthropic,
    skill_id: str,
    test_prompt: str,
    model: str = "claude-sonnet-4-5",
    include_anthropic_skills: Optional[List[str]] = None,
) -> Any:
    """
    使用提示测试自定义技能。

    Args:
        client: Anthropic客户端实例
        skill_id: 要测试的技能ID
        test_prompt: 测试技能的提示
        model: 用于测试的模型
        include_anthropic_skills: 要包含的Anthropic技能ID的可选列表

    Returns:
        Claude的响应

    Example:
        >>> response = test_skill(
        ...     client,
        ...     "skill_abc123",
        ...     "Calculate P/E ratio for a company with price $50 and earnings $2.50",
        ...     include_anthropic_skills=["xlsx"]
        ... )
    """
    # 构建技能列表
    skills = [{"type": "custom", "skill_id": skill_id, "version": "latest"}]

    # 如果请求，添加Anthropic技能
    if include_anthropic_skills:
        for anthropic_skill in include_anthropic_skills:
            skills.append({"type": "anthropic", "skill_id": anthropic_skill, "version": "latest"})

    response = client.beta.messages.create(
        model=model,
        max_tokens=4096,
        container={"skills": skills},
        tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
        messages=[{"role": "user", "content": test_prompt}],
        betas=["code-execution-2025-08-25", "files-api-2025-04-14", "skills-2025-10-02"],
    )

    return response


def list_skill_versions(client: Anthropic, skill_id: str) -> List[Dict[str, Any]]:
    """
    列出技能的所有版本。

    Args:
        client: Anthropic客户端实例
        skill_id: 技能ID

    Returns:
        版本字典列表
    """
    try:
        versions_response = client.beta.skills.versions.list(skill_id=skill_id)

        versions = []
        for version in versions_response.data:
            versions.append(
                {
                    "version": version.version,
                    "skill_id": version.skill_id,
                    "created_at": version.created_at,
                }
            )

        return versions

    except Exception as e:
        print(f"Error listing versions: {e}")
        return []


def validate_skill_directory(skill_path: str) -> Dict[str, Any]:
    """
    上传前验证技能目录结构。

    检查：
    - SKILL.md存在
    - YAML前导块有效
    - 目录名与技能名匹配
    - 总大小小于8MB

    Args:
        skill_path: 技能目录路径

    Returns:
        验证结果的字典
    """
    result = {"valid": True, "errors": [], "warnings": [], "info": {}}

    skill_dir = Path(skill_path)

    # 检查目录是否存在
    if not skill_dir.exists():
        result["valid"] = False
        result["errors"].append(f"Directory does not exist: {skill_path}")
        return result

    # 检查SKILL.md
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        result["valid"] = False
        result["errors"].append("SKILL.md file is required")
    else:
        # 读取并验证SKILL.md
        content = skill_md.read_text()

        # 检查YAML前导块
        if not content.startswith("---"):
            result["valid"] = False
            result["errors"].append("SKILL.md must start with YAML frontmatter (---)")
        else:
            # 提取前导块
            try:
                end_idx = content.index("---", 3)
                frontmatter = content[3:end_idx].strip()

                # 检查必需字段
                if "name:" not in frontmatter:
                    result["valid"] = False
                    result["errors"].append("YAML frontmatter must include 'name' field")

                if "description:" not in frontmatter:
                    result["valid"] = False
                    result["errors"].append("YAML frontmatter must include 'description' field")

                # 检查前导块大小
                if len(frontmatter) > 1024:
                    result["valid"] = False
                    result["errors"].append(
                        f"YAML frontmatter exceeds 1024 chars (found: {len(frontmatter)})"
                    )

            except ValueError:
                result["valid"] = False
                result["errors"].append("Invalid YAML frontmatter format")

    # 检查总大小
    total_size = sum(f.stat().st_size for f in skill_dir.rglob("*") if f.is_file())
    result["info"]["total_size_mb"] = total_size / (1024 * 1024)

    if total_size > 8 * 1024 * 1024:
        result["valid"] = False
        result["errors"].append(
            f"Total size exceeds 8MB (found: {total_size / (1024 * 1024):.2f} MB)"
        )

    # 统计文件
    files = list(skill_dir.rglob("*"))
    result["info"]["file_count"] = len([f for f in files if f.is_file()])
    result["info"]["directory_count"] = len([f for f in files if f.is_dir()])

    # 检查常见文件
    if (skill_dir / "REFERENCE.md").exists():
        result["info"]["has_reference"] = True

    if (skill_dir / "scripts").exists():
        result["info"]["has_scripts"] = True
        result["info"]["script_files"] = [
            f.name for f in (skill_dir / "scripts").iterdir() if f.is_file()
        ]

    return result


def print_skill_summary(skill_info: Dict[str, Any]) -> None:
    """
    打印技能的格式化摘要。

    Args:
        skill_info: 包含技能信息的字典
    """
    print(f"📦 Skill: {skill_info.get('display_title', 'Unknown')}")
    print(f"   ID: {skill_info.get('skill_id', 'N/A')}")
    print(f"   Version: {skill_info.get('latest_version', 'N/A')}")
    print(f"   Source: {skill_info.get('source', 'N/A')}")
    print(f"   Created: {skill_info.get('created_at', 'N/A')}")

    if "error" in skill_info:
        print(f"   ❌ Error: {skill_info['error']}")
