import ast
from typing import Optional

from ..core.agent import Agent
from ..core.config import Config
from ..core.llm import HelloAgents
from ..core.message import Message


DEFAULT_PLANNER_PROMPT = """
你是一个顶级的 AI 规划专家。你的任务是把用户提出的复杂问题拆解成多个清晰、可执行的步骤。
请保证计划中的每一步都是独立的子任务，并且严格按照逻辑顺序排列。

问题: {question}

请只输出一个 Python list，list 中每个元素都是一个步骤字符串，例如:
```python
["步骤1", "步骤2", "步骤3"]
```
"""


DEFAULT_EXECUTOR_PROMPT = """
你是一个 AI 执行专家。你会收到原始问题、完整计划、已经完成的步骤结果，以及当前要解决的步骤。
请只专注完成当前步骤，不要提前输出最终总结。

# 原始问题
{question}

# 完整计划
{plan}

# 已完成步骤与结果
{history}

# 当前步骤
{current_step}

请只输出当前步骤的结果。
"""


DEFAULT_FINAL_PROMPT = """
你是一个 AI 总结专家。你会收到原始问题、完整计划，以及每个步骤的执行结果。
请基于这些结果，给出面向用户的最终答案。不要重新规划，也不要只重复最后一步。

# 原始问题
{question}

# 完整计划
{plan}

# 步骤执行结果
{history}

请输出最终答案。
"""


def _build_messages(prompt: str, system_prompt: Optional[str] = None) -> list[dict[str, str]]:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    return messages


def _invoke_llm(llm, messages: list[dict[str, str]]) -> str:
    if hasattr(llm, "invoke"):
        return llm.invoke(messages=messages) or ""
    return llm.think(messages=messages) or ""


def _iter_list_literals(text: str):
    for start, char in enumerate(text):
        if char != "[":
            continue

        depth = 0
        quote = None
        escape = False

        for index in range(start, len(text)):
            current = text[index]

            if escape:
                escape = False
                continue
            if current == "\\":
                escape = True
                continue

            if quote:
                if current == quote:
                    quote = None
                continue

            if current in ("'", '"'):
                quote = current
                continue
            if current == "[":
                depth += 1
            elif current == "]":
                depth -= 1
                if depth == 0:
                    yield text[start : index + 1]
                    break


def _format_step_history(step_history: list[dict[str, str]]) -> str:
    if not step_history:
        return "无"

    lines = []
    for index, item in enumerate(step_history, start=1):
        lines.append(f"步骤 {index}: {item['step']}")
        lines.append(f"结果: {item['result']}")
    return "\n".join(lines)


class Planner:
    def __init__(
        self,
        llm,
        prompt_template: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ):
        self.llm = llm
        self.prompt_template = prompt_template or DEFAULT_PLANNER_PROMPT
        self.system_prompt = system_prompt

    def plan(self, question: str) -> list[str]:
        prompt = self.prompt_template.format(question=question)
        messages = _build_messages(prompt, self.system_prompt)

        print("--- 正在生成计划 ---")
        response_text = _invoke_llm(self.llm, messages)
        print(f"计划已生成:\n{response_text}")

        plan = self.parse_plan(response_text)
        if not plan:
            print(f"无法解析有效计划，原始响应: {response_text}")
        return plan

    @staticmethod
    def parse_plan(response_text: str) -> list[str]:
        candidates = []
        text = (response_text or "").strip()

        if "```" in text:
            parts = text.split("```")
            for index in range(1, len(parts), 2):
                block = parts[index].strip()
                lines = block.splitlines()
                if lines and lines[0].strip().lower() in {"python", "py", "json"}:
                    block = "\n".join(lines[1:]).strip()
                candidates.append(block)

        candidates.extend(_iter_list_literals(text))
        candidates.append(text)

        for candidate in candidates:
            try:
                parsed = ast.literal_eval(candidate)
            except (SyntaxError, ValueError):
                continue

            if not isinstance(parsed, list):
                continue

            plan = [step.strip() for step in parsed if isinstance(step, str) and step.strip()]
            if len(plan) == len(parsed):
                return plan

        return []


class Executor:
    def __init__(
        self,
        llm,
        prompt_template: Optional[str] = None,
        final_prompt_template: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ):
        self.llm = llm
        self.prompt_template = prompt_template or DEFAULT_EXECUTOR_PROMPT
        self.final_prompt_template = final_prompt_template or DEFAULT_FINAL_PROMPT
        self.system_prompt = system_prompt

    def execute(self, question: str, plan: list[str]) -> str:
        step_history = []

        print("\n--- 正在执行计划 ---")
        for index, step in enumerate(plan, start=1):
            print(f"\n-> 正在执行步骤 {index}/{len(plan)}: {step}")

            prompt = self.prompt_template.format(
                question=question,
                plan=plan,
                history=_format_step_history(step_history),
                current_step=step,
                step_index=index,
                total_steps=len(plan),
            )
            messages = _build_messages(prompt, self.system_prompt)
            response_text = _invoke_llm(self.llm, messages)

            step_history.append({"step": step, "result": response_text})
            print(f"步骤 {index}: 已完成，结果: {response_text}")

        return self.synthesize(question, plan, step_history)

    def synthesize(
        self,
        question: str,
        plan: list[str],
        step_history: list[dict[str, str]],
    ) -> str:
        print("\n--- 正在汇总最终答案 ---")
        prompt = self.final_prompt_template.format(
            question=question,
            plan=plan,
            history=_format_step_history(step_history),
        )
        messages = _build_messages(prompt, self.system_prompt)
        final_answer = _invoke_llm(self.llm, messages)
        if final_answer:
            return final_answer

        return step_history[-1]["result"] if step_history else ""


class PlanAndSolveAgent(Agent):
    def __init__(
        self,
        name: str,
        llm: HelloAgents,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        planner_prompt_template: Optional[str] = None,
        executor_prompt_template: Optional[str] = None,
        final_prompt_template: Optional[str] = None,
    ):
        super().__init__(name, llm, system_prompt, config)
        self.planner = Planner(
            self.llm,
            prompt_template=planner_prompt_template,
            system_prompt=self.system_prompt,
        )
        self.executor = Executor(
            self.llm,
            prompt_template=executor_prompt_template,
            final_prompt_template=final_prompt_template,
            system_prompt=self.system_prompt,
        )

    def run(self, question: str) -> str:
        print(f"\n--- 开始处理问题 ---\n问题: {question}")

        plan = self.planner.plan(question)
        if not plan:
            final_answer = "无法生成有效的行动计划，请调整问题或规划提示词后重试。"
            print(f"\n--- 任务终止 ---\n{final_answer}")
            self.add_message(Message(question, "user"))
            self.add_message(Message(final_answer, "assistant"))
            return final_answer

        final_answer = self.executor.execute(question, plan)
        print(f"\n--- 任务完成 ---\n最终答案: {final_answer}")

        self.add_message(Message(question, "user"))
        self.add_message(Message(final_answer, "assistant"))
        return final_answer
