
import sys
import os
current_script_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_script_path))
sys.path.append(project_root)

from agent.agent import Agent
from tools.tool import Tool
from tools.weather_api import get_weather
def get_agent():
# 通过Tool类显式创建工具配置
    weather_tool = Tool(
    model="weather_query",
    name="天气查询工具",
    func=get_weather,
    description="输入地名，返回当前天气信息",
    parameters={
        "query": "需要查询天气的地点（例如：北京）"
    }
    )

    # 创建代理实例
    agent = Agent(
              command="ollama run deepseek-r1:1.5b",
              tools=[weather_tool]  # 添加Tool实例列表
              )
    return agent

if __name__ == "__main__":
    # # 启动模型服务
    # agent = get_agent()
    
    # try:
    #     while True:
    #         query = input("请输入您的问题（输入'exit'退出）：")
    #         if query.lower() == 'exit':
    #             break
    #         print("回答：",agent.run(query))
    # finally:
    #     agent.model.terminate()
    print(get_weather('上海'))