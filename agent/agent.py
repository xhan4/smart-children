import logging
from typing import Dict, List, Optional, Tuple, Union
import json5
from tools.tool import Tool
from llms.deepSeekLLM import DeepSeekLLM

# 配置日志系统
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

TOOL_DESC = """{name_for_model}: Call this tool to interact with the {name_for_human} API. What is the {name_for_human} API useful for? {description_for_model} Parameters: {parameters} Format the arguments as a JSON object."""
REACT_PROMPT = """Answer the following questions as best you can. You have access to the following tools:

{tool_descs}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can be repeated zero or more times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!
"""


class Agent:
    def __init__(self, command: str = '', tools: List[Tool] = None) -> None:
        logger.info("正在初始化智能代理...")
        self.model = DeepSeekLLM(command)
        logger.info("正在启动模型服务...")
        self.model.start()
        self.tools = tools or []
        self.tool_funcs = {tool.name_for_model: tool.func for tool in self.tools}
        logger.debug(f"注册工具: {[tool.name_for_model for tool in self.tools]}")
        self.system_prompt = self.build_system_input()
        logger.debug(f"系统提示长度: {len(self.system_prompt)}")

    def build_system_input(self):
        logger.info("正在构建系统提示...")
        tool_descs = []
        tool_names = []
        for tool in self.tools:
            config = tool.to_config()
            parameters_str = json5.dumps(config['parameters'], ensure_ascii=False)
            formatted_desc = TOOL_DESC.format(
                name_for_model=config['name_for_model'],
                name_for_human=config['name_for_human'],
                description_for_model=config['description_for_model'],
                parameters=parameters_str
            )
            tool_descs.append(formatted_desc)
            tool_names.append(config['name_for_model'])
            logger.debug(f"添加工具描述: {config['name_for_model']}")
        
        system_prompt = REACT_PROMPT.format(
            tool_descs='\n\n'.join(tool_descs),
            tool_names=','.join(tool_names)
        )
        logger.debug(f"系统提示预览: {system_prompt[:200]}...")
        return system_prompt

    def parse_tool_call(self, text: str) -> Tuple[Optional[str], Optional[dict]]:
        logger.info("正在解析工具调用...")
        action_prefix = "\nAction:"
        input_prefix = "\nAction Input:"
        observation_prefix = "\nObservation:"
        
        action_pos = text.rfind(action_prefix)
        input_pos = text.rfind(input_prefix)
        obs_pos = text.rfind(observation_prefix)
        
        if action_pos == -1 or input_pos <= action_pos:
            logger.warning("未找到有效工具调用结构")
            return None, None
        
        tool_name = text[action_pos+len(action_prefix):input_pos].strip()
        tool_args_str = text[input_pos+len(input_prefix):obs_pos if obs_pos != -1 else None].strip()
        
        try:
            tool_args = json5.loads(tool_args_str)
            logger.info(f"成功解析工具调用: {tool_name} 参数: {tool_args}")
            return tool_name, tool_args
        except json5.JSONDecodeError as e:
            logger.error(f"工具参数解析失败: {e}")
            return None, None

    def execute_tool(self, tool_name: str, tool_args: dict) -> str:
        logger.info(f"正在执行工具: {tool_name}")
        if tool_name not in self.tool_funcs:
            error_msg = f"未知工具: {tool_name}"
            logger.error(error_msg)
            return f"\nObservation: {error_msg}"
        
        try:
            logger.debug(f"执行工具参数: {tool_args}")
            result = self.tool_funcs[tool_name](**tool_args)
            logger.info(f"工具执行成功，结果: {result}")
            return f"\nObservation: {result}"
        except Exception as e:
            error_msg = f"工具执行失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return f"\nObservation: {error_msg}"

    def generate_response(self, query: str, max_turns: int = 5) -> str:
        logger.info(f"开始处理查询: {query}")
        history = []
        current_prompt = f"\nQuestion: {query}"
        
        for turn in range(max_turns):
            logger.info(f"处理轮次 {turn+1}/{max_turns}")
            logger.debug(f"当前提示内容: {current_prompt}")
            
            # 构建完整提示
            full_prompt = self.model.build_prompt(current_prompt, history, self.system_prompt)
            logger.debug(f"完整提示长度: {len(full_prompt)}")
            
            # 调用模型
            try:
                response = self.model(full_prompt)
                logger.debug(f"模型原始响应: {response}")  # 新增此行
                logger.info(f"模型响应: {response[:200]}...")
            except Exception as e:
                logger.error(f"模型调用失败: {e}", exc_info=True)
                return f"系统错误: {str(e)}"
            
            # 解析工具调用
            tool_name, tool_args = self.parse_tool_call(response)
            
            if tool_name:
                observation = self.execute_tool(tool_name, tool_args)
                current_prompt = f"{response}{observation}"
                history.append({"role": "assistant", "content": current_prompt})
                logger.info("工具调用完成，继续下一轮处理")
            else:
                final_answer = self.extract_final_answer(response)
                logger.info(f"最终答案生成: {final_answer}")
                return final_answer
        
        error_msg = "超过最大工具调用次数"
        logger.error(error_msg)
        return error_msg

    def extract_final_answer(self, text: str) -> str:
        logger.info("正在提取最终答案...")
        final_answer_marker = "\nFinal Answer:"
        start_idx = text.rfind(final_answer_marker)
        if start_idx != -1:
            answer = text[start_idx + len(final_answer_marker):].strip()
            logger.info(f"找到最终答案: {answer}")
            return answer
        logger.warning("未找到最终答案标记，返回原始响应")
        return text.strip()

    def run(self, query: str) -> str:
        logger.info("启动查询处理流程")
        try:
            result = self.generate_response(query)
            logger.info("查询处理完成")
            return result
        except Exception as e:
            logger.error(f"处理过程中发生错误: {e}", exc_info=True)
            return f"系统内部错误: {str(e)}"