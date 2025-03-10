"""
1.写文件
2.读文件
3.追加
4.网络搜索
5.天气查询
"""
import json
import os
from langchain_community.tools.tavily_search import TavilySearchResults
import requests

def _get_workdir_root():
    workdir_root = os.environ.get("WORKDIR_ROOT",'./data/llm_result')
    return workdir_root


WORKDIR_ROOT = _get_workdir_root()


def read_file(filename):
    filename = os.path.join(WORKDIR_ROOT,filename)
    if not os.path.exists(filename):
        return f"{filename} not exist,please check file exist before read"
    with open(filename,'r') as f:
        return '\n'.join(f.readlines())

def append_to_file(filename,content):
    filename = os.path.join(WORKDIR_ROOT,filename)
    if not os.path.exists(filename):
        return f"{filename} not exist,please check file exist before read"
    with open(filename,'a') as f:
        f.write(content)
    return 'append content to file success'

def write_to_file(filename,content):
    filename = os.path.join(WORKDIR_ROOT,filename)
    if not os.path.exists(filename):
        os.makedirs(WORKDIR_ROOT)

    with open(filename,'w') as f:
        f.write(content)
    return 'write content to file success'

def search(query):
    tavily = TavilySearchResults(api_key= os.getenv("TAVILY_API_KEY"),max_results=5)

    try:
        ret = tavily.invoke(input=query)
        """
         ret:
         [{
           "content":"",
           "url":
         }]
        """
        content_list = [obj['content'] for obj in ret]
        return '\n'.join(content_list)
    except Exception as err:
        return "search err:{}".format(err)
    
def get_weather(query: str) -> str:
    api_key = "7d816ca88f33edc160a2ff6dd7002642"
    weather_url = "https://restapi.amap.com/v3/weather/weatherInfo"
    try:
        params = {
            "key": api_key,
            "city": query,
            "extensions": "base",
            "output": "json",
        }
        response = requests.get(weather_url, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get("status") != "1" or not data.get("lives"):
            return f"未找到 '{query}' 的天气信息。"
        weather_info = data["lives"][0]
        return weather_info
    except Exception as e:
        return f"查询天气时出错：{str(e)}"  

tools_info =[
    {
        "name":"read_file",
        "description":"从代理生成读取文件，应在读取之前写入文件",
        'args':[
            {
                "name":"filename",
                "type":"string",
                "description":"读取文件名"
            }
        ]
    },
    {
        "name":"append_to_file",
        "description":"将 llm 内容附加到文件，应在读取之前写入文件",
        'args':[
            {
                "name":"filename",
                "type":"string",
                "description":"文件名"
            },{
                "name":"content",
                "type":"string",
                "description":"追加到文件内容"
            }
        ]
    },
    {
        "name":"write_to_file",
        "description":"将 llm 内容写入文件",
        'args':[
            {
                "name":"filename",
                "type":"string",
                "description":"文件名"
            },{
                "name":"content",
                "type":"string",
                "description":"写入文件内容"
            }
        ]
    },
     {
        "name":"search",
        "description":"这是一个搜索引擎，当你没有从大模型中获取到一个确切结果的时候，你就可以从搜索引擎中获取到额外的信息",
        'args':[
            {
                "name":"query",
                "type":"string",
                "description":"搜索查询"
            }
        ]
    },
    {
        "name": "get_weather",
        "description": "这是一个天气查询工具，查询指定城市的实时天气信息，需要提供城市名称作为参数",
        'args': [
            {
                "name": "query",
                "type": "string",
                "description": "要查询天气的城市名称（例如：北京、上海等）"
            }
        ]
    },
     {
        "name": "finish",
        "description": "当任务完成时返回最终答案",
        'args': [
            {
                "name": "answer",
                "type": "string",
                "description": "最后目标的结果"
            }
        ]
    },
]

tools_map ={
    'read_file':read_file,
    'append_to_file':append_to_file,
    'write_to_file':write_to_file,
    'search':search,
    'get_weather': get_weather
}
          
def  gen_tools_desc():
    tools_desc=[]
    for idx,t in enumerate(tools_info):
        args_desc =[]
        for info in t['args']:
            args_desc.append({
                "name":info['name'],
                "description":info['description'],
                "type":info["type"]
            })
        args_desc = json.dumps(args_desc,ensure_ascii=False)
        tool_desc = f"{idx+1}. {t['name']}: {t['description']}, args:{args_desc}"
        tools_desc.append(tool_desc)
    tools_prompt = "\n".join(tools_desc)
    return tools_prompt