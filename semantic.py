class SemanticError(Exception):
    pass


class SymbolTable:
    def __init__(self):
        # stack فعال برای semantic checking
        self.scopes = [{}]
        self.scope_names = ["global"]

        # 👇 جدید: نگهداری همه‌ی scopeها برای نمایش
        # هر آیتم: (scope_name, scope_dict)
        self.all_scopes = []

    def enter_scope(self, name=""):
        new_scope = {}
        scope_name = name if name else f"scope_{len(self.all_scopes) + 1}"

        self.scopes.append(new_scope)
        self.scope_names.append(scope_name)

        # ثبت در تاریخچه
        self.all_scopes.append((scope_name, new_scope))

    def exit_scope(self):
        self.scopes.pop()
        self.scope_names.pop()

    def declare(self, name, info):
        if name in self.scopes[-1]:
            raise SemanticError(f"Semantic Error: redeclaration of '{name}'")
        self.scopes[-1][name] = info

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise SemanticError(f"Semantic Error: '{name}' is not defined")

    def print_symbol_table(self):
        print("----- Symbol Table (All Scopes) -----")

        # global scope
        print("Scope 0 (global):")
        global_scope = self.scopes[0]
        if global_scope:
            for name, info in global_scope.items():
                print(f"  {name}: {info}")
        else:
            print("  (empty)")

        # سایر scopeها
        for i, (scope_name, scope) in enumerate(self.all_scopes, start=1):
            print(f"\nScope {i} ({scope_name}):")
            if scope:
                for name, info in scope.items():
                    print(f"  {name}: {info}")
            else:
                print("  (empty)")

        print("------------------------------------")


class SemanticAnalyzer:
    def __init__(self):
        self.symtab = SymbolTable()
        self.errors = []
        self.current_function = None

    def analyze(self, ast):
        self.visit(ast)
        self.symtab.print_symbol_table()
        return self.errors

    def visit(self, node):
        if node is None:
            return None

        try:
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
                    et = self.visit(expr)
                    if et is not None:
                        self.check_assignment(var_type, et)

            elif tag == "var_decl_array":
                _, var_type, name, size = node
                if not isinstance(size, int):
                    raise SemanticError("Array size must be integer literal")
                self.symtab.declare(name, {"type": var_type, "array": True})

            elif tag == "func_decl":
                _, name, params, body = node
                if params is None:
                    params = []

                param_info = [(ptype, pname) for _, ptype, pname in params]
                self.symtab.declare(
                    name,
                    {"type": "func", "params": param_info, "return": "void"}
                )

                self.symtab.enter_scope(f"function:{name}")
                self.current_function = name

                for _, ptype, pname in params:
                    self.symtab.declare(pname, {"type": ptype})

                self.visit(body)

                self.current_function = None
                self.symtab.exit_scope()

            elif tag == "block":
                self.symtab.enter_scope("block")
                self.visit(node[1])
                self.symtab.exit_scope()

            elif tag == "stmt":
                self.visit(node[1])

            elif tag == "assign":
                _, loc, expr = node
                lt = self.visit(loc)
                rt = self.visit(expr)
                if lt is not None and rt is not None:
                    self.check_assignment(lt, rt)

            elif tag == "loc":
                info = self.symtab.lookup(node[1])
                return info["type"]

            elif tag == "loc_array":
                _, name, index = node
                info = self.symtab.lookup(name)
                if "array" not in info:
                    raise SemanticError(f"'{name}' is not an array")
                it = self.visit(index)
                if it != "int":
                    raise SemanticError("Array index must be int")
                return info["type"]

            elif tag == "if":
                _, cond, then_blk, elif_p, else_p = node
                ct = self.visit(cond)
                if ct is not None and ct != "bool":
                    raise SemanticError("Condition of if must be bool")
                self.visit(then_blk)
                self.visit(elif_p)
                self.visit(else_p)

            elif tag == "elif":
                _, cond, blk, next_elif = node
                ct = self.visit(cond)
                if ct is not None and ct != "bool":
                    raise SemanticError("Condition of elif must be bool")
                self.visit(blk)
                self.visit(next_elif)

            elif tag == "while":
                _, cond, blk = node
                ct = self.visit(cond)
                if ct is not None and ct != "bool":
                    raise SemanticError("Condition of while must be bool")
                self.visit(blk)

            elif tag == "for":
                _, init, cond, step, blk = node
                self.symtab.enter_scope("for_loop")
                self.visit(init)
                ct = self.visit(cond)
                if ct is not None and ct != "bool":
                    raise SemanticError("Condition of for must be bool")
                self.visit(step)
                self.visit(blk)
                self.symtab.exit_scope()

            elif tag == "print":
                self.visit(node[1])

            elif tag == "input":
                self.symtab.lookup(node[1])

            elif tag == "return":
                if self.current_function is None:
                    raise SemanticError("Return outside of function")
                if node[1] is not None:
                    raise SemanticError("Void function cannot return a value")

            elif tag == "binop":
                _, op, l, r = node
                lt = self.visit(l)
                rt = self.visit(r)

                if lt is None or rt is None:
                    return None

                if op in ("&&", "||"):
                    if lt != "bool" or rt != "bool":
                        raise SemanticError("Logical operators require bool")
                    return "bool"

                if op in ("<", "<=", ">", ">=", "==", "!="):
                    if lt != rt:
                        raise SemanticError("Type mismatch in comparison")
                    return "bool"

                return self.numeric_result(lt, rt)

            elif tag == "unary":
                _, op, expr = node
                et = self.visit(expr)
                if et is None:
                    return None
                if op == "!" and et != "bool":
                    raise SemanticError("Logical NOT requires bool")
                if op == "-" and et not in ("int", "float"):
                    raise SemanticError("Unary minus requires numeric")
                return et

            elif tag == "literal":
                v = node[1]
                if v in ("true", "false"):
                    return "bool"
                if isinstance(v, int):
                    return "int"
                if isinstance(v, float):
                    return "float"
                if isinstance(v, str) and len(v) == 1:
                    return "char"
                return "string"

            elif tag == "call":
                _, name, args = node
                info = self.symtab.lookup(name)

                if info["type"] != "func":
                    raise SemanticError(f"'{name}' is not a function")

                if args is None:
                    args = []

                params = info["params"] or []
                if len(params) != len(args):
                    raise SemanticError("Function argument count mismatch")

                for (_, pt, _), a in zip(params, args):
                    at = self.visit(a)
                    if at is not None:
                        self.check_assignment(pt, at)

                raise SemanticError("Void function used in expression")

        except SemanticError as e:
            self.errors.append(str(e))
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
