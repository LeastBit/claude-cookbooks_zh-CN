# Claude Skills Cookbook 技能手册 🚀

全面介绍Claude的Skills功能用于文档生成、数据分析和业务自动化的综合指南。本手册演示了如何利用Claude的内置技能创建Excel、PowerPoint和PDF文件，以及如何为专业工作流构建自定义技能。

> **🎯 查看技能实战：** 查看**[Claude创建文件](https://www.anthropic.com/news/create-files)**，了解这些技能如何赋能Claude在Claude.ai和桌面应用中直接创建和编辑文档！

## 什么是Skills？

Skills是组织化的指令包、可执行代码和资源，为Claude提供针对特定任务的专业能力。可以将它们视为Claude可以动态发现和加载的"专业技能包"，用于：

- 创建专业文档（Excel、PowerPoint、PDF、Word）
- 执行复杂的数据分析和可视化
- 应用公司特定的工作流程和品牌
- 自动化具有领域专业知识的业务流程

📖 阅读我们的工程博客文章[用Skills武装智能体应对现实世界](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

## 核心特性

- ✨ **渐进式披露架构** - 技能仅在需要时加载，优化令牌使用
- 📊 **金融领域专注** - 金融和商业分析的真实示例
- 🔧 **自定义技能开发** - 学习构建和部署自己的技能
- 🎯 **生产就绪示例** - 可立即使用的代码，可根据需要调整

## 手册结构

### 📚 [Notebook 1: Skills入门](notebooks/01_skills_introduction.ipynb)

通过快速入门示例学习Claude的Skills功能基础知识。

- 理解Skills架构
- 使用beta标头设置API
- 创建你的第一个Excel电子表格
- 生成PowerPoint演示文稿
- 导出为PDF格式

### 💼 [Notebook 2: 金融应用](notebooks/02_skills_financial_applications.ipynb)

使用真实金融数据探索强大的商业用例。

- 构建带有图表和数据透视表的金融仪表板
- 投资组合分析和投资报告
- 跨格式工作流：CSV → Excel → PowerPoint → PDF
- 令牌优化策略

### 🔧 [Notebook 3: 自定义技能开发](notebooks/03_skills_custom_development.ipynb)

掌握创建自己的专业技能的技巧。

- 构建金融比率计算器
- 创建公司品牌指南技能
- 高级：金融建模套件
- [最佳实践](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices) 和安全考虑

## 快速开始

### 前置条件

- Python 3.8或更高版本
- Anthropic API密钥（[在此获取](https://console.anthropic.com/)）
- Jupyter Notebook或JupyterLab

### 安装

1. **克隆仓库**

```bash
git clone https://github.com/anthropics/claude-cookbooks.git
cd claude-cookbooks/skills
```

2. **创建虚拟环境**（推荐）

```bash
python -m venv venv
source venv/bin/activate  # 在Windows上：venv\Scripts\activate
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

4. **配置API密钥**

```bash
cp .env.example .env
# 编辑.env并添加您的ANTHROPIC_API_KEY
```

5. **启动Jupyter**

```bash
jupyter notebook
```

6. **从Notebook 1开始**
   打开 `notebooks/01_skills_introduction.ipynb` 并跟随学习！

## 示例数据

手册在 `sample_data/` 中包含真实的金融数据集：

- 📊 **financial_statements.csv** - 季度损益表、资产负债表和现金流数据
- 💰 **portfolio_holdings.json** - 带有绩效指标的投资组合
- 📋 **budget_template.csv** - 带差异分析的部门预算
- 📈 **quarterly_metrics.json** - KPI和运营指标

## 项目结构

```
skills/
├── notebooks/                    # Jupyter笔记本
│   ├── 01_skills_introduction.ipynb
│   ├── 02_skills_financial_applications.ipynb
│   └── 03_skills_custom_development.ipynb
├── sample_data/                  # 金融数据集
│   ├── financial_statements.csv
│   ├── portfolio_holdings.json
│   ├── budget_template.csv
│   └── quarterly_metrics.json
├── custom_skills/                # 您的自定义技能
│   ├── financial_analyzer/
│   ├── brand_guidelines/
│   └── report_generator/
├── outputs/                      # 生成的文件
├── docs/                         # 文档
├── requirements.txt             # Python依赖
├── .env.example                 # 环境模板
└── README.md                    # 本文件
```

## API配置

Skills需要特定的beta标头。笔记本会自动处理这一点，但幕后发生的事情如下：

```python
from anthropic import Anthropic

client = Anthropic(
    api_key="your-api-key",
    default_headers={
        "anthropic-beta": "code-execution-2025-08-25,files-api-2025-04-14,skills-2025-10-02"
    }
)
```

**必需的Beta标头：**

- `code-execution-2025-08-25` - 为Skills启用代码执行
- `files-api-2025-04-14` - 下载生成的文件所需
- `skills-2025-10-02` - 启用Skills功能

## 使用生成的文件

当Skills创建文档（Excel、PowerPoint、PDF等）时，它们在响应中返回`file_id`属性。您必须使用**Files API**下载这些文件。

### 工作原理

1. **Skills在代码执行期间创建文件**
2. **响应包含每个创建文件的file_ids**
3. **使用Files API**下载实际文件内容
4. **本地保存**或根据需要处理

### 示例：创建和下载Excel文件

```python
from anthropic import Anthropic

client = Anthropic(api_key="your-api-key")

# 步骤1：使用技能创建文件
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    container={
        "skills": [
            {"type": "anthropic", "skill_id": "xlsx", "version": "latest"}
        ]
    },
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
    messages=[{
        "role": "user",
        "content": "Create an Excel file with a simple budget spreadsheet"
    }]
)

# 步骤2：从响应中提取file_id
file_id = None
for block in response.content:
    if block.type == "tool_result" and hasattr(block, 'output'):
        # 在工具输出中查找file_id
        if 'file_id' in str(block.output):
            file_id = extract_file_id(block.output)  # 解析file_id
            break

# 步骤3：使用Files API下载文件
if file_id:
    file_content = client.beta.files.download(file_id=file_id)

    # 步骤4：保存到磁盘
    with open("outputs/budget.xlsx", "wb") as f:
        f.write(file_content.read())

    print(f"✅ File downloaded: budget.xlsx")
```

### Files API方法

```python
# 下载文件内容（二进制）
content = client.beta.files.download(file_id="file_abc123...")
with open("output.xlsx", "wb") as f:
    f.write(content.read())  # 使用.read()而不是.content

# 获取文件元数据
info = client.beta.files.retrieve_metadata(file_id="file_abc123...")
print(f"Filename: {info.filename}, Size: {info.size_bytes} bytes")  # 使用size_bytes而不是size

# 列出所有文件
files = client.beta.files.list()
for file in files.data:
    print(f"{file.filename} - {file.created_at}")

# 删除文件
client.beta.files.delete(file_id="file_abc123...")
```

**重要提示：**

- 文件临时存储在Anthropic的服务器上
- 下载的文件应保存到您的本地`outputs/`目录
- Files API使用与Messages API相同的API密钥
- 所有笔记本都包含文件下载辅助函数
- **默认会覆盖文件** - 重新运行单元格将替换现有文件（您将在输出中看到`[overwritten]`）

有关完整详情，请参阅[Files API文档](https://docs.claude.com/en/api/files-content)。

## 内置技能参考

Claude附带这些预构建技能：

| 技能         | ID     | 说明                                                    |
| ------------ | ------ | ------------------------------------------------------- |
| Excel        | `xlsx` | 创建和操作带有公式、图表和格式的Excel工作簿            |
| PowerPoint   | `pptx` | 生成带有幻灯片、图表和过渡效果的专业演示文稿            |
| PDF          | `pdf`  | 创建带有文本、表格和图像的格式化PDF文档                |
| Word         | `docx` | 生成具有丰富格式和结构的Word文档                       |

## 创建自定义技能

自定义技能遵循此结构：

```
my_skill/
├── SKILL.md           # 必需：Claude的指令
├── scripts/           # 可选：Python/JS代码
│   └── processor.py
└── resources/         # 可选：模板、数据
    └── template.xlsx
```

在[Notebook 3](notebooks/03_skills_custom_development.ipynb)中了解更多信息。

## 常见用例

### 财务报告

- 自动化季度报告
- 预算差异分析
- 投资绩效仪表板

### 数据分析

- 基于Excel的复杂公式分析
- 数据透视表生成
- 统计分析和可视化

### 文档自动化

- 品牌演示生成
- 多源报告编译
- 跨格式文档转换

## 性能优化技巧

1. **使用渐进式披露**：技能分阶段加载以最小化令牌使用
2. **批量操作**：在单次对话中处理多个文件
3. **技能组合**：结合多个技能实现复杂工作流
4. **缓存重用**：使用容器ID重用已加载的技能

## 故障排除

### 常见问题

**找不到API密钥**

```
ValueError: ANTHROPIC_API_KEY not found
```

→ 确保您已将`.env.example`复制到`.env`并添加了您的密钥

**缺少Skills Beta标头**

```
Error: Skills feature requires beta header
```

→ 确保您使用的是笔记本中所示的正确beta标头

**超出令牌限制**

```
Error: Request exceeds token limit
```

→ 将大型操作分解为较小的块或使用渐进式披露

## 资源

### 文档

- 📖 [Claude API文档](https://docs.anthropic.com/en/api/messages)
- 🔧 [Skills文档](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)

### 支持文章

- 📚 [使用Skills教Claude您的工作方式](https://support.claude.com/en/articles/12580051-teach-claude-your-way-of-working-using-skills) - 使用Skills的用户指南
- 🛠️ [如何通过对话与Claude创建技能](https://support.claude.com/en/articles/12599426-how-to-create-a-skill-with-claude-through-conversation) - 交互式技能创建指南

### 社区与支持

- 💬 [Claude支持](https://support.claude.com)
- 🐙 [GitHub问题](https://github.com/anthropics/claude-cookbooks/issues)

## 贡献

我们欢迎贡献！请查看[CONTRIBUTING.md](../CONTRIBUTING.md)了解指南。

## 许可证

本手册基于MIT许可证提供。详见[LICENSE](../LICENSE)。

## 致谢

特别感谢Anthropic团队开发了Skills功能并提供SDK。

---

**有问题？** 查看[FAQ](docs/FAQ.md)或提出问题。

**准备好开始了吗？** 打开[Notebook 1](notebooks/01_skills_introduction.ipynb)，让我们构建一些令人惊叹的内容！🎉
