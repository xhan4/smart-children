import os
import time

from deepSeekLLM import DeepSeekLLM
from prompt import gen_prompt,user_prompt
from qwenLLM import QwenLLM
from tools import tools_map
dsLLM = DeepSeekLLM()
qwLLM = QwenLLM()
MP = qwLLM
MAX_REQUEST_TIME = int(os.getenv('MAX_REQUEST_TIME'))
def parse_thoughts(response):
     try:
          thoughts = response.get("thoughts")
          observation = response.get('observation')
          plan  = thoughts.get('plan')
          reasoning = thoughts.get('reasoning')
          criticism = thoughts.get('criticism')
          prompt = f"plan:{plan}\nreasoning:{reasoning}\ncriticism:{criticism}\nobservation:{observation}"
          return prompt
     except Exception as err:
          print("parse thoughts err:{}".format(err))
          return "".format(err)

def agent_execute(query,max_request_time=10):
     cur_request_time = 0
     chat_history = []
     agent_scratch = ''

     while cur_request_time < max_request_time:
          cur_request_time+=1
          """
            如果返回结果达到预期，则直接返回
          """
          """
            prompt包含的功能：
               1.任务的描述
               2.工具的描述
               3.用户输入user_msg
               4.assistant_msg
               5.限制
               6.给出更好实践的描述
          """
          prompt = gen_prompt(query,agent_scratch)
          start_time = time.time()
          print("******************* {}. 开始调用 *******************".format(cur_request_time),flush=True)
          # if cur_request_time<2:
          #      print("prompt:",prompt)
          response = MP.chat(prompt,chat_history)
          end_time = time.time()
          print("******************* {}. 调用结束，耗时：{}...*******************".format(cur_request_time,end_time-start_time ),flush=True)

          if not response or not isinstance(response,dict):
               print("调用大模型错误，即将重试...",response)
               continue
     
          action_info = response.get("action")
          action_name = action_info.get("name")
          action_args = action_info.get('args')
          print("当前action name:",action_name,action_args)

          if action_name == "finish":
               final_answer = action_args.get('answer')
               print("final_answer:",final_answer)
               break
          
          observation = response.get("observation")
          try:
               func = tools_map.get(action_name)
               call_func_result = func(**action_args)
          except Exception as err:
               print('调用工具异常：',err)
         
          agent_scratch  = agent_scratch + "/n：observation:{}\n execute action result:{}".format(observation,call_func_result) 
          assistant_msg = parse_thoughts(response)
          chat_history.append([user_prompt,assistant_msg])
     if cur_request_time == max_request_time:
          print("本次任务失败")

def main():
    while True:
          query = input("请输入您的问题：")
          if query == 'exit':
                return
          agent_execute(query,max_request_time=MAX_REQUEST_TIME )

        
if __name__ == "__main__":
     main()