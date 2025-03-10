import re
import json

def extract_json(text):
    # 先清理可能存在的代码块标记
    text = re.sub(r'```.*?```', lambda m: m.group().replace('```', ''), text, flags=re.DOTALL)
    
    # 查找最外层JSON结构
    start = text.find('{')
    if start == -1:
        return None

    stack = 1
    end = start + 1
    while stack > 0 and end < len(text):
        if text[end] == '{':
            stack += 1
        elif text[end] == '}':
            stack -= 1
        end += 1

    if stack != 0:
        return None  # 不完整的JSON结构

    json_str = text[start:end]
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None