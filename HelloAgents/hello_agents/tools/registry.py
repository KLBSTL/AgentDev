from .base import Tool
from typing import Any, Callable, Dict


class ToolRegistry:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self._tools: dict[str, Tool] = {}
        self._functions: dict[str, dict[str, Any]] = {}

    def register_tool(self, tool: Tool):
        if tool.name in self._tools:
            print(f"警告: 工具 '{tool.name}' 已存在，将被覆盖")
        self._tools[tool.name] = tool
        print(f"工具 '{tool.name}' 已注册")

    def register_function(self, name: str, description: str,func: Callable[[str],str]):
        if name in self._functions:
            print(f"警告: 函数 '{name}' 已存在，将被覆盖")

        self._functions[name] = {
            "description": description,
            "func": func
        }

        print(f"工具 '{name}' 已注册")



    def unregister(self, tool_name: str) -> bool:
        return self._tools.pop(tool_name, None) is not None

    def get_tool(self, tool_name: str):
        return self._tools.get(tool_name)

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

    def get_tools_description(self) -> str:
        descriptions = []

        # Tool对象描述
        for tool in self._tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")

        # 函数工具描述
        for name, info in self._functions.items():
            descriptions.append(f"- {name}: {info['description']}")

        return "\n".join(descriptions) if descriptions else "暂无可用工具"

    def execute_tool(self, tool_name: str, parameters):
        tool = self.get_tool(tool_name)
        if tool is not None:
            return tool.run(parameters)

        function_info = self._functions.get(tool_name)
        if function_info is not None:
            return function_info["func"](parameters)

        raise ValueError(f"Tool not found: {tool_name}")

    def to_openai_schema(self) -> Dict[str, Any]:
        parameters = self.get_parameters()
        properties = {}
        required = []


        for param in parameters:
            prop = {
                "type": param.type,
                "description": param.description
            }

            if param.default is not None:
                prop["description"] = f"{param.description} (默认: {param.default})"

            if param.type == "array":
                prop["items"] = {"type": "string"}

            properties[param.name] = prop


            if param.required:
                required.append(param.name)


        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }































   
