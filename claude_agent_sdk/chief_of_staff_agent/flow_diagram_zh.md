# 首席助理代理架构

```mermaid
graph TD
    User[用户] --> Chief[首席助理代理]
    Chief --> Memory[CLAUDE.md]
    Chief --> FinData[财务数据/]
    Chief --> Tools[工具]
    Chief --> Commands[斜杠命令]
    Chief --> Styles[输出样式]
    Chief --> Hooks[钩子]

    Tools --> Task[任务工具]
    Task --> FA[财务分析师]
    Task --> Recruiter[招聘专员]

    FA --> Scripts1[Python脚本]
    Recruiter --> Scripts2[Python脚本]

    style Chief fill:#f9f,stroke:#333,stroke-width:3px
    style Task fill:#bbf,stroke:#333,stroke-width:2px
    style FA fill:#bfb,stroke:#333,stroke-width:2px
    style Recruiter fill:#bfb,stroke:#333,stroke-width:2px
```

## 预期的代理通信流程

```mermaid
sequenceDiagram
    participant User[用户]
    participant Chief[首席助理]
    participant Task[任务工具]
    participant FA[财务分析师]
    participant Scripts[Python脚本]
    participant Hooks[写后钩子]
    User->>Chief: /budget-impact 招聘5名工程师
    Chief->>Chief: 展开斜杠命令
    Chief->>Task: 委托财务分析
    Task->>FA: 分析招聘影响
    FA->>Scripts: 执行hiring_impact.py
    Scripts-->>FA: 返回分析结果
    FA->>FA: 生成报告
    FA-->>Task: 返回发现
    Task-->>Chief: 子代理结果
    Chief->>Chief: 将报告写入磁盘
    Chief->>Hooks: 触发写后钩子
    Hooks->>Hooks: 记录到审计跟踪
    Chief-->>User: 执行摘要
```

  根目录文件

  1. agent.py - 首席助理代理主文件
  2. CLAUDE.md - 公司背景和上下文文档
  3. flow_diagram.md - 架构流程图文档

  scripts/ 目录（5个Python文件）

  1. simple_calculation.py - 简单财务计算器
  2. financial_forecast.py - 财务预测工具
  3. hiring_impact.py - 招聘影响计算器
  4. talent_scorer.py - 人才评分工具
  5. decision_matrix.py - 决策矩阵工具

  output_reports/ 目录（2个markdown文件）

  1. hiring_decision.md - 招聘决策预算影响分析报告
  2. Q2_2024_Financial_Forecast.md - 2024年第二季度财务预测报告

  .claude/ 目录（10个文档文件）

  agents/ 子目录：
  1. financial-analyst.md - 财务分析师代理文档
  2. recruiter.md - 招聘专员代理文档

  commands/ 子目录：
  1. budget-impact.md - 预算影响分析命令
  2. strategic-brief.md - 战略简报命令
  3. talent-scan.md - 人才扫描命令
  4. slash-command-test.md - 斜杠命令测试

  hooks/ 子目录：
  1. report-tracker.py - 报告跟踪钩子
  2. script-usage-logger.py - 脚本使用日志钩子

  output-styles/ 子目录：
  1. executive.md - 高管输出样式
  2. technical.md - 技术输出样式

