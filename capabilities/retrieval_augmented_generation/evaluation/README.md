# 使用Promptfoo进行评估

### 前置条件
使用Promptfoo，您需要在系统上安装node.js和npm。有关更多信息，请遵循[此指南](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)

您可以使用npm安装promptfoo或直接使用npx运行它。在本指南中，我们将使用npx。

*注意：对于此示例，您无需运行`npx promptfoo@latest init`，因为此目录中已有一个初始化的`promptfooconfig.yaml`文件*

查看官方文档[这里](https://www.promptfoo.dev/docs/getting-started)  


### 入门
评估由`promptfooconfig...``.yaml`文件编排。在我们的应用程序中，我们将评估逻辑分为用于评估检索系统的`promptfooconfig_retrieval.yaml`和用于评估端到端性能的`promptfooconfig_end_to_end.yaml`。在每个这些文件中，我们定义以下部分

### 检索评估

- 提示
    - Promptfoo使您能够以许多不同格式导入提示。您可以在[这里](https://www.promptfoo.dev/docs/configuration/parameters)了解更多关于此的信息。
    - 在我们的例子中，我们每次都跳过提供新提示，仅将`{{query}}`传递给每个检索"提供者"进行评估
- 提供者
    - 我们没有使用标准的LLM提供者，而是为`guide.ipynb`中找到的每种检索方法编写了自定义提供者
- 测试
    - 我们将使用与`guide.ipynb`中相同的数据。我们将其拆分为`end_to_end_dataset.csv`和`retrieval_dataset.csv`，并为每个数据集添加了`__expected`列，这使我们能够为每一行自动运行断言
    - 您可以在`eval_end_to_end.py`中找到我们的检索评估逻辑

### 端到端评估

- 提示
    - Promptfoo使您能够以许多不同格式导入提示。您可以在[这里](https://www.promptfoo.dev/docs/configuration/parameters)了解更多关于此的信息。
    - 我们的端到端评估配置中有3个提示：每个对应一种方法使用
        - 这些函数与`guide.ipynb`中使用的函数相同，只是它们不调用Claude API，而是仅返回提示。然后Promptfoo处理调用API和存储结果的编排。
        - 您可以在[这里](https://www.promptfoo.dev/docs/configuration/parameters#prompt-functions)了解更多关于提示函数的信息。使用python使我们能够重用RAG所需的VectorDB类，这定义在`vectordb.py`中。
- 提供者
    - 使用Promptfoo，您可以连接到来自不同平台的许多不同LLM，更多信息请参见[这里](https://www.promptfoo.dev/docs/providers)。在`guide.ipynb`中，我们使用Haiku，默认温度为0.0。我们将使用Promptfoo实验不同的模型。
- 测试
    - 我们将使用与`guide.ipynb`中相同的数据。我们将其拆分为`end_to_end_dataset.csv`和`retrieval_dataset.csv`，并为每个数据集添加了`__expected`列，这使我们能够为每一行自动运行断言
    - Promptfoo有广泛的内置测试，可在[这里](https://www.promptfoo.dev/docs/configuration/expected-outputs/deterministic)找到。
    - 您可以在`eval_retrieval.py`中找到检索系统的测试逻辑，在`eval_end_to_end.py`中找到端到端系统的测试逻辑
- 输出
    - 我们定义输出文件的路径。Promptfoo可以输出多种格式的结果，[参见这里](https://www.promptfoo.dev/docs/configuration/parameters/#output-file)。或者，您可以使用Promptfoo的Web UI，[参见这里](https://www.promptfoo.dev/docs/usage/web-ui)。


### 运行评估

要开始使用Promptfoo，请打开您的终端并导航到此目录（`./evaluation`）。

在运行评估之前，您必须定义以下环境变量：

`export ANTHROPIC_API_KEY=YOUR_API_KEY`
`export VOYAGE_API_KEY=YOUR_API_KEY`

从`evaluation`目录中，运行以下命令之一。

- 要评估端到端系统性能：`npx promptfoo@latest eval -c promptfooconfig_end_to_end.yaml --output ../data/end_to_end_results.json`

- 要单独评估检索系统性能：`npx promptfoo@latest eval -c promptfooconfig_retrieval.yaml --output ../data/retrieval_results.json`

当评估完成时，终端将打印数据集中每一行的结果。您也可以运行`npx promptfoo@latest view`在promptfoo UI查看器中查看输出。