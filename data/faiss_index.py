# data/faiss_index.py
import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings

def get_faiss_index():
    # 此处简单示例，假设已经构建好向量库并存储在 disk_index 目录中
    index_path = "data/faiss_index.index"
    if os.path.exists(index_path):
        # 加载现有索引
        index = FAISS.load_local(index_path, OpenAIEmbeddings())
    else:
        # 构建新索引（示例数据）
        texts = [
            "鸡禽养殖过程中需要注意饲料的配比和环境温湿度。",
            "常见疾病包括禽流感、鸡新城疫等，需定期疫苗接种。",
            "实时监控系统可以帮助及时发现环境异常。"
        ]
        index = FAISS.from_texts(texts, OpenAIEmbeddings())
        index.save_local(index_path)
    return index
