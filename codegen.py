class ThreeAddressCode:
    def __init__(self):
        self.code = []
        self.temp_counter = 0
        self.label_counter = 0
    
    def new_temp(self):
        """ایجاد یک متغیر موقت جدید."""
        self.temp_counter += 1
        return f"t{self.temp_counter}"
    
    def new_label(self):
        """ایجاد یک برچسب جدید."""
        self.label_counter += 1
        return f"L{self.label_counter}"
    
    def add(self, op, arg1, arg2, result):
        """افزودن یک دستور به کد سه آدرسی."""
        self.code.append((op, str(arg1), str(arg2), str(result)))
    
    def print_code(self):
        """چاپ کد سه آدرسی."""
        for i, (op, a1, a2, res) in enumerate(self.code):
            print(f"{i}: ({op}, {a1}, {a2}, {res})")

class CodeGenerator:
    def __init__(self, ast, symtab=None):
        self.ast = ast
        self.tac = ThreeAddressCode()
        self.symbol_table = symtab or {}
    
    def generate(self):
        """تولید کد سه آدرسی از AST."""
        self.visit(self.ast)
        return self.tac
    
    def visit(self, node):
        """پیمایش درخت AST و تولید کد میانه."""
        if node is None:
            return None
        
        # پردازش لیست‌ها
        if isinstance(node, list):
            results = []
            for n in node:
                result = self.visit(n)
                if result is not None:
                    results.append(result)
            return results
        
        tag = node[0]
        
        # برنامه اصلی
        if tag == "program":
            statements = node[1]
            return self.visit(statements)
        
        # دستور (stmt)
        elif tag == "stmt":
            stmt_content = node[1]
            return self.visit(stmt_content)
        
        # تعریف متغیر
        elif tag == "var_decl":
            _, var_type, name, expr = node
            if expr is not None:
                expr_temp = self.visit(expr)
                self.tac.add("=", expr_temp, "_", name)
            return name
        
        # تعریف آرایه
        elif tag == "var_decl_array":
            _, var_type, name, size = node
            # آرایه‌ها فعلاً ساده
            return name
        
        # انتساب
        elif tag == "assign":
            _, loc, expr = node
            expr_temp = self.visit(expr)
            loc_name = self.visit(loc)
            self.tac.add("=", expr_temp, "_", loc_name)
            return loc_name
        
        # عملگر دو تایی
        elif tag == "binop":
            _, op, left, right = node
            left_temp = self.visit(left)
            right_temp = self.visit(right)
            result_temp = self.tac.new_temp()
            
            # تبدیل عملگرها به فرم TAC
            op_map = {
                '+': '+', '-': '-', '*': '*', '/': '/', '%': '%',
                '&&': 'and', '||': 'or',
                '==': '==', '!=': '!=',
                '<': '<', '>': '>', '<=': '<=', '>=': '>='
            }
            tac_op = op_map.get(op, op)
            
            self.tac.add(tac_op, left_temp, right_temp, result_temp)
            return result_temp
        
        # عملگر یک تایی
        elif tag == "unary":
            _, op, expr = node
            expr_temp = self.visit(expr)
            result_temp = self.tac.new_temp()
            
            if op == "-":
                self.tac.add("uminus", expr_temp, "_", result_temp)
            elif op == "!":
                self.tac.add("not", expr_temp, "_", result_temp)
            
            return result_temp
        
        # مقادیر ثابت
        elif tag == "literal":
            value = node[1]
            # برای رشته‌ها و کاراکترها
            if isinstance(value, str):
                # اگر رشته است
                if len(value) > 1 or value in ['true', 'false']:
                    temp = self.tac.new_temp()
                    self.tac.add("=", f'"{value}"', "_", temp)
                    return temp
                # اگر کاراکتر است
                else:
                    temp = self.tac.new_temp()
                    self.tac.add("=", f"'{value}'", "_", temp)
                    return temp
            else:
                temp = self.tac.new_temp()
                self.tac.add("=", value, "_", temp)
                return temp
        
        # محل متغیر
        elif tag == "loc":
            return node[1]
        
        # محل آرایه
        elif tag == "loc_array":
            _, name, index = node
            index_temp = self.visit(index)
            temp = self.tac.new_temp()
            self.tac.add("[]", name, index_temp, temp)
            return temp
        
        # چاپ
        elif tag == "print":
            _, expr = node
            expr_temp = self.visit(expr)
            self.tac.add("print", expr_temp, "_", "_")
            return None
        
        # خواندن از ورودی
        elif tag == "input":
            _, var_name = node
            self.tac.add("input", "_", "_", var_name)
            return var_name
        
        # بلوک
        elif tag == "block":
            _, stmts = node
            return self.visit(stmts)
        
        # دستور if
        elif tag == "if":
            _, cond, then_block, elif_part, else_part = node
            
            else_label = self.tac.new_label()
            end_label = self.tac.new_label()
            
            # شرط
            cond_temp = self.visit(cond)
            self.tac.add("ifFalse", cond_temp, "_", else_label)
            
            # then بخش
            self.visit(then_block)
            self.tac.add("goto", "_", "_", end_label)
            
            # else بخش
            self.tac.add("label", "_", "_", else_label)
            if else_part:
                self.visit(else_part)
            
            self.tac.add("label", "_", "_", end_label)
            return None
        
        # دستور while
        elif tag == "while":
            _, cond, block = node
            
            start_label = self.tac.new_label()
            end_label = self.tac.new_label()
            
            self.tac.add("label", "_", "_", start_label)
            
            # شرط
            cond_temp = self.visit(cond)
            self.tac.add("ifFalse", cond_temp, "_", end_label)
            
            # بدنه حلقه
            self.visit(block)
            self.tac.add("goto", "_", "_", start_label)
            
            self.tac.add("label", "_", "_", end_label)
            return None
        
        # دستور for
        elif tag == "for":
            _, init, cond, step, block = node
            
            start_label = self.tac.new_label()
            end_label = self.tac.new_label()
            
            # مقداردهی اولیه
            self.visit(init)
            
            self.tac.add("label", "_", "_", start_label)
            
            # شرط
            cond_temp = self.visit(cond)
            self.tac.add("ifFalse", cond_temp, "_", end_label)
            
            # بدنه حلقه
            self.visit(block)
            
            # گام
            self.visit(step)
            self.tac.add("goto", "_", "_", start_label)
            
            self.tac.add("label", "_", "_", end_label)
            return None
        
        # دستور return
        elif tag == "return":
            if len(node) > 1:
                expr = node[1]
                if expr is not None:
                    expr_temp = self.visit(expr)
                    self.tac.add("return", expr_temp, "_", "_")
            else:
                self.tac.add("return", "_", "_", "_")
            return None
        
        # فراخوانی تابع
        elif tag == "call":
            _, func_name, args = node
            if args is None:
                args = []
            
            # پردازش آرگومان‌ها
            arg_temps = []
            for arg in args:
                arg_temp = self.visit(arg)
                arg_temps.append(arg_temp)
            
            # اگر تابع مقداری برگرداند
            if func_name != "print" and func_name != "input":
                result_temp = self.tac.new_temp()
                arg_str = ",".join(arg_temps)
                self.tac.add("call", func_name, arg_str, result_temp)
                return result_temp
            else:
                # برای print/input قبلاً پردازش شده
                return None
        
        # تعریف تابع (فعلاً ساده)
        elif tag == "func_decl":
            _, name, params, body = node
            self.tac.add("func", name, "_", "_")
            self.visit(body)
            self.tac.add("endfunc", "_", "_", "_")
            return None
        
        # هشدار برای nodeهای پردازش نشده
        else:
            print(f"Warning: Unhandled node type '{tag}' in code generation")
            return None
