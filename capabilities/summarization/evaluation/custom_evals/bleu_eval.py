import numpy as np
from typing import Dict, Union, Any
import nltk
from nltk.translate.bleu_score import sentence_bleu
from nltk.tokenize import word_tokenize

# 下载所需的NLTK数据
nltk.download("punkt", quiet=True)


def nltk_bleu_eval(output, ground_truth) -> float:
    """
    使用NLTK计算BLEU分数并与阈值进行比较。

    Args:
    output (str): 要评估的输出。
    ground_truth (str): 基准真相输出。
    threshold (float): BLEU分数的阈值（默认：0.5）。

    Returns:
    tuple: (float, bool) - BLEU分数以及是否通过阈值。
    """
    # 对摘要进行分词
    output_tokens = word_tokenize(output.lower())
    ground_truth_tokens = word_tokenize(ground_truth.lower())

    try:
        # 计算BLEU分数
        # 注意：sentence_bleu期望引用列表，因此我们将reference_tokens包装在列表中
        bleu_score = sentence_bleu(
            [ground_truth_tokens], output_tokens, weights=(0.25, 0.25, 0.25, 0.25)
        )

        # 确保bleu_score是浮点数
        if isinstance(bleu_score, (int, float)):
            bleu_score_float = float(bleu_score)
        elif isinstance(bleu_score, (list, np.ndarray)):
            # 如果是列表或数组，取平均值
            bleu_score_float = float(np.mean(bleu_score))
        else:
            # 如果既不是数字也不是列表，默认设为0
            print(f"警告：意外的BLEU分数类型：{type(bleu_score)}。默认设为0。")
            bleu_score_float = 0.0
    except Exception as e:
        print(f"计算BLEU分数时出错：{e}。默认设为0。")
        bleu_score_float = 0.0

    # 返回BLEU分数以及是否通过阈值
    return bleu_score_float


def get_assert(output: str, context, threshold=0.3) -> Union[bool, float, Dict[str, Any]]:
    ground_truth = context["vars"]["ground_truth"]
    score = nltk_bleu_eval(output, ground_truth)

    if score >= threshold:
        return {"pass": True, "score": score, "reason": "平均分数高于阈值"}
    else:
        return {"pass": False, "score": score, "reason": "平均分数低于阈值"}
