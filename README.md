---

# 🖥️ MyLang Compiler

A **Python-based compiler** for a custom C-like language, `MyLang`, capable of parsing, compiling, and running `.my` programs.

---

## ⚡ Usage

Run your `.my` program with:

```bash
python -m compiler.main test1.my --emit test.py --run
python compile.py test.my --mode native --output myapp --run

```

* `test1.my` → your MyLang source file
* `--emit test.py` → generates equivalent Python code
* `--run` → executes the generated Python program

---

## 📜 Language Grammar

The MyLang language is structured as follows:

### **Program Structure**

```
<program> ::= <function>+
```

### **Function Declaration**

```
<function> ::= "func" <type> <identifier> "(" <params> ")" "{" <statement>* "}"
<params>   ::= <param> ("," <param>)* | ε
<param>    ::= <type> <identifier>
<type>     ::= "int" | "float" | "string" | "bool" | "void"
```

---

### **Statements**

```
<statement> ::= <var_decl>
              | <expr_stmt>
              | <if_stmt>
              | <while_stmt>
              | <for_stmt>
              | <return_stmt>
```

#### Variable Declaration

```
<var_decl> ::= <type> <var_init> ("," <var_init>)* ";"
<var_init> ::= <identifier> | <identifier> "=" <expr>
```

#### Expression Statement

```
<expr_stmt> ::= <expr> ";"
```

#### Conditional Statements

```
<if_stmt> ::= "if" "(" <expr> ")" "{" <statement>* "}" 
              ("else" "{" <statement>* "}")?
```

#### Loops

```
<while_stmt> ::= "while" "(" <expr> ")" "{" <statement>* "}"
<for_stmt>   ::= "for" "(" <for_init> ";" <expr>? ";" <expr>? ")" "{" <statement>* "}"
<for_init>   ::= <var_decl> | <expr> ";" | ";"
```

#### Return Statement

```
<return_stmt> ::= "return" <expr>? ";"
```

---

### **Expressions**

```
<expr>        ::= <assignment> | <logical_or>
<assignment>  ::= <identifier> "=" <expr>
<logical_or>  ::= <logical_and> ("||" <logical_and>)*
<logical_and> ::= <equality> ("&&" <equality>)*
<equality>    ::= <relational> (("==" | "!=") <relational>)*
<relational>  ::= <additive> (("<" | ">" | "<=" | ">=") <additive>)*
<additive>    ::= <multiplicative> (("+" | "-") <multiplicative>)*
<multiplicative> ::= <unary> (("*" | "/" | "%") <unary>)*
<unary>       ::= ("+" | "-" | "!") <unary> | <primary>
<primary>     ::= <number> | <string> | <boolean> | <identifier> | <func_call> | "(" <expr> ")"
<func_call>   ::= <identifier> "(" <args> ")"
<args>        ::= <expr> ("," <expr>)* | ε
```

---

### **Literals & Identifiers**

```
<identifier> ::= [A-Za-z_][A-Za-z0-9_]*
<number>     ::= [0-9]+ ("." [0-9]+)?
<string>     ::= '"' ([^"\\] | "\\".)* '"'
<boolean>    ::= "true" | "false"
```

---

## 🌟 Features

* Function definitions with typed parameters and return values
* Variable declarations with types (`int`, `float`, `string`, `bool`)
* Arithmetic, logical, and relational expressions
* Control flow: `if-else`, `while`, `for` loops
* Function calls with arguments
* `return` statements and expression evaluation
* Print support via generated Python code

