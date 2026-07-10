import ast
import operator


class CalculatorTool:
    name = "calculator"
    description = "Evaluate basic arithmetic expressions."

    _operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def run(self, expression):
        if isinstance(expression, dict):
            expression = expression.get("expression") or expression.get("input") or ""

        expression = str(expression).strip().replace("×", "*").replace("÷", "/")
        if len(expression) >= 2 and expression[0] == expression[-1] and expression[0] in {"'", '"'}:
            expression = expression[1:-1].strip()

        value = self._eval(ast.parse(expression, mode="eval").body)
        return str(value)

    def _eval(self, node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in self._operators:
            return self._operators[type(node.op)](
                self._eval(node.left),
                self._eval(node.right),
            )
        if isinstance(node, ast.UnaryOp) and type(node.op) in self._operators:
            return self._operators[type(node.op)](self._eval(node.operand))
        raise ValueError("Only arithmetic expressions are supported")
