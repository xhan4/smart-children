import logging
import time
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)

class DeepSeekLLM:
    def __init__(self, command: str):
        self.command = command
        self.process: Optional[subprocess.Popen] = None
        logger.debug(f"创建模型实例，命令: {self.command}")

    def start(self):
        """启动持久化模型服务"""
        logger.info("正在启动模型服务...")
        if self.process:
            logger.warning("检测到已有模型进程，跳过重复启动")
            return
        
        try:
            self.process = subprocess.Popen(
                self.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                encoding='utf-8'
            )
            logger.info(f"模型服务启动成功 (PID: {self.process.pid})")
        except Exception as e:
            logger.error(f"模型服务启动失败: {str(e)}", exc_info=True)
            raise

    def build_prompt(self, user_input: str, history: list, system_prompt: str) -> str:
        """构建完整提示词"""
        conversation = [{"role": "system", "content": system_prompt}]
        conversation += history + [{"role": "user", "content": user_input}]
        
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation])
        logger.debug(f"构建提示词完成，长度: {len(prompt)}字符")
        return prompt

    def __call__(self, full_prompt: str) -> str:
        logger.info("发起模型调用请求")
        start_time = time.time()
        timeout = 30  # 强制30秒超时
        
        try:
            if not self.process:
                raise RuntimeError("模型服务未启动")
                
            self.process.stdin.write(full_prompt + "\n")
            self.process.stdin.flush()
            
            # 使用非阻塞读取方案
            response = []
            buffer = ""
            
            while time.time() - start_time < timeout:
                # 逐字符读取以捕获不完整输出
                char = self.process.stdout.read(1)
                if char:
                    buffer += char.decode('utf-8', errors='ignore')
                    if '\n' in buffer:  # 按行分割
                        line = buffer.strip()
                        response.append(line)
                        buffer = ""
                        break  # 假设单行响应
                else:
                    time.sleep(0.01)
            
            if not response:
                raise TimeoutError("模型响应超时")
            
            final_response = response[0] if response else ""
            logger.debug(f"收到原始响应: {final_response}")
            
            # 捕获错误输出
            stderr = self.process.stderr.read()
            if stderr:
                logger.error(f"模型错误输出: {stderr}")
                raise RuntimeError(f"模型执行错误: {stderr}")
                
            return final_response
        
        except Exception as e:
            logger.error(f"模型调用失败: {str(e)}", exc_info=True)
            raise

    def terminate(self):
        """终止模型服务"""
        if self.process:
            logger.info(f"正在终止模型进程 (PID: {self.process.pid})")
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
                logger.info("模型进程已成功终止")
            except Exception as e:
                logger.error(f"进程终止异常: {str(e)}", exc_info=True)
            finally:
                self.process = None
        else:
            logger.warning("尝试终止未启动的模型进程")