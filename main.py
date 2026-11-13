import ast, math, operator as op, functools

BIN = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
       ast.FloorDiv: op.floordiv, ast.Mod: op.mod, ast.Pow: op.pow}
UN = {ast.UAdd: op.pos, ast.USub: op.neg}
FUNCS = {"sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "log": math.log,
         "abs": abs, "round": round}
CONSTS = {"pi": math.pi, "e": math.e}

class CalcError(Exception):
    pass

def _ev(n):
    if isinstance(n, ast.Constant) and type(n.value) in (int, float):
        return n.value
    if isinstance(n, ast.Name) and n.id in CONSTS:
        return CONSTS[n.id]
    if isinstance(n, ast.UnaryOp) and type(n.op) in UN:
        return UN[type(n.op)](_ev(n.operand))
    if isinstance(n, ast.BinOp) and type(n.op) in BIN:
        a, b = _ev(n.left), _ev(n.right)
        if isinstance(n.op, ast.Pow) and abs(b) > 1000:
            raise CalcError("занадто великий степінь")
        return BIN[type(n.op)](a, b)
    if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            and n.func.id in FUNCS and not n.keywords):
        return FUNCS[n.func.id](*map(_ev, n.args))
    raise CalcError(f"недозволена конструкція: {type(n).__name__}")

def _report(kind, msg):
    print(f"[Помилка калькулятора] {kind}: {msg}")

def safe_calculator(func):
    @functools.wraps(func)
    def wrapper(expression):
        if not isinstance(expression, str) or not expression.strip():
            return _report("ValueError", "вираз має бути непорожнім рядком")
        if len(expression) > 200:
            return _report("ValueError", "вираз задовгий (макс. 200 символів)")
        try:
            tree = ast.parse(expression.strip().replace("^", "**"), mode="eval")
            return _ev(tree.body)
        except ZeroDivisionError:
            return _report("ZeroDivisionError", "ділення на нуль")
        except SyntaxError:
            return _report("SyntaxError", "синтаксична помилка у виразі")
        except Exception as e:  # CalcError, ValueError, TypeError, OverflowError...
            return _report(type(e).__name__, str(e))
    return wrapper

@safe_calculator
def calculate(expression):
    return eval(expression)  # не викликається: декоратор підміняє обчислення

if __name__ == "__main__":
    for t in ["2 + 2 * 3", "2 ^ 10", "sqrt(16) + pi", "10 / 0", "2 +",
              "__import__('os')", "sqrt(-1)", "9 ** 99999", ""]:
        print(f"{t!r:22} -> {calculate(t)}")