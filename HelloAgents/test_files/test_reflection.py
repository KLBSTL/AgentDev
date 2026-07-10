# test_reflection_agent.py
import sys

from dotenv import load_dotenv

from ..hello_agents.agents import ReflectionAgent
from ..hello_agents import HelloAgents

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

load_dotenv()
llm = HelloAgents()

# 使用默认通用提示词
general_agent = ReflectionAgent(name="我的反思助手", llm=llm)

# 使用自定义代码生成提示词（类似第四章）
code_prompts = {
    "initial": "你是Python专家，请编写函数:{task}",
    "reflect": "请审查代码的算法效率:\n任务:{task}\n代码:{content}",
    "refine": "请根据反馈优化代码:\n任务:{task}\n反馈:{feedback}"
}
code_agent = ReflectionAgent(
    name="我的代码生成助手",
    llm=llm,
    prompt_templates=code_prompts,
    max_iterations=2,
)

# 测试使用
result = code_agent.run("编写一个函数，判断一个数字是否为素数")
print(f"最终结果: {result}")
