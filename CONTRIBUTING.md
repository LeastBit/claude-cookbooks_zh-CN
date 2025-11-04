# 为 Claude Cookbooks 做贡献

感谢您对为 Claude Cookbooks 做贡献的兴趣！本指南将帮助您开始开发，并确保您的贡献符合我们的质量标准。

## 开发设置

### 先决条件

- Python 3.11 或更高版本
- [uv](https://docs.astral.sh/uv/) 包管理器（推荐）或 pip

### 快速开始

1. **安装 uv**（推荐包管理器）：
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   或使用 Homebrew：
   ```bash
   brew install uv
   ```

2. **克隆仓库**：
   ```bash
   git clone https://github.com/anthropics/anthropic-cookbook.git
   cd anthropic-cookbook
   ```

3. **设置开发环境**：
   ```bash
   # 创建虚拟环境并安装依赖
   uv sync --all-extras

   # 或使用 pip：
   pip install -e ".[dev]"
   ```

4. **安装预提交钩子**：
   ```bash
   uv run pre-commit install
   # 或者：pre-commit install
   ```

5. **设置您的 API 密钥**：
   ```bash
   cp .env.example .env
   # 编辑 .env 并添加您的 Claude API 密钥
   ```

## 质量标准

此仓库使用自动化工具来维护代码质量：

### Notebook 验证栈

- **[nbconvert](https://nbconvert.readthedocs.io/)**: 用于测试的 Notebook 执行
- **[ruff](https://docs.astral.sh/ruff/)**: 具有原生 Jupyter 支持的快速 Python linter 和格式化工具
- **Claude AI 审查**: 使用 Claude 进行智能代码审查

**注意**：Notebook 输出在此仓库中有意保留，因为它们向用户展示了预期结果。

### Claude Code 斜杠命令

此仓库包含在 Claude Code（用于本地开发）和 GitHub Actions CI 中都能工作的斜杠命令。当您使用 Claude Code 在此仓库中工作时，这些命令会自动可用。

**可用命令**：
- `/link-review` - 验证 markdown 和 notebook 中的链接
- `/model-check` - 验证 Claude 模型使用是否最新
- `/notebook-review` - 全面的 notebook 质量检查

**在 Claude Code 中的使用**：
```bash
# 运行与 CI 将运行的相同验证
/notebook-review skills/my-notebook.ipynb
/model-check
/link-review README.md
```

这些命令使用与我们的 CI 管道完全相同的验证逻辑，帮助您在推送之前发现问题。命令定义存储在 `.claude/commands/` 中，供本地和 CI 使用。

### 提交之前

1. **运行质量检查**：
   ```bash
   uv run ruff check skills/ --fix
   uv run ruff format skills/

   uv run python scripts/validate_notebooks.py
   ```

3. **测试 notebook 执行**（可选，需要 API 密钥）：
   ```bash
   uv run jupyter nbconvert --to notebook \
     --execute skills/classification/guide.ipynb \
     --ExecutePreprocessor.kernel_name=python3 \
     --output test_output.ipynb
   ```

### 预提交钩子

预提交钩子会在每次提交前自动运行以确保代码质量：

- 使用 ruff 格式化代码
- 验证 notebook 结构

如果钩子失败，请修复问题并重试提交。

## 贡献指南

### Notebook 最佳实践

1. **使用环境变量进行 API 密钥管理**：
   ```python
   import os
   api_key = os.environ.get("ANTHROPIC_API_KEY")
   ```

2. **使用当前的 Claude 模型**：
   - 如果可用，使用模型别名以提高可维护性
   - 最新的 Haiku 模型：`claude-haiku-4-5-20251001`（Haiku 4.5）
   - 在以下网址查看当前模型：https://docs.claude.com/en/docs/about-claude/models/overview
   - Claude 将在 PR 审查中自动验证模型使用情况

3. **保持 notebook 专注**：
   - 每个 notebook 一个概念
   - 清晰的解释和注释
   - 包含预期输出作为 markdown 单元

4. **测试您的 notebook**：
   - 确保它们从头到尾运行无误
   - 为示例 API 调用使用最少的标记
   - 包含错误处理

### Git 工作流程

1. **创建功能分支**：
   ```bash
   git checkout -b <your-name>/<feature-description>
   # 示例：git checkout -b alice/add-rag-example
   ```

2. **使用约定式提交**：
   ```bash
   # 格式：<type>(<scope>): <subject>

   # 类型：
   feat     # 新功能
   fix      # 错误修复
   docs     # 文档
   style    # 格式
   refactor # 代码重构
   test     # 测试
   chore    # 维护
   ci       # CI/CD 更改

   # 示例：
   git commit -m "feat(skills): add text-to-sql notebook"
   git commit -m "fix(api): use environment variable for API key"
   git commit -m "docs(readme): update installation instructions"
   ```

3. **保持提交原子性**：
   - 每次提交一个逻辑更改
   - 编写清晰、描述性的消息
   - 在适用时引用问题

4. **推送并创建 PR**：
   ```bash
   git push -u origin your-branch-name
   gh pr create  # 或使用 GitHub web 界面
   ```

### 拉取请求指南

1. **PR 标题**：使用约定式提交格式
2. **描述**：包括：
   - 您做了什么更改
   - 为什么做这些更改
   - 如何测试它们
   - 相关问题编号
3. **保持 PR 专注**：每个 PR 一个功能/修复
4. **回应反馈**：及时解决审查评论

## 测试

### 本地测试

运行验证套件：

```bash
# 检查所有 notebook
uv run python scripts/validate_notebooks.py

# 对所有文件运行预提交
uv run pre-commit run --all-files
```

### CI/CD

我们的 GitHub Actions 工作流将自动：

- 验证 notebook 结构
- 使用 ruff 检查代码
- 测试 notebook 执行（对于维护者）
- 检查链接
- Claude 审查代码和模型使用

外部贡献者将进行有限的 API 测试以节省资源。

## 获取帮助

- **问题**：[GitHub Issues](https://github.com/anthropics/anthropic-cookbook/issues)
- **讨论**：[GitHub Discussions](https://github.com/anthropics/anthropic-cookbook/discussions)
- **Discord**：[Anthropic Discord](https://www.anthropic.com/discord)

## 安全

- 永远不要提交 API 密钥或秘钥
- 对敏感数据使用环境变量
- 私下向 security@anthropic.com 报告安全问题

## 许可证

通过贡献，您同意您的贡献将在与项目相同的许可证下获得许可（MIT 许可证）。