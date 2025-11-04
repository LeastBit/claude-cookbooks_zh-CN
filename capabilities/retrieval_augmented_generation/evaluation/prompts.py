import json
import os
from typing import List, Dict, Tuple
from vectordb import VectorDB, SummaryIndexedVectorDB
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# 初始化向量数据库
db = VectorDB("anthropic_docs")
# 加载Claude文档
with open("../data/anthropic_docs.json", "r") as f:
    anthropic_docs = json.load(f)
db.load_data(anthropic_docs)


def _retrieve_base(query, db):
    results = db.search(query, k=3)
    context = ""
    for result in results:
        chunk = result["metadata"]
        context += f"\n{chunk['text']}\n"
    return results, context


def answer_query_base(context):
    input_query = context["vars"]["query"]
    documents, document_context = _retrieve_base(input_query, db)
    prompt = f"""
    你的任务是帮助我们回答以下查询：
    <query>
    {input_query}
    </query>
    你可以访问以下文档，它们旨在为回答查询提供上下文：
    <documents>
    {document_context}
    </documents>
    请忠实于底层上下文，只有在100%确定自己已经知道答案的情况下才偏离它。
    现在回答问题，避免提供前言，例如"以下是答案"等
    """

    return prompt


# 初始化向量数据库
db_summary = SummaryIndexedVectorDB("anthropic_docs_summaries")
# 加载Claude文档
with open("../data/anthropic_summary_indexed_docs.json", "r") as f:
    anthropic_docs_summaries = json.load(f)
db_summary.load_data(anthropic_docs_summaries)


def retrieve_level_two(query):
    results = db_summary.search(query, k=3)
    context = ""
    for result in results:
        chunk = result["metadata"]
        context += f"\n <document> \n {chunk['chunk_heading']}\n\n文本\n {chunk['text']} \n\n摘要：\n {chunk['summary']} \n </document> \n"  # 向模型展示所有3项内容
    return results, context


def answer_query_level_two(context):
    input_query = context["vars"]["query"]
    documents, document_context = retrieve_level_two(input_query)
    prompt = f"""
    你的任务是帮助我们回答以下查询：
    <query>
    {input_query}
    </query>
    你可以访问以下文档，它们旨在为回答查询提供上下文：
    <documents>
    {document_context}
    </documents>
    请忠实于底层上下文，只有在100%确定自己已经知道答案的情况下才偏离它。
    现在回答问题，避免提供前言，例如"以下是答案"等
    """

    return prompt


# 初始化向量数据库
db_rerank = SummaryIndexedVectorDB("anthropic_docs_rerank")
# 加载Claude文档
with open("../data/anthropic_summary_indexed_docs.json", "r") as f:
    anthropic_docs_summaries = json.load(f)
db_rerank.load_data(anthropic_docs_summaries)


def _rerank_results(query: str, results: List[Dict], k: int = 5) -> List[Dict]:
    # 准备带索引的摘要
    summaries = []
    print(len(results))
    for i, result in enumerate(results):
        summary = "[{}] Document: {} {}".format(
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
    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
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


def _retrieve_advanced(query: str, k: int = 3, initial_k: int = 20) -> Tuple[List[Dict], str]:
    # 第1步：获取初始结果
    initial_results = db_rerank.search(query, k=initial_k)

    # 第2步：重新排序结果
    reranked_results = _rerank_results(query, initial_results, k=k)

    # 第3步：从重新排序的结果生成新的上下文字符串
    new_context = ""
    for result in reranked_results:
        chunk = result["metadata"]
        new_context += (
            f"\n <document> \n {chunk['chunk_heading']}\n\n{chunk['text']} \n </document> \n"
        )

    return reranked_results, new_context


# answer_query_advanced函数保持不变
def answer_query_level_three(context):
    input_query = context["vars"]["query"]
    documents, document_context = _retrieve_advanced(input_query)
    prompt = f"""
    你的任务是帮助我们回答以下查询：
    <query>
    {input_query}
    </query>
    你可以访问以下文档，它们旨在为回答查询提供上下文：
    <documents>
    {document_context}
    </documents>
    请忠实于底层上下文，只有在100%确定自己已经知道答案的情况下才偏离它。
    现在回答问题，避免提供前言，例如"以下是答案"等
    """
    return prompt
