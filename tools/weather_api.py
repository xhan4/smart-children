import requests

def get_weather(location: str) -> str:
    api_key = "7d816ca88f33edc160a2ff6dd7002642"
    weather_url = "https://restapi.amap.com/v3/weather/weatherInfo"
    try:
        # 调用高德地图天气 API
        params = {
            "key": api_key,
            "city": location,
            "extensions": "base",  # base: 实时天气, all: 预报天气
            "output": "json",
        }
        response = requests.get(weather_url, params=params)
        response.raise_for_status()  # 检查 HTTP 错误

        # 解析 API 响应
        data = response.json()
        if data.get("status") != "1" or not data.get("lives"):
            return f"未找到 '{location}' 的天气信息。"

        # 提取天气信息
        weather_info = data["lives"][0]
        return (
            f"{weather_info['city']} 当前天气：\n"
            f"- 天气：{weather_info['weather']}\n"
            f"- 温度：{weather_info['temperature']}℃\n"
            f"- 湿度：{weather_info['humidity']}%\n"
            f"- 风向：{weather_info['winddirection']}\n"
            f"- 风力：{weather_info['windpower']}级\n"
            f"- 更新时间：{weather_info['reporttime']}"
        )
    except Exception as e:
        return f"查询高德天气时出错：{str(e)}"