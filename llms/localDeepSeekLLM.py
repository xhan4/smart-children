import logging
import requests
from prompt import user_prompt
from utils import extract_json
logger = logging.getLogger(__name__)

class LocalDeepSeekLLM:
    def __init__(self, base_url="http://localhost:11434/api/generate"):
        self.base_url = base_url
        self.max_retry_time = 3
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def chat(self, prompt: str, chat_history: list, model: str = "deepseek-r1:1.5b", timeout: int = 30) -> str:
        cur_retry_time = 0
        while cur_retry_time < self.max_retry_time:
            cur_retry_time += 1
            try:
                chat_history_str = "\n".join(
                   [f"User: {msg[0]}\nAssistant: {msg[1]}" for msg in chat_history]
                   )
                full_prompt = f"{chat_history_str}\nUser: {user_prompt}"

                # 构造请求体
                payload = {
                    "model": model,
                    "prompt": full_prompt,
                    "system": prompt,
                    "stream": False
                }
                
                # 发送请求
                response = self.session.post(
                    self.base_url,
                    json=payload,
                    timeout=timeout
                )
                response.raise_for_status()  # 检查HTTP状态码
                response_data = response.json()
                text = response_data.get("response", "")
                print(extract_json(text),'text')
                return extract_json(text)
            
            except Exception as err:
               print('调用大模型出错：{}',err)
        return {}