import re

from detect_secrets.plugins.base import BasePlugin
from detect_secrets.core.log import log


class AnthropicSecretsDetector(BasePlugin):
    """扫描笔记本中常见的API密钥和凭据。"""

    log.info("正在运行Anthropic密钥检测器")
    secret_type = "API Credentials"  # type: ignore

    denylist = [
        # Anthropic API密钥 (sk-ant-api03-...)
        re.compile(r"sk-ant-api03-[A-Za-z0-9_-]{95,}"),
        # 其他API密钥 (sk-...)
        re.compile(r"sk-[A-Za-z0-9]{48,}"),
        re.compile(r"pa-[A-Za-z0-9]{48,}"),
        # 通用API密钥模式
        re.compile(r'api[_-]?key[\'"\s]*[:=][\'"\s]*[A-Za-z0-9_\-]{20,}', re.IGNORECASE),
        re.compile(r'apikey[\'"\s]*[:=][\'"\s]*[A-Za-z0-9_\-]{20,}', re.IGNORECASE),
    ]
