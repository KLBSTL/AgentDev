from http.client import responses

import requests
import os
from tavily import TavilyClient
from win32comext.adsi.demos.search import search


def get_weather(city: str) -> str:
    """
    调用 wttr.in api 查询天气信息
    :param city:
    :return:
    """


    url = f"https://wttr.in/{city}?format=j1"

    try:
        response = requests.get(url)

        response.raise_for_status()

        data = response.json()

        current_condition = data['current_condition'][0]

        weather_desc = current_condition['weatherDesc'][0]['value']
        temp_c = current_condition['temp_C']

        return f"{city}当前天气：{weather_desc},气温{temp_c}摄氏度"


    except requests.exceptions.RequestException as e:
        return f"错误:查询天气时遇到网络问题 - e"


    except (KeyError, IndexError) as e:
        return f"错误：解析天气数据失败，可能是城市名称无效 - {e}"



def get_attraction(city: str,weather: str) -> str:
    """
    根据天气返回景点
    :param city:
    :param weather:
    :return:
    """

    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "错误:未配置TAVILY_API_KEY环境变量"


    tavily = TavilyClient(api_key=api_key)

    query = f"'{city}'在'{weather}'天气下最值得去的旅游景点推荐及理由"


    try:
        response = tavily.search(query=query,search_depth="basic",include_answer=True)

        if response.get("answer"):
            return response["answer"]


        formatted_result = []

        for result in response.get("results",[]):
            formatted_result.append(f"- {result['title']}: {result['content']}")


        if not formatted_result:
            return "抱歉，没有找到相关的旅游推荐景点。"


        return "根据搜索，为您找到以下信息：\n" + "\n".join(formatted_result)



    except Exception as e:
        return f"错误:执行Tavily搜索时出现错误 - {e}"




available_tools = {
    "get_weather": get_weather,
    "get_attraction": get_attraction,
}


AGENT_SYSTEM_PROMPT = """
你是一个智能旅行助手。你的任务是分析用户的请求，并使用可用工具一步步地解决问题。

# 可用工具:
- `get_weather(city: str)`: 查询指定城市的实时天气。
- `get_attraction(city: str, weather: str)`: 根据城市和天气搜索推荐的旅游景点。

# 输出格式要求:
你的每次回复必须严格遵循以下格式，包含一对Thought和Action：

Thought: [你的思考过程和下一步计划]
Action: [你要执行的具体行动]

Action的格式必须是以下之一：
1. 调用工具：function_name(arg_name="arg_value")
2. 结束任务：Finish[最终答案]

# 重要提示:
- 每次只输出一对Thought-Action
- Action必须在同一行，不要换行
- 当收集到足够信息可以回答用户问题时，必须使用 Action: Finish[最终答案] 格式结束

请开始吧！
"""





































