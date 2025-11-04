# 构建高效代理指南手册

Erik Schluntz 和 Barry Zhang 的[构建高效代理](https://anthropic.com/research/building-effective-agents)参考实现。

本仓库包含博客中讨论的常见代理工作流程的最小实现示例：

- 基本构建模块
  - 提示链
  - 路由
  - 多LLM并行化
- 高级工作流程
  - 协调器-子代理
  - 评估器-优化器

## 开始使用
查看Jupyter笔记本以获取详细示例：

- [基本工作流程](basic_workflows.ipynb)
- [评估器-优化器工作流程](evaluator_optimizer.ipynb)
- [协调器-工作者工作流程](orchestrator_workers.ipynb)
