class SemanticError(Exception):
    pass


class SymbolTable:
    def __init__(self):
        self.scopes = [{}]

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        self.scopes.pop()

    def declare(self, name, info):
        if name in self.scopes[-1]:
            raise SemanticError(f"Semantic Error: redeclaration of '{name}'")
        self.scopes[-1][name] = info

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise SemanticError(f"Semantic Error: '{name}' is not defined")


class SemanticAnalyzer:
    def __init__(self):
        self.symtab = SymbolTable()
        self.errors = []
        self.current_function = None

    def analyze(self, ast):
        try:
            self.visit(ast)
        except SemanticError as e:
            self.errors.append(str(e))
        return self.errors

    def visit(self, node):
        if node is None:
            return None

        if isinstance(node, list):
            for n in node:
                self.visit(n)
            return None

        tag = node[0]

        if tag == "program":
            self.visit(node[1])

        elif tag == "var_decl":
            _, var_type, name, expr = node
            self.symtab.declare(name, {"type": var_type})
            if expr:
                expr_type = self.visit(expr)
                self.check_assignment(var_type, expr_type)

        elif tag == "var_decl_array":
            _, var_type, name, size = node
            if not isinstance(size, int):
                raise SemanticError("Array size must be integer literal")
            self.symtab.declare(name, {"type": var_type, "array": True, "size": size})

        elif tag == "func_decl":
            _, name, params, body = node
            self.symtab.declare(name, {"type": "func", "params": params})
            self.symtab.enter_scope()
            self.current_function = name

            if params:
                for _, ptype, pname in params:
                    self.symtab.declare(pname, {"type": ptype})

            self.visit(body)

            self.current_function = None
            self.symtab.exit_scope()

        elif tag == "block":
            self.symtab.enter_scope()
            self.visit(node[1])
            self.symtab.exit_scope()

        elif tag == "stmt":
            self.visit(node[1])

        elif tag == "assign":
            _, loc, expr = node
            lhs_type = self.visit(loc)
            rhs_type = self.visit(expr)
            self.check_assignment(lhs_type, rhs_type)

        elif tag == "loc":
            info = self.symtab.lookup(node[1])
            return info["type"]

        elif tag == "loc_array":
            _, name, index = node
            info = self.symtab.lookup(name)
            if "array" not in info:
                raise SemanticError(f"'{name}' is not an array")
            idx_type = self.visit(index)
            if idx_type != "int":
                raise SemanticError("Array index must be int")
            return info["type"]

        elif tag == "if":
            _, cond, then_blk, elif_part, else_part = node
            if self.visit(cond) != "bool":
                raise SemanticError("Condition of if must be bool")
            self.visit(then_blk)
            if elif_part:
                self.visit(elif_part)
            if else_part:
                self.visit(else_part)

        elif tag == "elif":
            _, cond, blk, next_elif = node
            if self.visit(cond) != "bool":
                raise SemanticError("Condition of elif must be bool")
            self.visit(blk)
            if next_elif:
                self.visit(next_elif)

        elif tag == "while":
            _, cond, blk = node
            if self.visit(cond) != "bool":
                raise SemanticError("Condition of while must be bool")
            self.visit(blk)

        elif tag == "for":
            _, init, cond, step, blk = node
            self.visit(init)
            if self.visit(cond) != "bool":
                raise SemanticError("Condition of for must be bool")
            self.visit(step)
            self.visit(blk)

        elif tag == "print":
            self.visit(node[1])

        elif tag == "input":
            self.symtab.lookup(node[1])

        elif tag == "return":
            if node[1]:
                self.visit(node[1])

        elif tag == "binop":
            _, op, left, right = node
            lt = self.visit(left)
            rt = self.visit(right)

            if op in ("&&", "||"):
                if lt != "bool" or rt != "bool":
                    raise SemanticError("Logical operators require bool operands")
                return "bool"

            if op in ("<", "<=", ">", ">=", "==", "!="):
                if lt != rt:
                    raise SemanticError("Type mismatch in comparison")
                return "bool"

            if op in ("+", "-", "*", "/", "%"):
                return self.numeric_result(lt, rt)

        elif tag == "unary":
            _, op, expr = node
            et = self.visit(expr)
            if op == "!" and et != "bool":
                raise SemanticError("Logical NOT requires bool")
            if op == "-" and et not in ("int", "float"):
                raise SemanticError("Unary minus requires numeric type")
            return et

        elif tag == "literal":
            val = node[1]
            if isinstance(val, bool):
                return "bool"
            if isinstance(val, int):
                return "int"
            if isinstance(val, float):
                return "float"
            if isinstance(val, str) and len(val) == 1:
                return "char"
            return "string"

        elif tag == "call":
            _, name, args = node
            info = self.symtab.lookup(name)
            if info["type"] != "func":
                raise SemanticError(f"'{name}' is not a function")

            params = info["params"] or []
            args = args or []

            if len(params) != len(args):
                raise SemanticError("Function argument count mismatch")

            for (_, ptype, _), arg in zip(params, args):
                atype = self.visit(arg)
                self.check_assignment(ptype, atype)

            return None

    def check_assignment(self, lhs, rhs):
        if lhs == rhs:
            return
        if lhs == "float" and rhs == "int":
            return
        raise SemanticError(f"Cannot assign {rhs} to {lhs}")

    def numeric_result(self, t1, t2):
        if t1 == "float" or t2 == "float":
            return "float"
        if t1 == "int" and t2 == "int":
            return "int"
        raise SemanticError("Invalid operands for arithmetic")
