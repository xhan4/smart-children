import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from dashscope.api_entities.dashscope_response import Message
from prompt import user_prompt
load_dotenv()

class QwenLLM(object):
    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.model_name = os.getenv("QWEN_MODEL_NAME")
        self._client = OpenAI(
                            api_key=os.getenv("DASHSCOPE_API_KEY"), 
                            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                          )
        self.max_retry_time=3
    
    def chat(self,prompt,chat_history):
        cur_retry_time = 0
        reasoning_content = ""  # 定义完整思考过程
        answer_content = ""     # 定义完整回复
        is_answering = False   # 判断是否结束思考过程并开始回复
        while cur_retry_time < self.max_retry_time:
            cur_retry_time +=1
            try:
              messages = [Message(role='system',content=prompt)]
              for his in chat_history:
                  messages.append(Message(role='user',content=his[0]))
                  messages.append(Message(role='assistant',content=his[1]))
              messages.append(Message(role='user',content=user_prompt))
              completion = self._client.chat.completions.create(
                            model= self.model_name,
                            messages= messages,  
                            stream=True,           
                            )
              for chunk in completion:
                # 如果chunk.choices为空，则打印usage
                if not chunk.choices:
                    print("\nUsage:")
                    print(chunk.usage)
                else:
                    delta = chunk.choices[0].delta
                    # 打印思考过程
                    if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
                        reasoning_content += delta.reasoning_content
                    else:
                        # 开始回复
                        if delta.content != "" and is_answering is False:
                            is_answering = True
                        # 打印回复过程
                        answer_content += delta.content
              return json.loads(answer_content)
              # response_json=completion.model_dump_json()
              # response = json.loads(response_json)
              # content = response["choices"][0]["message"]["content"]
              # print(content,"content")
              # return json.loads(content)
            except Exception as err:
              print("调用Qwen出错:",err)