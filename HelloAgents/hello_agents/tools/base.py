from abc import ABC, abstractmethod
from typing import Any, List

from pydantic import BaseModel


class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None
    
    

class Tool(ABC):
    def __init__(self, name: str, description: str):
        self.name: str = name
        self.description: str = description

    @abstractmethod
    def run(self, parameters: Any):
        pass

    @abstractmethod
    def get_parameters(self) -> List[ToolParameter]:
        pass

































