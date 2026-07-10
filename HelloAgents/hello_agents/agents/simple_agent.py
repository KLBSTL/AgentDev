from typing import Optional

from ..core.agent import Agent
from ..core.config import Config
from ..core.llm import HelloAgents


class SimpleAgent(Agent):
    def __init__(
        self,
        name: str,
        llm: HelloAgents,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
    ):
        super().__init__(name, llm, system_prompt, config)
