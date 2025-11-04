# 使用Claude Agent SDK构建强大的智能体

本教程系列演示如何使用[Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python)构建复杂的通用智能体系统，从简单的研究智能体到多智能体编排与外部系统集成。

## 快速开始

#### 1. 安装uv、[node](https://nodejs.org/en/download/)和Claude Code CLI（如果您还没有的话）

```curl -LsSf https://astral.sh/uv/install.sh | sh ```

```npm install -g @anthropic-ai/claude-code```

#### 2. 克隆并设置项目

```git clone https://github.com/anthropics/anthropic-cookbook.git ```

```cd anthropic-cookbook/claude_agent_sdk```

```uv sync ```

#### 3. 注册venv为Jupyter内核，以便您可以在笔记本中使用

```uv run python -m ipykernel install --user --name="cc-sdk-tutorial" --display-name "Python (cc-sdk-tutorial)" ```

#### 4. Claude API密钥
1. 访问[console.anthropic.com](https://console.anthropic.com/dashboard)
2. 注册或登录您的账户
3. 点击"获取API密钥"
4. 复制密钥并粘贴到您的`.env`文件中，格式为```ANTHROPIC_API_KEY=```

#### 5. 笔记本02的GitHub令牌
如果您计划学习可观测性智能体笔记本：
1. 在[此处](https://github.com/settings/personal-access-tokens/new)获取GitHub个人访问令牌
2. 选择具有默认选项的"细粒度"令牌（公共仓库，无账户权限）
3. 将其添加到您的`.env`文件中，格式为`GITHUB_TOKEN="<token>"`
4. 确保您的机器上运行着[Docker](https://www.docker.com/products/docker-desktop/)

## 教程系列概述

本教程系列带您从基本智能体实现到能够处理现实世界复杂性的复杂多智能体系统。每个笔记本都建立在前一个的基础上，引入新概念和功能，同时保持实用的、生产就绪的实现。

### 您将学到的内容

通过本系列，您将接触到：
- **核心SDK基础**包括Python SDK中的`query()`、`ClaudeSDKClient`和`ClaudeAgentOptions`接口
- **工具使用模式**从基本的WebSearch到复杂的MCP服务器集成
- **多智能体编排**与专门的子智能体和协调
- **企业功能**通过钩子实现合规跟踪和审计跟踪
- **外部系统集成**通过模型上下文协议(MCP)

注意：本教程假设您对Claude Code有一定程度的熟悉。理想情况下，如果您一直在使用Claude Code来增强您的编码任务，并且希望将其原始智能体能力用于软件工程之外的任务，本教程将帮助您入门。

## 笔记本结构与内容

### [笔记本00：一行式研究智能体](00_The_one_liner_research_agent.ipynb)

用几行代码构建一个简单而强大的研究智能体，开始您的旅程。本笔记本介绍核心SDK概念，并展示Claude Agent SDK如何实现自主信息收集和综合。

**核心概念：**
- 使用`query()`和异步迭代的基本智能体循环
- 用于自主研究的WebSearch工具
- 使用Read工具的多模态能力
- 使用`ClaudeSDKClient`管理对话上下文
- 用于智能体专业的系统提示

### [笔记本01：首席助理智能体](01_The_chief_of_staff_agent.ipynb)

为初创公司CEO构建一个全面的AI首席助理，展示生产环境的高级SDK功能。本笔记本演示如何创建具有治理、合规性和专门知识的复杂智能体架构。

**探索的关键功能：**
- **记忆与上下文：**使用CLAUDE.md文件实现持久化指令
- **输出样式：**针对不同受众的定制化通信
- **计划模式：**复杂任务的战略规划而非执行
- **自定义斜杠命令：**常见操作的用户友好快捷方式
- **钩子：**自动化合规跟踪和审计跟踪
- **子智能体编排：**协调专门智能体提供领域专业知识
- **Bash工具集成：**用于程序化知识和复杂计算的Python脚本执行

### [笔记本02：可观测性智能体](02_The_observability_agent.ipynb)

通过模型上下文协议将智能体连接到外部系统，超越本地能力。将您的智能体从被动观察者转变为DevOps工作流中的主动参与者。

**高级功能：**
- **Git MCP服务器：**13+个用于仓库分析和版本控制的工具
- **GitHub MCP服务器：**100+个用于完整GitHub平台集成的工具
- **实时监控：**CI/CD管道分析和故障检测
- **智能事件响应：**自动化根本原因分析
- **生产工作流自动化：**从监控到可操作洞察

## 完整的智能体实现

每个笔记本在其各自目录中包含一个智能体实现：
- **`research_agent/`** - 具有网络搜索和多模态分析的自主研究智能体
- **`chief_of_staff_agent/`** - 具有财务建模和合规性的多智能体执行助理
- **`observability_agent/`** - 具有GitHub集成的DevOps监控智能体

## 背景
### Claude Agent SDK的演进

Claude Code已成为Anthropic最成功的产品之一，但这不仅仅是因为其SOTA编码能力。它的真正突破在于更基本的东西：**Claude在智能体工作方面表现出色**。

Claude Code的特别之处不仅仅在于代码理解；它在于能够：
- 自主地将复杂任务分解为可管理的步骤
- 有效地使用工具并明智地决定何时使用哪些工具
- 在长期运行的任务中保持上下文和记忆
- 从错误中优雅地恢复并在需要时调整方法
- 知道何时寻求澄清以及何时在合理假设下继续

这些能力使Claude Code成为Claude原始智能体能力的"裸金属"支架最接近的存在：一个最小化yet完整而复杂的接口，以最少的开销让模型的能力发光。

### 超越编码：智能体构建工具包

最初作为Anthropic工程师构建的内部工具来加速开发工作流，SDK的公开发布揭示了意想不到的潜力。在Claude Agent SDK及其GitHub集成发布后，开发者开始将其用于远 beyond 编码的任务：

- **研究智能体**收集和综合多个来源的信息
- **数据分析智能体**探索数据集并生成洞察
- **工作流自动化智能体**处理重复的业务流程
- **监控和可观测性智能体**观察系统并响应问题
- **内容生成智能体**创建和完善各种类型的内容

模式很清晰：SDK无意中成为了一个有效的智能体构建框架。其旨在处理软件开发复杂性的架构被证明非常适合通用智能体创建。

本教程系列演示如何利用Claude Agent SDK为任何领域或用例构建高效的智能体，从简单自动化到复杂企业系统。

## 贡献

发现问题或有建议？请打开问题或提交拉取请求！
