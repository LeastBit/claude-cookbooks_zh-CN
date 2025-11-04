
# 使用Promptfoo进行评估

### 关于本评估套件的说明

1) 请务必遵循下面的说明——特别是关于所需软件包的先决条件。

2) 运行完整的评估套件可能需要高于正常的速率限制。考虑仅在promptfoo中运行测试的子集。

3) 并非每个测试都能开箱即用——我们设计的评估是中等挑战性的。

### 先决条件
要使用Promptfoo，您需要在系统上安装node.js和npm。有关更多信息，请遵循[本指南](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)

您可以使用npm安装promptfoo或使用npx直接运行它。在本指南中，我们将使用npx。

*注意：对于此示例，您不需要运行`npx promptfoo@latest init`，因为此目录中已有一个初始化的`promptfooconfig.yaml`文件*

在此处查看官方文档[here](https://www.promptfoo.dev/docs/getting-started)

#### 注意 - 额外依赖项
对于此示例，您需要安装以下依赖项，以便我们的custom_evals正常运行。

`pip install nltk rouge-score`

### 入门

要开始，请设置您的ANTHROPIC_API_KEY环境变量，或为您选择的提供商设置其他必需的密钥。您可以执行`export ANTHROPIC_API_KEY=YOUR_API_KEY`。

然后，`cd`到`evaluation`目录并写入`npx promptfoo@latest eval -c promptfooconfig.yaml --output ../data/results.csv`

之后，您可以通过运行`npx promptfoo@latest view`查看结果。

### 工作原理

promptfooconfig.yaml文件是我们评估设置的核心。它定义了以下几个关键部分：

提示：
- 提示从prompts.py文件导入。
- 这些提示旨在测试LM性能的各个方面。


提供商：
- 我们在此处配置不同的Claude版本及其设置。
- 这使我们能够跨多个模型或使用不同参数（例如，不同的温度设置）进行测试。


测试：
- 测试用例在此文件中定义，或者在此情况下从tests.yaml导入。
- 这些测试指定了我们评估的输入和预期输出。
- Promptfoo提供各种内置测试类型（请参阅文档），或者您可以定义自己的测试。我们有3个自定义评估和1个开箱即用（包含方法）：
    - `bleu_eval.py`：实现BLEU（双语评估替代）分数，衡量机器生成文本与参考文本之间的相似性。
    - `rouge_eval.py`：实现ROUGE（面向召回的摘要评估替代）分数，通过与参考摘要比较来评估摘要质量。
    - `llm_eval.py`：包含利用语言模型评估生成文本各个方面（如连贯性、相关性或事实准确性）的自定义评估指标。

输出：
- 指定评估结果的格式和位置。
- Promptfoo也支持各种输出格式！

### 覆盖Python二进制文件

默认情况下，promptfoo将在您的shell中运行python。确保python指向适当的可执行文件。

如果不存在python二进制文件，您将看到"python: command not found"错误。

要覆盖Python二进制文件，请设置PROMPTFOO_PYTHON环境变量。您可以将其设置为路径（如/path/to/python3.11）或PATH中的可执行文件（如python3.11）。
