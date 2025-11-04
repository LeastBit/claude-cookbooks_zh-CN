# 使用 Promptfoo 进行评估



### 前提条件
使用 Promptfoo 需要在系统上安装 node.js 和 npm。有关更多信息，请遵循 [此指南](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)

您可以使用 npm 安装 promptfoo 或直接使用 npx 运行它。在本指南中我们将使用 npx。

*注意：在此示例中，您不需要运行 `npx promptfoo@latest init`，因为此目录中已有一个初始化的 `promptfooconfig.yaml` 文件*

查看官方文档 [此处](https://www.promptfoo.dev/docs/getting-started)



### 入门指南
评估由 `promptfooconfig.yaml` 文件编排。在此文件中，我们定义以下部分：

- 提示词
    - Promptfoo 使您能够以多种不同格式导入提示词。您可以在 [此处](https://www.promptfoo.dev/docs/configuration/parameters) 了解更多信息。
    - 在此示例中，我们将加载 3 个提示词 - 与 `guide.ipynb` 中使用的相同，来自 `prompts.py` 文件：
        - 这些函数与 `guide.ipynb` 中使用的函数相同，只是它们不调用 Claude API，而是只返回提示词。Promptfoo 然后处理 API 调用和存储结果的编排。
        - 您可以在 [此处](https://www.promptfoo.dev/docs/configuration/parameters#prompt-functions) 了解有关提示词函数的更多信息。使用 python 使我们能够重用 RAG 所需的 VectorDB 类，这是在 `vectordb.py` 中定义的。
- 提供者
    - 使用 Promptfoo，您可以连接到来自不同平台的许多不同 LLM，查看 [此处了解更多](https://www.promptfoo.dev/docs/providers)。在 `guide.ipynb` 中，我们使用默认温度 0.0 的 Haiku。我们将使用 Promptfoo 来实验一系列不同的温度设置，以确定我们用例的最佳选择。
- 测试
    - 我们将使用与 `guide.ipynb` 中使用的数据相同的数据，该数据可以在此 [Google 表格](https://docs.google.com/spreadsheets/d/1UwbrWCWsTFGVshyOfY2ywtf5BEt7pUcJEGYZDkfkufU/edit#gid=0) 中找到。
    - Promptfoo 有广泛的内置测试，可以在 [此处](https://www.promptfoo.dev/docs/configuration/expected-outputs/deterministic) 找到。
    - 在此示例中，我们将在 `dataset.csv` 中定义一个测试，因为评估条件随每行而变化，在 `promptfooconfig.yaml` 中定义一个测试，用于所有测试用例一致的条件。在 [此处](https://www.promptfoo.dev/docs/configuration/parameters/#import-from-csv) 了解更多
- 转换
    - 在 `defaultTest` 部分我们定义一个转换函数。这是一个 python 函数，用于从 LLM 响应中提取我们想要测试的特定输出。
- 输出
    - 我们定义输出文件的路径。Promptfoo 可以输出多种格式的结果，[见此处](https://www.promptfoo.dev/docs/configuration/parameters/#output-file)。或者您可以使用 Promptfoo 的 Web UI，[见此处](https://www.promptfoo.dev/docs/usage/web-ui)。


### 运行评估

开始使用 Promptfoo，请打开您的终端并导航到此目录 (`./evaluation`)。

在运行评估之前，您必须定义以下环境变量：

`export ANTHROPIC_API_KEY=YOUR_API_KEY`
`export VOYAGE_API_KEY=YOUR_API_KEY`

从 `evaluation` 目录，运行以下命令。

`npx promptfoo@latest eval`

如果您想增加请求的并发数（默认 = 4），运行以下命令。

`npx promptfoo@latest eval -j 25`

当评估完成时，终端将打印数据集中每行的结果。

您现在可以回到 `guide.ipynb` 来分析结果！


