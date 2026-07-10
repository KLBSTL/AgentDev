import sys

from dotenv import load_dotenv

from ..hello_agents import HelloAgents
from ..hello_agents.agents import PlanAndSolveAgent


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


load_dotenv()

llm = HelloAgents()
agent = PlanAndSolveAgent(
    name="我的规划执行助手",
    llm=llm,
)

question = (
    "一个水果店周一卖出了15个苹果。周二卖出的苹果数量是周一的两倍。"
    "周三卖出的数量比周二少了5个。请问这三天总共卖出了多少个苹果？"
)

result = agent.run(question)
history = agent.get_history()

assert isinstance(result, str)
assert result.strip()
assert len(history) == 2

print(f"\n最终结果: {result}")
print(f"对话历史: {len(history)} 条消息")
