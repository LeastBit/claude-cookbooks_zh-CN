# Claude Cookbooks（中文版）

> 本仓库是 [Anthropic 官方 Claude Cookbooks](https://github.com/anthropics/claude-cookbooks) 的中文翻译版本，致力于为中文开发者提供 Claude AI 的使用指南和最佳实践。

## 关于本仓库

Claude Cookbooks 是由 Anthropic 官方提供的实用代码集合和教程，旨在帮助开发者快速掌握和集成 Claude AI 到自己的项目中。本中文版仓库将持续跟进原仓库的更新，为中文开发者提供便捷的学习资源。其翻译内容包括代码中的注释，代码的print的提示文本语句，ipynb中的md文本块，以及用户可读的文档内容。

### 适用人群

- **AI 应用开发者**: 希望将 Claude 集成到产品中的开发人员
- **学习者**: 对大语言模型应用开发感兴趣的初学者和进阶者
- **研究人员**: 探索 AI 助手在不同场景下应用的研究者
- **企业技术团队**: 需要了解 Claude 最佳实践的技术决策者

### 主要内容

本仓库涵盖以下核心主题：

- **基础能力应用**: 分类、检索增强生成、文本总结等基础任务
- **工具使用与集成**: 外部工具调用、函数集成、扩展 Claude 功能
- **第三方服务集成**: 向量数据库、Wikipedia、Web 页面等外部数据源
- **多模态应用**: 图像理解、图表分析、文档处理等视觉任务
- **高级技术**: 子代理、PDF 处理、自动化评估、内容审核等

### 特色

- **可复制的代码**: 每个示例都提供完整的代码片段，可直接运行
- **循序渐进**: 从基础到高级，适合不同水平的开发者
- **最佳实践**: 官方推荐的开发模式和集成方法
- **实用场景**: 涵盖客服、计算器、SQL 查询等真实业务场景
- **持续更新**: 紧跟 Anthropic 最新功能和模型

欢迎PR，纠正错误和提交相关学习笔记和经验笔记：提交笔记命名格式studynote/studynote_github用户名.md

# 原仓库readme:

Claude Cookbooks 提供代码和指南，旨在帮助开发者使用 Claude 进行构建，提供可复制的代码片段，您可以轻松集成到自己的项目中。

## 先决条件

为了充分利用此 cookbook 中的示例，您需要一个 Claude API 密钥（可在此处[免费注册](https://www.anthropic.com/)）。

虽然代码示例主要用 Python 编写，但这些概念可以适用于任何支持与 Claude API 交互的编程语言。

如果您是第一次使用 Claude API，我们建议从我们的 [Claude API 基础课程](https://github.com/anthropics/courses/tree/master/anthropic_api_fundamentals) 开始，以建立坚实的基础。

## 进一步探索

寻找更多资源来增强您与 Claude 和 AI 助手的体验？查看这些有用的链接：

* [Anthropic developer documentation](https://docs.claude.com/claude/docs/guide-to-anthropics-prompt-engineering-resources)
* [Anthropic support docs](https://support.anthropic.com/)
* [Anthropic Discord community](https://www.anthropic.com/discord)

## 贡献

Claude Cookbooks 的发展依赖于开发者社区的贡献。我们重视您的意见，无论是提交想法、修复错字、添加新指南还是改进现有内容。通过贡献，您可以帮助使这个资源对每个人都有价值。

为避免重复工作，请在贡献前查看现有的问题和拉取请求。

如果您对新示例或指南有想法，请在[issues 页面](https://github.com/LeastBit/claude-cookbooks_zh-CN/issues)上分享。

## 食谱清单

### 能力

* [分类](https://github.com/LeastBit/claude-cookbooks_zh-CN/tree/main/capabilities/classification): 探索使用 Claude 进行文本和数据分类的技术。
* [检索增强生成](https://github.com/LeastBit/claude-cookbooks_zh-CN/tree/main/capabilities/retrieval_augmented_generation): 学习如何使用外部知识增强 Claude 的响应。
* [总结](https://github.com/LeastBit/claude-cookbooks_zh-CN/tree/main/capabilities/summarization): 发现使用 Claude 进行有效文本总结的技术。

### 工具使用和集成

* [工具使用](https://github.com/LeastBit/claude-cookbooks_zh-CN/tree/main/tool_use): 学习如何将 Claude 与外部工具和函数集成以扩展其功能。
  * [客服代理](https://github.com/LeastBit/claude-cookbooks_zh-CN/blob/main/tool_use/customer_service_agent.ipynb)
  * [计算器集成](https://github.com/LeastBit/claude-cookbooks_zh-CN/blob/main/tool_use/calculator_tool.ipynb)
  * [SQL 查询](https://github.com/LeastBit/claude-cookbooks_zh-CN/blob/main/misc/how_to_make_sql_queries.ipynb)

### 第三方集成

* [检索增强生成](https://github.com/LeastBit/claude-cookbooks_zh-CN/tree/main/third_party): 使用外部数据源补充 Claude 的知识。
  * [向量数据库 (Pinecone)](https://github.com/LeastBit/claude-cookbooks_zh-CN/blob/main/third_party/Pinecone/rag_using_pinecone.ipynb)
  * [维基百科](https://github.com/LeastBit/claude-cookbooks_zh-CN/blob/main/third_party/Wikipedia/wikipedia-search-cookbook.ipynb/)
  * [网页](https://github.com/LeastBit/claude-cookbooks_zh-CN/blob/main/misc/read_web_pages_with_haiku.ipynb)
* [使用 Voyage AI 进行嵌入](https://github.com/LeastBit/claude-cookbooks_zh-CN/blob/main/third_party/VoyageAI/how_to_create_embeddings.md)

### 多模态能力

* [使用 Claude 进行视觉](https://github.com/LeastBit/claude-cookbooks_zh-CN/tree/main/multimodal):
  * [图像入门](https://github.com/LeastBit/claude-cookbooks_zh-CN/blob/main/multimodal/getting_started_with_vision.ipynb)
  * [视觉最佳实践](https://github.com/LeastBit/claude-cookbooks_zh-CN/blob/main/multimodal/best_practices_for_vision.ipynb)
  * [解释图表和图形](https://github.com/LeastBit/claude-cookbooks_zh-CN/blob/main/multimodal/reading_charts_graphs_powerpoints.ipynb)
  * [从表单中提取内容](https://github.com/LeastBit/claude-cookbooks_zh-CN/blob/main/multimodal/how_to_transcribe_text.ipynb)
* [使用 Claude 生成图像](https://github.com/LeastBit/claude-cookbooks_zh-CN/blob/main/misc/illustrated_responses.ipynb): 将 Claude 与 Stable Diffusion 结合使用进行图像生成。

### 高级技术

* [子代理](https://github.com/LeastBit/claude-cookbooks_zh-CN/blob/main/multimodal/using_sub_agents.ipynb): 学习如何将 Haiku 作为子代理与 Opus 结合使用。
* [上传 PDF 到 Claude](https://github.com/LeastBit/claude-cookbooks_zh-CN/blob/main/misc/pdf_upload_summarization.ipynb): 解析并将 PDF 作为文本传递给 Claude。
* [自动化评估](https://github.com/LeastBit/claude-cookbooks_zh-CN/blob/main/misc/building_evals.ipynb): 使用 Claude 自动化提示评估过程。
* [启用 JSON 模式](https://github.com/LeastBit/claude-cookbooks_zh-CN/blob/main/misc/how_to_enable_json_mode.ipynb): 确保从 Claude 输出一致的 JSON。
* [创建内容审核过滤器](https://github.com/LeastBit/claude-cookbooks_zh-CN/blob/main/misc/building_moderation_filter.ipynb): 使用 Claude 为您的应用程序创建内容审核过滤器。
* [提示缓存](https://github.com/LeastBit/claude-cookbooks_zh-CN/blob/main/misc/prompt_caching.ipynb): 学习使用 Claude 进行高效提示缓存的技术。

## 其他资源

* [AWS 上的 Anthropic](https://github.com/aws-samples/anthropic-on-aws): 探索在 AWS 基础设施上使用 Claude 的示例和解决方案。
* [AWS 示例](https://github.com/aws-samples/): 来自 AWS 的代码示例集合，可以适配与 Claude 一起使用。请注意，某些示例可能需要修改才能与 Claude 最佳配合工作。
