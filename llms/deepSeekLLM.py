import json
import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from prompt import user_prompt
from utils import extract_json
load_dotenv()

class DeepSeekLLM(object):
    def __init__(self):
        self.model_name = os.getenv("DEEPSEEK_MODEL_NAME")
        self._client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),  # 修正环境变量名称
            base_url="https://api.deepseek.com/v1",  # 补充API版本路径
        )
        self.max_retry_time = 3
    
    def chat(self, prompt, chat_history):
        cur_retry_time = 0
        while cur_retry_time < self.max_retry_time:
            cur_retry_time += 1
            try:
                # 构建符合OpenAI格式的消息列表
                messages = [{"role": "system", "content": prompt}]
                for user_msg, assistant_msg in chat_history:
                    messages.extend([
                        {"role": "user", "content": user_msg},
                        {"role": "assistant", "content": assistant_msg}
                    ])
                messages.append({"role": "user", "content": user_prompt})
                
                # 禁用流式传输以简化处理
                completion = self._client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    stream=False,  # 关闭流式传输
                )
                
                # 提取响应内容
                content = completion.choices[0].message.content
                
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return json.loads(re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL).group(1))
                    
            except Exception as err:
                print(f"调用DeepSeek出错（尝试次数 {cur_retry_time}）:", err)
        return None
    