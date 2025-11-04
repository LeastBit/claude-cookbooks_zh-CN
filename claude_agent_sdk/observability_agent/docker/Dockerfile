FROM python:3.11

WORKDIR /app

# 安装系统依赖，包括Docker CLI
RUN apt-get update && apt-get install -y \
    curl \
    git \
    ca-certificates \
    gnupg \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
    "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" > /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y docker-ce-cli \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN npm install -g @anthropic-ai/claude-code

COPY observability_agent ./observability_agent  # 复制可观测性代理目录

RUN pip install --no-cache-dir \
    claude-agent-sdk \
    fastapi \
    python-dotenv \
    uvicorn[standard] \
    mcp-server-git

RUN claude --version

EXPOSE 8000  # 暴露端口

CMD ["python", "-m", "observability_agent.web.app"]