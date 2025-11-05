# 文本嵌入
文本嵌入是文本字符串的数值表示，表示为浮点数向量。我们可以使用两个文本嵌入之间的距离（常用余弦相似度）来衡量两段文本之间的相关性，距离越小表示相关性越高。

比较字符串的相似性，或根据字符串之间的距离对字符串进行聚类，可以实现多种应用，包括**搜索**（在RAG架构中很流行）、**推荐**和**异常检测**。

## 如何使用Anthropic获取嵌入
虽然Anthropic不提供自己的嵌入模型，但我们与[Voyage AI](https://www.voyageai.com/?ref=anthropic)合作，作为我们文本嵌入的首选提供商。Voyage提供[最先进](https://blog.voyageai.com/2023/10/29/voyage-embeddings/?ref=anthropic)的嵌入模型，甚至提供为特定行业领域定制的模型，如金融和医疗保健领域，以及可以为您的公司微调的模型。

要访问Voyage嵌入，请首先在[Voyage AI网站](https://dash.voyageai.com/?ref=anthropic)上注册，获取API密钥，并为了方便将API密钥设置为环境变量：

```bash
export VOYAGE_API_KEY="<your secret key>"
```

您可以使用官方的[`voyageai` Python包](https://github.com/voyage-ai/voyageai-python)或HTTP请求来获取嵌入，如下所述。

### Voyage Python包

可以使用以下命令安装`voyageai`包：

```bash
pip install -U voyageai
```

然后，您可以创建一个客户端对象并开始使用它来嵌入您的文本：

```python
import voyageai

vo = voyageai.Client()
# 这将自动使用环境变量 VOYAGE_API_KEY。
# 或者，您可以使用 vo = voyageai.Client(api_key="<your secret key>")

texts = ["Sample text 1", "Sample text 2"]

result = vo.embed(texts, model="voyage-2", input_type="document")
print(result.embeddings[0])
print(result.embeddings[1])
```

`result.embeddings`将是一个包含两个嵌入向量的列表，每个向量包含1024个浮点数。运行上述代码后，两个嵌入将在屏幕上打印：

```
[0.02012746, 0.01957859, ...]  # "Sample text 1"的嵌入
[0.01429677, 0.03077182, ...]  # "Sample text 2"的嵌入
```

创建嵌入时，您可以为`embed()`函数指定一些其他参数。规范如下：

> `voyageai.Client.embed(texts : List[str], model : str = "voyage-2", input_type : Optional[str] = None, truncation : Optional[bool] = None)`

- **texts** (List[str]) - 文本列表，例如`["I like cats", "I also like dogs"]`。目前，列表的最大长度为128，列表中标记的总数在`voyage-2`中最多为320K，在`voyage-code-2`中最多为120K。
- **model** (str) - 模型名称。推荐选项：`voyage-2`（默认）、`voyage-code-2`。
- **input_type** (str, optional, defaults to `None`) - 输入文本的类型。默认为`None`。其他选项：`query`、`document`。
    - 当input_type设置为`None`时，输入文本将由我们的嵌入模型直接编码。另外，当输入是文档或查询时，用户可以分别指定input_type为`query`或`document`。在这种情况下，Voyage将在输入文本前添加特殊提示，并将扩展的输入发送给嵌入模型。
    - 对于检索/搜索用例，我们建议在编码查询或文档时指定此参数以提高检索质量。使用和未使用input_type参数生成的嵌入是兼容的。

- **truncation** (bool, optional, defaults to `None`) - 是否截断输入文本来适应上下文长度。
    - 如果为`True`，超长的输入文本将在被嵌入模型向量化之前被截断以适应上下文长度。
    - 如果为`False`，如果任何给定文本超出上下文长度，将引发错误。
    - 如果未指定（默认为`None`），如果输入文本稍微超出上下文窗口长度，Voyage将在发送给嵌入模型之前截断输入文本。如果显著超出上下文窗口长度，将引发错误。

### Voyage HTTP API

您还可以通过请求Voyage HTTP API来获取嵌入。例如，您可以通过终端中的`curl`命令发送HTTP请求：

```bash
curl https://api.voyageai.com/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $VOYAGE_API_KEY" \
  -d '{
    "input": ["Sample text 1", "Sample text 2"],
    "model": "voyage-2"
  }'
```

您将获得的响应是一个包含嵌入和标记使用情况的JSON对象：

```bash
{
  "object": "list",
  "data": [
    {
      "embedding": [0.02012746, 0.01957859, ...],
      "index": 0
    },
    {
      "embedding": [0.01429677, 0.03077182, ...],
      "index": 1
    }
  ],
  "model": "voyage-2",
  "usage": {
    "total_tokens": 10
  }
}
```

Voyage AI的嵌入端点是`https://api.voyageai.com/v1/embeddings`（POST）。请求头必须包含API密钥。请求体是一个包含以下参数的JSON对象：

- **input** (str, List[str]) - 单个文本字符串，或文本列表。目前，列表的最大长度为128，列表中标记的总数在`voyage-2`中最多为320K，在`voyage-code-2`中最多为120K。
- **model** (str) - 模型名称。推荐选项：`voyage-2`（默认）、`voyage-code-2`。
- **input_type** (str, optional, defaults to `None`) - 输入文本的类型。默认为`None`。其他选项：`query`、`document`。
- **truncation** (bool, optional, defaults to `None`) - 是否截断输入文本来适应上下文长度。
    - 如果为`True`，超长的输入文本将在被嵌入模型向量化之前被截断以适应上下文长度。
    - 如果为`False`，如果任何给定文本超出上下文长度，将引发错误。
    - 如果未指定（默认为`None`），如果输入文本稍微超出上下文窗口长度，Voyage将在发送给嵌入模型之前截断输入文本。如果显著超出上下文窗口长度，将引发错误。
- **encoding_format** (str, optional, default to `None`) - 嵌入编码的格式。Voyage目前支持两个选项：
    - 如果未指定（默认为`None`）：嵌入表示为浮点数列表；
    - `"base64"`：嵌入压缩为[Base64](https://docs.python.org/3/library/base64.html)编码。


### AWS Marketplace

Voyage嵌入在[AWS Marketplace](https://aws.amazon.com/marketplace/seller-profile?id=seller-snt4gb6fd7ljg)上可用。以下是在AWS上访问Voyage的说明：

1. 订阅模型包

    1. 导航到[模型包列表页面](https://aws.amazon.com/marketplace/seller-profile?id=seller-snt4gb6fd7ljg)并选择要部署的模型。
    1. 点击*继续订阅*按钮。
    1. 在*订阅此软件*页面上，请仔细查看详细信息。如果您和您的组织同意标准最终用户许可协议（EULA）、定价和支持条款，请点击"接受要约"。
    1. 选择*继续配置*并选择区域后，您将看到一个产品ARN。这是使用Boto3创建可部署模型所需的模型包ARN。复制与您选择的区域对应的ARN，并在后续单元格中使用它。

2. 部署模型包

    从现在开始，我们建议您在[Sagemaker Studio](https://aws.amazon.com/sagemaker/studio/)中继续使用我们提供的[笔记本](https://github.com/voyage-ai/voyageai-aws/blob/main/notebooks/deploy_voyage_code_2_sagemaker.ipynb)。请创建一个JupyterLab空间，上传我们的笔记本，然后从那里继续。


## 可用模型

Voyage推荐使用以下嵌入模型：

|  模型 | 上下文长度 | 嵌入维度 | 描述 |
| --- | --- | --- | --- |
| `voyage-2` | 4000 | 1024 | 最新的基础（通用）嵌入模型，具有最佳的检索质量。详细信息请参见[博客文章](https://blog.voyageai.com/2023/10/29/voyage-embeddings/?ref=anthropic)。 |
| `voyage-code-2` | 16000 | 1536 | 针对代码检索进行了优化（比其他替代方案好17%），在通用语料库上也是最先进的。详细信息请参见[博客文章](https://blog.voyageai.com/2024/01/23/voyage-code-2-elevate-your-code-retrieval/?ref=anthropic)。 |

`voyage-2`是一个通用嵌入模型，在各个领域都达到了最先进的性能，并保持了高效率。`voyage-code-2`针对代码应用进行了优化，提供4倍的上下文长度以实现更灵活的使用，尽管延迟稍高一些。

Voyage正在积极开发更先进和专业的模型，并且可以为您的公司微调嵌入。请发送邮件至[contact@voyageai.com](mailto:contact@voyageai.com)获取试用访问或对您自己的数据进行微调！

- `voyage-finance-2`：即将推出
- `voyage-law-2`：即将推出
- `voyage-multilingual-2`：即将推出
- `voyage-healthcare-2`：即将推出

## 激励示例
现在我们了解了如何获取嵌入，让我们看一个简短的激励示例。

假设我们有一个包含六个文档的小语料库需要检索

```python
documents = [
    "The Mediterranean diet emphasizes fish, olive oil, and vegetables, believed to reduce chronic diseases.",
    "Photosynthesis in plants converts light energy into glucose and produces essential oxygen.",
    "20th-century innovations, from radios to smartphones, centered on electronic advancements.",
    "Rivers provide water, irrigation, and habitat for aquatic species, vital for ecosystems.",
    "Apple’s conference call to discuss fourth fiscal quarter results and business updates is scheduled for Thursday, November 2, 2023 at 2:00 p.m. PT / 5:00 p.m. ET.",
    "Shakespeare's works, like 'Hamlet' and 'A Midsummer Night's Dream,' endure in literature."
]
```

我们将首先使用Voyage将每个文档转换为嵌入向量

```python
import voyageai

vo = voyageai.Client()

# 嵌入文档
doc_embds = vo.embed(
    documents, model="voyage-2", input_type="document"
).embeddings
```

嵌入将使我们能够在向量空间中进行语义搜索/检索。给定一个示例查询，

```python
query = "When is Apple's conference call scheduled?"
```

我们将其转换为嵌入，并进行最近邻搜索，以根据嵌入空间中的距离找到最相关的文档。

```python
import numpy as np

# 嵌入查询
query_embd = vo.embed(
    [query], model="voyage-2", input_type="query"
).embeddings[0]

# 计算相似性
# Voyage嵌入归一化为长度1，因此点积
# 和余弦相似度是相同的。
similarities = np.dot(doc_embds, query_embd)

retrieved_id = np.argmax(similarities)
print(documents[retrieved_id])
```

请注意，我们分别使用`input_type="document"`和`input_type="query"`来嵌入文档和查询。更多规范可以在[这里](#voyage-python-package)找到。

输出将是第5个文档，这确实与查询最相关：

```
Apple's conference call to discuss fourth fiscal quarter results and business updates is scheduled for Thursday, November 2, 2023 at 2:00 p.m. PT / 5:00 p.m. ET.
```

如果您正在寻找关于如何使用嵌入（包括向量数据库）进行RAG的详细教程，请查看我们的[RAG教程](https://github.com/anthropics/anthropic-cookbook/blob/main/third_party/Pinecone/rag_using_pinecone.ipynb)。

## 常见问题
### 如何计算两个嵌入向量之间的距离？
余弦相似度是一个流行的选择，但大多数距离函数都可以。Voyage嵌入归一化为长度1，因此余弦相似度本质上是两个向量之间的点积。以下是您可以用来计算两个嵌入向量之间余弦相似度的代码片段。

```python
import numpy

similarity = np.dot(embd1, embd2)
# Voyage嵌入归一化为长度1，因此余弦相似度
# 与点积相同。
```

如果您想要在大语料库中找到K个最近的嵌入向量，我们建议使用大多数向量数据库内置的功能。

### 我可以在嵌入之前计算字符串中的标记数量吗？
可以！您可以使用以下代码来做到这一点。

```python
import voyageai

vo = voyageai.Client()
total_tokens = vo.count_tokens(["Sample text"])
```

## 定价
定价信息可在Voyage网站的[定价页面](https://docs.voyageai.com/pricing/?ref=anthropic)上查看，请在那里查看。
