# Final Evalutor file
import math
import datetime
from parser_ast import *
from environment import Environment
from js_types import *

class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class JSFunction:
    def __init__(self, name, params, rest_param, body, closure, is_arrow=False, is_expression_body=False):
        self.name = name
        self.params = params
        self.rest_param = rest_param
        self.body = body
        self.closure = closure
        self.is_arrow = is_arrow
        self.is_expression_body = is_expression_body

    def __repr__(self):
        name_str = self.name if self.name else "anonymous"
        return f"[Function: {name_str}]"


class Evaluator:
    def __init__(self):
        self.global_env = Environment()
        self.init_globals()

    def init_globals(self):
        # Math object
        self.global_env.declare('Math', JSMath())
        
        # console object
        console_obj = JSObject({
            'log': lambda *args: print(" ".join(js_to_string(arg) for arg in args))
        })
        self.global_env.declare('console', console_obj)
        
        # Date constructor
        def js_date_constructor(*args):
            return datetime.datetime.now().strftime("%a %b %d %Y %H:%M:%S GMT")
        self.global_env.declare('Date', js_date_constructor)
        
        # undefined & null
        self.global_env.declare('undefined', Undefined)
        self.global_env.declare('null', None)

    def evaluate(self, node, env):
        method_name = f"eval_{type(node).__name__}"
        visitor = getattr(self, method_name, None)
        if not visitor:
            raise NotImplementedError(f"No visitor method eval_{type(node).__name__}")
        return visitor(node, env)

    # 1. Statements

    def eval_Program(self, node, env):
        # Pass 1: Function hoisting
        for stmt in node.body:
            if isinstance(stmt, FunctionDecl) and stmt.name:
                self.evaluate(stmt, env)
        # Pass 2: Execution
        val = Undefined
        for stmt in node.body:
            if isinstance(stmt, FunctionDecl) and stmt.name:
                continue
            val = self.evaluate(stmt, env)
        return val

    def eval_BlockStmt(self, node, env):
        block_env = Environment(env)
        # Pass 1: Function hoisting
        for stmt in node.body:
            if isinstance(stmt, FunctionDecl) and stmt.name:
                self.evaluate(stmt, block_env)
        # Pass 2: Execution
        val = Undefined
        for stmt in node.body:
            if isinstance(stmt, FunctionDecl) and stmt.name:
                continue
            val = self.evaluate(stmt, block_env)
        return val

    def eval_VarDecl(self, node, env):
        val = Undefined
        if node.init:
            val = self.evaluate(node.init, env)
        env.declare(node.name, val, is_const=(node.kind == 'const'))
        return val

    def eval_IfStmt(self, node, env):
        cond = self.evaluate(node.condition, env)
        if js_is_truthy(cond):
            return self.evaluate(node.then_branch, env)
        elif node.else_branch:
            return self.evaluate(node.else_branch, env)
        return Undefined

    def eval_WhileStmt(self, node, env):
        val = Undefined
        while js_is_truthy(self.evaluate(node.condition, env)):
            try:
                val = self.evaluate(node.body, env)
            except BreakException:
                break
            except ContinueException:
                continue
        return val

    def eval_DoWhileStmt(self, node, env):
        val = Undefined
        while True:
            try:
                val = self.evaluate(node.body, env)
            except BreakException:
                break
            except ContinueException:
                pass
            if not js_is_truthy(self.evaluate(node.condition, env)):
                break
        return val

    def eval_ForStmt(self, node, env):
        val = Undefined
        for_env = Environment(env)
        if node.init:
            self.evaluate(node.init, for_env)

        while True:
            if node.test:
                if not js_is_truthy(self.evaluate(node.test, for_env)):
                    break
            
            try:
                val = self.evaluate(node.body, for_env)
            except BreakException:
                break
            except ContinueException:
                pass

            if node.update:
                self.evaluate(node.update, for_env)
        return val

    def eval_SwitchStmt(self, node, env):
        disc_val = self.evaluate(node.discriminant, env)
        matched = False
        default_idx = -1
        match_idx = -1

        for idx, case in enumerate(node.cases):
            if case.test is None:
                default_idx = idx
            else:
                test_val = self.evaluate(case.test, env)
                if js_strict_eq(disc_val, test_val):
                    match_idx = idx
                    break

        start_idx = match_idx if match_idx != -1 else default_idx

        if start_idx != -1:
            try:
                for idx in range(start_idx, len(node.cases)):
                    for stmt in node.cases[idx].consequent:
                        self.evaluate(stmt, env)
            except BreakException:
                pass
        return Undefined

    def eval_BreakStmt(self, node, env):
        raise BreakException()

    def eval_ContinueStmt(self, node, env):
        raise ContinueException()

    def eval_ReturnStmt(self, node, env):
        val = Undefined
        if node.value:
            val = self.evaluate(node.value, env)
        raise ReturnException(val)

    def eval_ExpressionStmt(self, node, env):
        return self.evaluate(node.expression, env)

    def eval_EmptyStmt(self, node, env):
        return Undefined

    # 2. Expressions

    def eval_Literal(self, node, env):
        return node.value

    def eval_Identifier(self, node, env):
        if node.name == 'this':
            try:
                return env.get('this')
            except NameError:
                return Undefined
        return env.get(node.name)

    def eval_BinaryExpr(self, node, env):
        if node.op == '&&':
            left = self.evaluate(node.left, env)
            if not js_is_truthy(left):
                return left
            return self.evaluate(node.right, env)
        if node.op == '||':
            left = self.evaluate(node.left, env)
            if js_is_truthy(left):
                return left
            return self.evaluate(node.right, env)

        left = self.evaluate(node.left, env)
        right = self.evaluate(node.right, env)

        if node.op == '+': return js_add(left, right)
        if node.op == '-': return js_to_number(left) - js_to_number(right)
        if node.op == '*': return js_to_number(left) * js_to_number(right)
        if node.op == '/':
            r = js_to_number(right)
            if r == 0:
                return float('inf') if js_to_number(left) >= 0 else float('-inf')
            return js_to_number(left) / r
        if node.op == '%': return js_to_number(left) % js_to_number(right)
        if node.op == '**': return js_to_number(left) ** js_to_number(right)

        if node.op == '===': return js_strict_eq(left, right)
        if node.op == '!==': return not js_strict_eq(left, right)
        if node.op == '==': return js_loose_eq(left, right)
        if node.op == '!=': return not js_loose_eq(left, right)

        if node.op == '<': return js_lt(left, right)
        if node.op == '<=': return js_le(left, right)
        if node.op == '>': return js_gt(left, right)
        if node.op == '>=': return js_ge(left, right)

        raise NotImplementedError(f"Binary operator {node.op}")

    def eval_UnaryExpr(self, node, env):
        right = self.evaluate(node.right, env)
        if node.op == '+': return js_to_number(right)
        if node.op == '-': return -js_to_number(right)
        if node.op == '!': return not js_is_truthy(right)
        if node.op == 'typeof':
            if right is Undefined: return "undefined"
            if right is None: return "object"
            if isinstance(right, bool): return "boolean"
            if isinstance(right, (int, float)): return "number"
            if isinstance(right, str): return "string"
            if isinstance(right, (JSArray, JSObject, JSDate)): return "object"
            if callable(right) or isinstance(right, JSFunction): return "function"
            return "object"
        raise NotImplementedError(f"Unary operator {node.op}")

    def eval_UpdateExpr(self, node, env):
        if isinstance(node.argument, Identifier):
            name = node.argument.name
            old_val = js_to_number(env.get(name))
            new_val = old_val + 1 if node.op == '++' else old_val - 1
            env.set(name, new_val)
            return old_val if not node.prefix else new_val
        elif isinstance(node.argument, MemberExpr):
            obj = self.evaluate(node.argument.object, env)
            prop = self.evaluate(node.argument.property, env) if node.argument.computed else node.argument.property
            
            if isinstance(obj, JSArray):
                old_val = js_to_number(obj.get_item(prop))
                new_val = old_val + 1 if node.op == '++' else old_val - 1
                obj.set_item(prop, new_val)
                return old_val if not node.prefix else new_val
            elif isinstance(obj, JSObject):
                old_val = js_to_number(obj.get_prop(prop))
                new_val = old_val + 1 if node.op == '++' else old_val - 1
                obj.set_prop(prop, new_val)
                return old_val if not node.prefix else new_val
            else:
                raise TypeError("Cannot set property on non-object")
        else:
            raise TypeError("Invalid left-hand side in update expression")

    def eval_AssignmentExpr(self, node, env):
        right_val = self.evaluate(node.right, env)

        if isinstance(node.left, Identifier):
            name = node.left.name
            if node.op == '=':
                env.set(name, right_val)
                return right_val
            
            old_val = env.get(name)
            if node.op == '+=':
                res = js_add(old_val, right_val)
            elif node.op == '-=':
                res = js_to_number(old_val) - js_to_number(right_val)
            else:
                raise NotImplementedError(f"Assignment operator {node.op}")
            env.set(name, res)
            return res

        elif isinstance(node.left, MemberExpr):
            obj = self.evaluate(node.left.object, env)
            prop = self.evaluate(node.left.property, env) if node.left.computed else node.left.property

            if node.op == '=':
                if isinstance(obj, JSArray):
                    obj.set_item(prop, right_val)
                elif isinstance(obj, JSObject):
                    obj.set_prop(prop, right_val)
                else:
                    raise TypeError(f"Cannot set property '{prop}' of non-object")
                return right_val

            # +=, -=
            if isinstance(obj, JSArray):
                old_val = obj.get_item(prop)
            elif isinstance(obj, JSObject):
                old_val = obj.get_prop(prop)
            else:
                raise TypeError(f"Cannot set property '{prop}' of non-object")

            if node.op == '+=':
                res = js_add(old_val, right_val)
            elif node.op == '-=':
                res = js_to_number(old_val) - js_to_number(right_val)
            else:
                raise NotImplementedError(f"Assignment operator {node.op}")

            if isinstance(obj, JSArray):
                obj.set_item(prop, res)
            else:
                obj.set_prop(prop, res)
            return res
        else:
            raise TypeError("Invalid left-hand side in assignment expression")

    def eval_TernaryExpr(self, node, env):
        cond = self.evaluate(node.condition, env)
        if js_is_truthy(cond):
            return self.evaluate(node.then_expr, env)
        return self.evaluate(node.else_expr, env)

    def eval_CallExpr(self, node, env):
        # Arguments evaluation
        args_vals = []
        for arg in node.args:
            if isinstance(arg, SpreadExpr):
                spread_val = self.evaluate(arg.argument, env)
                if isinstance(spread_val, JSArray):
                    args_vals.extend(spread_val.elements)
                elif isinstance(spread_val, list):
                    args_vals.extend(spread_val)
            else:
                args_vals.append(self.evaluate(arg, env))

        # Callee evaluation
        this_val = Undefined
        if isinstance(node.callee, MemberExpr):
            obj_val = self.evaluate(node.callee.object, env)
            prop_val = self.evaluate(node.callee.property, env) if node.callee.computed else node.callee.property

            if isinstance(obj_val, str):
                callee_fn = get_string_member(obj_val, prop_val)
                this_val = obj_val
            elif isinstance(obj_val, JSArray):
                callee_fn = obj_val.get_method(prop_val, self)
                this_val = obj_val
            elif isinstance(obj_val, JSDate):
                callee_fn = obj_val.get_method(prop_val)
                this_val = obj_val
            elif isinstance(obj_val, JSMath):
                callee_fn = obj_val.get_method(prop_val)
                this_val = obj_val
            elif isinstance(obj_val, JSObject):
                callee_fn = obj_val.get_prop(prop_val)
                this_val = obj_val
            else:
                raise TypeError(f"Cannot read property '{prop_val}' of {type(obj_val)}")
        else:
            callee_fn = self.evaluate(node.callee, env)

        if callee_fn is Undefined or callee_fn is None:
            raise TypeError(f"TypeError: {node.callee} is not a function")

        # Function Execution
        if isinstance(callee_fn, JSFunction):
            return self.call_function(callee_fn, args_vals, this_val)
        elif callable(callee_fn):
            return callee_fn(*args_vals)
        else:
            raise TypeError(f"TypeError: {callee_fn} is not a function")

    def eval_NewExpr(self, node, env):
        args_vals = []
        for arg in node.args:
            if isinstance(arg, SpreadExpr):
                spread_val = self.evaluate(arg.argument, env)
                if isinstance(spread_val, JSArray):
                    args_vals.extend(spread_val.elements)
                elif isinstance(spread_val, list):
                    args_vals.extend(spread_val)
            else:
                args_vals.append(self.evaluate(arg, env))

        callee_fn = self.evaluate(node.callee, env)

        # Date constructor check
        if callee_fn == self.global_env.get('Date'):
            return JSDate(*args_vals)

        if isinstance(callee_fn, JSFunction):
            new_obj = JSObject()
            res = self.call_function(callee_fn, args_vals, new_obj)
            if isinstance(res, (JSObject, JSArray)):
                return res
            return new_obj

        raise TypeError(f"TypeError: {node.callee} is not a constructor")

    def eval_MemberExpr(self, node, env):
        obj_val = self.evaluate(node.object, env)
        prop_val = self.evaluate(node.property, env) if node.computed else node.property

        if isinstance(obj_val, str):
            return get_string_member(obj_val, prop_val)
        elif isinstance(obj_val, JSArray):
            return obj_val.get_method(prop_val, self)
        elif isinstance(obj_val, JSDate):
            return obj_val.get_method(prop_val)
        elif isinstance(obj_val, JSMath):
            return obj_val.get_method(prop_val)
        elif isinstance(obj_val, JSObject):
            return obj_val.get_prop(prop_val)
        else:
            if obj_val is Undefined:
                raise TypeError(f"Cannot read properties of undefined (reading '{prop_val}')")
            if obj_val is None:
                raise TypeError(f"Cannot read properties of null (reading '{prop_val}')")
            return Undefined

    def eval_ObjectLiteral(self, node, env):
        props = {}
        for key, expr in node.properties.items():
            props[key] = self.evaluate(expr, env)
        return JSObject(props)

    def eval_ArrayLiteral(self, node, env):
        elements = []
        for el in node.elements:
            if isinstance(el, SpreadExpr):
                spread_val = self.evaluate(el.argument, env)
                if isinstance(spread_val, JSArray):
                    elements.extend(spread_val.elements)
                elif isinstance(spread_val, list):
                    elements.extend(spread_val)
            else:
                elements.append(self.evaluate(el, env))
        return JSArray(elements)

    def eval_ArrowFunction(self, node, env):
        return JSFunction(
            name=None,
            params=node.params,
            rest_param=node.rest_param,
            body=node.body,
            closure=env,
            is_arrow=True,
            is_expression_body=node.is_expression_body
        )

    def eval_FunctionDecl(self, node, env):
        func = JSFunction(
            name=node.name,
            params=node.params,
            rest_param=node.rest_param,
            body=node.body,
            closure=env,
            is_arrow=False,
            is_expression_body=False
        )
        if node.name:
            env.declare(node.name, func)
        return func

    def call_function(self, func, args_vals, this_val=Undefined):
        fn_env = Environment(func.closure)
        if func.is_arrow:
            # Lexical this
            pass
        else:
            fn_env.declare('this', this_val)

        for i in range(len(func.params)):
            val = args_vals[i] if i < len(args_vals) else Undefined
            fn_env.declare(func.params[i], val)

        if func.rest_param:
            rest_vals = args_vals[len(func.params):]
            fn_env.declare(func.rest_param, JSArray(rest_vals))

        if func.is_expression_body:
            return self.evaluate(func.body, fn_env)
        else:
            try:
                self.evaluate(func.body, fn_env)
                return Undefined
            except ReturnException as re:
                return re.value