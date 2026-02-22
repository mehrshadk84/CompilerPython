import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import customtkinter as ctk
import os
import sys

# Import modules from your project
from lexer import lexer, lex_errors
from parser import parser, errors
from semantic import SemanticAnalyzer
from codegen import CodeGenerator, ThreeAddressCode

# Set appearance
ctk.set_appearance_mode("dark")  # "dark", "light", "system"
ctk.set_default_color_theme("blue")

class CompilerGUI:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Compiler Project")
        self.window.geometry("1000x700")
        
        # Configure grid
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self.window, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)
        
        # Logo/Title
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="Compiler", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Buttons
        self.load_file_btn = ctk.CTkButton(
            self.sidebar, 
            text="Load File", 
            command=self.load_file
        )
        self.load_file_btn.grid(row=1, column=0, padx=20, pady=10)
        
        self.run_btn = ctk.CTkButton(
            self.sidebar, 
            text="Run Compiler", 
            command=self.run_compiler,
            fg_color="#2E7D32",
            hover_color="#1B5E20"
        )
        self.run_btn.grid(row=2, column=0, padx=20, pady=10)
        
        self.clear_btn = ctk.CTkButton(
            self.sidebar, 
            text="Clear All", 
            command=self.clear_all,
            fg_color="#D32F2F",
            hover_color="#B71C1C"
        )
        self.clear_btn.grid(row=3, column=0, padx=20, pady=10)
        
        # Theme toggle
        self.appearance_mode_label = ctk.CTkLabel(
            self.sidebar, 
            text="Theme:", 
            anchor="w"
        )
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        
        self.appearance_mode_menu = ctk.CTkOptionMenu(
            self.sidebar, 
            values=["Dark", "Light", "System"],
            command=self.change_theme
        )
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=(10, 20))
        
        # Main area - Notebook
        self.notebook = ctk.CTkTabview(self.window)
        self.notebook.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        
        # Create tabs
        self.tabs = ["Source Code", "Lexer", "Parser", "Semantic", "CodeGen"]
        for tab in self.tabs:
            self.notebook.add(tab)
        
        # Source code tab
        self.source_text = scrolledtext.ScrolledText(
            self.notebook.tab("Source Code"),
            font=("Consolas", 12),
            bg="#2b2b2b",
            fg="#ffffff",
            insertbackground="white"
        )
        self.source_text.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Lexer tab
        self.lexer_text = scrolledtext.ScrolledText(
            self.notebook.tab("Lexer"),
            font=("Consolas", 11),
            bg="#2b2b2b",
            fg="#ffffff",
            state="disabled"
        )
        self.lexer_text.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Parser tab
        self.parser_text = scrolledtext.ScrolledText(
            self.notebook.tab("Parser"),
            font=("Consolas", 11),
            bg="#2b2b2b",
            fg="#ffffff",
            state="disabled"
        )
        self.parser_text.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Semantic tab
        self.semantic_text = scrolledtext.ScrolledText(
            self.notebook.tab("Semantic"),
            font=("Consolas", 11),
            bg="#2b2b2b",
            fg="#ffffff",
            state="disabled"
        )
        self.semantic_text.pack(expand=True, fill="both", padx=5, pady=5)
        
        # CodeGen tab
        self.codegen_text = scrolledtext.ScrolledText(
            self.notebook.tab("CodeGen"),
            font=("Consolas", 11),
            bg="#2b2b2b",
            fg="#ffffff",
            state="disabled"
        )
        self.codegen_text.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Status bar
        self.status_bar = ctk.CTkLabel(
            self.window, 
            text="Ready", 
            anchor="w",
            font=("Segoe UI", 10)
        )
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 5))
    
    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Source File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                
                self.source_text.delete(1.0, tk.END)
                self.source_text.insert(1.0, content)
                self.status_bar.configure(text=f"Loaded: {os.path.basename(file_path)}")
                self.current_file = file_path
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def run_compiler(self):
        self.clear_results()
        source_code = self.source_text.get(1.0, tk.END).strip()

        if not source_code:
            messagebox.showwarning("Warning", "Source code is empty!")
            return

        self.status_bar.configure(text="Compiling...")
        self.window.update()

        try:
            lex_errors.clear()
            errors.clear()
            lexer.lineno = 1

            # === LEXER ===
            lexer.input(source_code)
            lexer_output = "TOKENS:\n" + "="*50 + "\n"

            while True:
                tok = lexer.token()
                if not tok:
                    break
                lexer_output += f"Line {tok.lineno:3}: {tok.type:15} = {tok.value}\n"

            if lex_errors:
                lexer_output += "\nLEXICAL ERRORS:\n" + "="*50 + "\n"
                for err in lex_errors:
                    lexer_output += f"{err}\n"

            self.update_text(self.lexer_text, lexer_output)

            if lex_errors:
                self.status_bar.configure(text="Lexical errors found!")
                return

            # === PARSER ===
            result = parser.parse(source_code, lexer=lexer)
            parser_output = "PARSE TREE:\n" + "="*50 + "\n"

            if errors:
                parser_output += "SYNTAX ERRORS:\n" + "="*50 + "\n"
                for err in errors:
                    parser_output += f"{err}\n"
            else:
                parser_output += "✓ Syntax is valid!\n\n"
                if result:
                    parser_output += "AST Structure (simplified):\n"
                    parser_output += str(result)[:500] + "...\n"

            self.update_text(self.parser_text, parser_output)

            if errors:
                self.status_bar.configure(text="Syntax errors found!")
                return

            # === SEMANTIC ANALYSIS (FIXED) ===
            semantic_analyzer = SemanticAnalyzer()
            sem_errors = semantic_analyzer.analyze(result)

            semantic_output = "SEMANTIC ANALYSIS:\n" + "="*50 + "\n"

            if sem_errors:
                semantic_output += "SEMANTIC ERRORS:\n" + "="*50 + "\n"
                for err in sem_errors:
                    semantic_output += f"{err}\n"
            else:
                semantic_output += "✓ Semantic analysis passed!\n\n"
                semantic_output += "Symbol Table:\n"
                semantic_output += "-"*30 + "\n"

                symtab = semantic_analyzer.symtab
                for i, (scope, name) in enumerate(zip(symtab.scopes, symtab.scope_names)):
                    semantic_output += f"Scope {i} ({name}):\n"
                    if scope:
                        for sym, info in scope.items():
                            semantic_output += f"  {sym}: {info}\n"
                    else:
                        semantic_output += "  (empty)\n"
                    semantic_output += "\n"

            self.update_text(self.semantic_text, semantic_output)

            if sem_errors:
                self.status_bar.configure(text="Semantic errors found!")
                return

            # === CODE GENERATION ===
            generator = CodeGenerator(result)
            tac = generator.generate()

            codegen_output = "THREE-ADDRESS CODE:\n" + "="*50 + "\n"
            for i, (op, a1, a2, res) in enumerate(tac.code):
                codegen_output += f"{i:3}: ({op}, {a1}, {a2}, {res})\n"

            if not tac.code:
                codegen_output += "No code generated.\n"

            self.update_text(self.codegen_text, codegen_output)
            self.status_bar.configure(text="Compilation successful! ✓")

        except Exception as e:
            messagebox.showerror("Compiler Error", str(e))
            self.status_bar.configure(text="Error during compilation")

    def update_text(self, text_widget, content):
        text_widget.config(state="normal")
        text_widget.delete(1.0, tk.END)
        text_widget.insert(1.0, content)
        text_widget.config(state="disabled")
    
    def clear_all(self):
        self.source_text.delete(1.0, tk.END)
        self.clear_results()
        self.status_bar.configure(text="Cleared all")
    
    def clear_results(self):
        for text_widget in [self.lexer_text, self.parser_text,
                           self.semantic_text, self.codegen_text]:
            text_widget.config(state="normal")
            text_widget.delete(1.0, tk.END)
            text_widget.config(state="disabled")
    
    def change_theme(self, new_theme):
        ctk.set_appearance_mode(new_theme.lower())
    
    def run(self):
        self.window.mainloop()

def main():
    required_modules = ['lexer.py', 'parser.py', 'semantic.py', 'codegen.py']
    missing = []

    for module in required_modules:
        if not os.path.exists(module):
            missing.append(module)

    if missing:
        print("Error: Missing required files:")
        for m in missing:
            print(f"  - {m}")
        return
    
    app = CompilerGUI()
    app.run()

if __name__ == "__main__":
    main()
