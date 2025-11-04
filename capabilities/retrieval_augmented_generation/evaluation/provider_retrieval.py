import json
import os
from typing import List, Dict
from vectordb import VectorDB, SummaryIndexedVectorDB
from anthropic import Anthropic

# 初始化向量数据库
db = VectorDB("anthropic_docs")
# 加载Claude文档
with open("../data/anthropic_docs.json", "r") as f:
    anthropic_docs = json.load(f)
db.load_data(anthropic_docs)


def retrieve_base(query, options, context):
    input_query = context["vars"]["query"]
    results = db.search(input_query, k=3)
    outputs = []
    for result in results:
        outputs.append(result["metadata"]["chunk_link"])
    print(outputs)
    result = {"output": outputs}
    return result


# 初始化向量数据库
db_summary = SummaryIndexedVectorDB("anthropic_docs_summaries")
# 加载Claude文档
with open("../data/anthropic_summary_indexed_docs.json", "r") as f:
    anthropic_docs_summaries = json.load(f)
db_summary.load_data(anthropic_docs_summaries)


def retrieve_level_two(query, options, context):
    input_query = context["vars"]["query"]
    results = db_summary.search(input_query, k=3)
    outputs = []
    for result in results:
        outputs.append(result["metadata"]["chunk_link"])
    print(outputs)
    result = {"output": outputs}
    return result


def _rerank_results(query: str, results: List[Dict], k: int = 3) -> List[Dict]:
    # 准备带索引的摘要
    summaries = []
    print(len(results))
    for i, result in enumerate(results):
        summary = "[{}] 文档：{} {}".format(
            i, result["metadata"]["chunk_heading"], result["metadata"]["summary"]
        )
        summary += " \n {}".format(result["metadata"]["text"])
        summaries.append(summary)

    # 用换行符连接摘要
    joined_summaries = "\n".join(summaries)

    prompt = f"""
    查询：{query}
    你将收到一组文档，每个文档前都有方括号中的索引号。你的任务是从列表中选择{k}个最相关的文档来帮助我们回答查询。

    {joined_summaries}

    仅输出{k}个最相关文档的索引，按相关性排序，用逗号分隔，用XML标签括起来：
    <relevant_indices>put the numbers of your indices here, seeparted by commas</relevant_indices>
    """

    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=50,
            messages=[
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": "<relevant_indices>"},
            ],
            temperature=0,
            stop_sequences=["</relevant_indices>"],
        )

        # 从响应中提取索引
        response_text = response.content[0].text.strip()
        indices_str = response_text
        relevant_indices = []
        for idx in indices_str.split(","):
            try:
                relevant_indices.append(int(idx.strip()))
            except ValueError:
                continue  # 跳过无效索引
        print(indices_str)
        print(relevant_indices)
        # 如果我们没有获得足够多的有效索引，则回退到按原始顺序的前k个
        if len(relevant_indices) == 0:
            relevant_indices = list(range(min(k, len(results))))

        # 确保我们没有超出范围的索引
        relevant_indices = [idx for idx in relevant_indices if idx < len(results)]

        # 返回重排序的结果
        reranked_results = [results[idx] for idx in relevant_indices[:k]]
        # 分配降序相关性得分
        for i, result in enumerate(reranked_results):
            result["relevance_score"] = (
                100 - i
            )  # 最高得分为100，每个排名递减1

        return reranked_results

    except Exception as e:
        print(f"重排序过程中发生错误：{str(e)}")
        # 回退到返回前k个结果而不重排序
        return results[:k]


# 初始化向量数据库
db_rerank = SummaryIndexedVectorDB("anthropic_docs_summaries_rerank")
# 加载Claude文档
with open("../data/anthropic_summary_indexed_docs.json", "r") as f:
    anthropic_docs_summaries = json.load(f)
db_rerank.load_data(anthropic_docs_summaries)


def retrieve_level_three(query, options, context):
    # 第1步：从摘要数据库获取初始结果
    initial_results = db_rerank.search(query, k=20)

    # 第2步：重新排序结果
    reranked_results = _rerank_results(query, initial_results, k=3)

    # 第3步：从重新排序的结果生成新的上下文字符串
    new_context = ""
    for result in reranked_results:
        chunk = result["metadata"]
        new_context += (
            f"\n <document> \n {chunk['chunk_heading']}\n\n{chunk['text']} \n </document> \n"
        )

    outputs = []
    for result in reranked_results:
        outputs.append(result["metadata"]["chunk_link"])
    print(outputs)
    result = {"output": outputs}
    return result
