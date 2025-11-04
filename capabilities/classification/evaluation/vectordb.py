import os
import numpy as np
import voyageai
import pickle
import json


class VectorDB:
    def __init__(self, api_key=None):
        if api_key is None:
            api_key = os.getenv("VOYAGE_API_KEY")
        self.client = voyageai.Client(api_key=api_key)
        self.embeddings = []
        self.metadata = []
        self.query_cache = {}
        self.db_path = "../data/vector_db.pkl"

    def load_data(self, data):
        # 检查向量数据库是否已经加载
        if self.embeddings and self.metadata:
            print("向量数据库已加载。跳过数据加载。")
            return
        # 检查 vector_db.pkl 是否存在
        if os.path.exists(self.db_path):
            print("从磁盘加载向量数据库。")
            self.load_db()
            return

        texts = [item["text"] for item in data]

        # 使用 for 循环嵌入超过 128 个文档
        batch_size = 128
        result = [
            self.client.embed(texts[i : i + batch_size], model="voyage-2").embeddings
            for i in range(0, len(texts), batch_size)
        ]

        # 扁平化嵌入
        self.embeddings = [embedding for batch in result for embedding in batch]
        self.metadata = [item for item in data]
        # 将向量数据库保存到磁盘
        print("向量数据库已加载并保存。")

    def search(self, query, k=5, similarity_threshold=0.85):
        query_embedding = None
        if query in self.query_cache:
            query_embedding = self.query_cache[query]
        else:
            query_embedding = self.client.embed([query], model="voyage-2").embeddings[0]
            self.query_cache[query] = query_embedding

        if not self.embeddings:
            raise ValueError("向量数据库中未加载数据。")

        similarities = np.dot(self.embeddings, query_embedding)
        top_indices = np.argsort(similarities)[::-1]
        top_examples = []

        for idx in top_indices:
            if similarities[idx] >= similarity_threshold:
                example = {
                    "metadata": self.metadata[idx],
                    "similarity": similarities[idx],
                }
                top_examples.append(example)

                if len(top_examples) >= k:
                    break

        return top_examples

    def load_db(self):
        if not os.path.exists(self.db_path):
            raise ValueError(
                "未找到向量数据库文件。使用 load_data 创建新数据库。"
            )

        with open(self.db_path, "rb") as file:
            data = pickle.load(file)
        self.embeddings = data["embeddings"]
        self.metadata = data["metadata"]
        self.query_cache = json.loads(data["query_cache"])
