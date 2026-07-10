import ast
import operator
import math
from ..registry import ToolRegistry

def my_calculate(expression: str) -> str:
    if not expression.strip():
        return "计算表达式不能为空"


    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }

    functions = {
        'sqrt': math.sqrt,
        'pi': math.pi,
    }

    try:
        node = ast.parse(expression,mode='eval')
        result = _eval_node(node.body, operators, functions)
        return str(result)

    except Exception as e:
        return f"计算失败，请检查表达式: {e}"



def _eval_node(node, operators, functions):
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BinOp):
        left = _eval_node(node.left,operators,functions)
        right = _eval_node(node.right,operators,functions)
        op = operators.get(type(node.op))
        return op(left,right)
    elif isinstance(node, ast.Call):
        func_name = node.func.id
        if func_name not in functions:
            raise ValueError(f"Unsupported function: {func_name}")

        args = [_eval_node(arg, operators, functions) for arg in node.args]
        return functions[func_name](*args)


def create_calculator_registry():
    registry = ToolRegistry("","")

    registry.register_function(
        name="my_calculator",
        description="simple math operation tool",
        func=my_calculate
    )

    return registry




































