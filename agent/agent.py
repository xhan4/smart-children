import os
import sys
current_script_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_script_path))
sys.path.append(project_root)
import subprocess
from langchain.agents import initialize_agent, Tool
from langchain.llms.base import LLM
from langchain.chains import RetrievalQA
from external.weather_api import get_weather

# from external.market_api import get_market_price
# from data.faiss_index import get_faiss_index
from pydantic import Field  # 导入 Field

class DeepSeekLLM(LLM):
    """自定义调用本地 DeepSeek 模型的 LLM 封装器"""
    model_command: str = Field(default="", description="命令行命令，用于调用本地模型")

    def __init__(self, model_command: str):
        super().__init__(model_command=model_command)  # 使用 Pydantic 的初始化方法

    @property
    def _llm_type(self) -> str:
        return "deepseek"

    def _call(self, prompt: str, stop=None) -> str:
        # 调用本地命令行工具执行模型推理
        process = subprocess.Popen(
            self.model_command.split() + [prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",  # 显式指定编码
            errors="replace"   # 替换无法解码的字符
        )
        stdout, stderr = process.communicate()
        if stderr:
            print("Error:", stderr)
        if stdout is None:
            return ""  # 如果 stdout 为 None，返回空字符串
        return stdout.strip()

def get_agent():
    # # 初始化向量检索工具，封装为 LangChain 的 Tool 类型
    # def faiss_search(query: str) -> str:
    #     index = get_faiss_index()  # 获取预构建的 FAISS 索引对象
    #     docs = index.similarity_search(query, k=3)
    #     return "\n".join([doc.page_content for doc in docs])
    
    # vector_tool = Tool(
    #     name="向量检索工具",
    #     func=faiss_search,
    #     description="通过向量数据库检索相关知识，输入查询内容，返回相关文档摘要"
    # )

    # 外部数据调用工具（例如天气查询）
    def weather_tool(query: str) -> str:
        return get_weather(query)

    weather_data_tool = Tool(
        name="天气查询工具",
        func=weather_tool,
        description="输入地名，返回当前天气信息"
    )
    # market_price_tool = Tool(
    #     name="市场价格查询工具",
    #     func=MarketPriceTool()._run,  # 使用 MarketPriceTool 的 _run 方法
    #     description="输入农产品名称和地区（格式：<产品名称>,<地区>），返回市场价格"
    # )
    # 初始化 DeepSeek 模型
    deepseek_llm = DeepSeekLLM("ollama run deepseek-r1:1.5b")

    # # 使用 LangChain 的 RetrievalQA 作为基础问答链，结合向量检索工具
    # retrieval_qa = RetrievalQA.from_chain_type(
    #     llm=deepseek_llm,
    #     chain_type="stuff",   # 此处可根据需要选择不同 chain 模型
    #     retriever=get_faiss_index()  # FAISS 检索器
    # )

    # 整合 agent，可加入多个工具
    agent = initialize_agent(
        tools=[weather_data_tool],
        llm=deepseek_llm,
        agent="zero-shot-react-description",
        verbose=True,# 输出详细日志
        handle_parsing_errors=True # 自动处理解析错误
    )
    return agent

if __name__ == "__main__":
    agent = get_agent()
    query = input("请输入您的问题：")
    answer = agent.run(query)
    print("回答：", answer)

    # location = input("请输入要查询天气的地名：")
    # weather_info = get_weather(location)
    # print("天气信息：", weather_info)