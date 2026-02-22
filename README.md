# ⚙️ Python-Based Academic Compiler Pipeline

A comprehensive frontend compiler implementation built with Python and PLY (Python Lex-Yacc). This project demonstrates a deep understanding of language processing, transforming raw source code through theoretical computer science phases: Lexical Analysis, Syntax Parsing, Semantic Analysis, and Intermediate Representation (IR).

## 🔬 Academic Overview & Architecture

This project is structured based on classic compiler design principles. It processes a custom C-like syntax and outputs **Three-Address Code (TAC)**. The compiler is equipped with a modern Graphical User Interface (GUI) allowing users and researchers to visualize the data transformation at each phase.

The pipeline consists of four distinct theoretical phases:

1. **Lexical Analysis (Scanner):** Utilizes Regular Expressions to convert a stream of characters into meaningful tokens.
2. **Syntax Analysis (Parser):** Implements a Context-Free Grammar (CFG) using an LALR(1) parser to construct an Abstract Syntax Tree (AST).
3. **Semantic Analysis:** Validates scope rules and type safety. It manages a hierarchical **Symbol Table** to detect undeclared variables or scope violations in $O(1)$ lookup time per scope level.
4. **Intermediate Code Generation (IR):** Traverses the AST to generate Three-Address Code (TAC). Every complex expression is broken down into fundamental operations of the form:
   $result = arg_1 \text{ op } arg_2$

## 🚀 Features

- **Modern GUI Integration:** Built with `CustomTkinter`, providing a dark-mode, tabbed interface to inspect Tokens, AST, Symbol Tables, and TAC in real-time.
- **Robust Error Handling:** Pinpoints exact line numbers for Lexical and Syntax errors.
- **Scope Management:** Supports nested scoping (Global and Local) during semantic analysis.
- **Control Flow Support:** Capable of generating IR for `if/else`, `while`, and `for` loops using dynamic label generation ($L_1, L_2$).

## 🛠️ Technology Stack

- **Core Logic:** Python 3.x
- **Compiler Tools:** `PLY` (Python Lex-Yacc)
- **Graphical Interface:** `CustomTkinter`, `Tkinter`

## 📦 Installation & Setup

Ensure you have Python 3.8+ installed. Clone the repository and install the required dependencies:
```bash
git clone https://github.com/mehrshadk84/CompilerPython.git
cd Compilerpython
pip install ply customtkinter
```
### Running the Compiler
Launch the Graphical Interface by running:

bash
python main.py
From the GUI, click **Load File** to import your `.txt` source code, then click **Run Compiler** to execute the pipeline.

## 🧠 Intermediate Representation (IR) Example

The `codegen.py` module converts high-level AST nodes into Three-Address Code. 

**Input (Source Code):**
c
int x = 10;
int y = 20;
int z = (x + y) * 2;

**Output (Generated TAC):**
text
0: (=, 10, _, x)
1: (=, 20, _, y)
2: (+, x, y, t1)
3: (*, t1, 2, t2)
4: (=, t2, _, z)
*(Here, $t_n$ represents temporary variables generated dynamically during AST traversal).*

## 🔮 Future Work / Roadmap

As this is an ongoing academic project, future implementations will focus on:
- **Code Optimization:** Implementing peephole optimization and dead-code elimination on the TAC.
- **Target Code Generation:** Translating the optimized TAC into machine code (x86 Assembly) or LLVM IR.

---
*Developed as a demonstration of Compiler Construction and Systems Programming.*


---

### 💡 چند پیشنهاد مهم برای قدم‌های بعدی:
1. **فایل `requirements.txt`:** از آنجایی که `customtkinter` نصب پیش‌فرض پایتون نیست، حتماً یک فایل به نام `requirements.txt` در پروژه بسازید و خطوط زیر را در آن قرار دهید (و روی گیت‌هاب کامیت کنید):
   
```text
   ply==3.11
   customtkinter==5.2.2
