# 1. Architecture Diagram


```text
                         JavaScript Source Code
                                   │
                                   ▼
                        ┌──────────────────┐
                        │      Lexer       │
                        │   (lexer.py)     │
                        └──────────────────┘
                                   │
                                   ▼
                             Token Stream
                                   │
                                   ▼
                        ┌──────────────────┐
                        │      Parser      │
                        │ (parser_ast.py)  │
                        └──────────────────┘
                                   │
                                   ▼
                          Abstract Syntax Tree
                                   │
                                   ▼
                ┌──────────────────────────────────┐
                │         Evaluator                │
                │       (evaluator.py)             │
                └──────────────────────────────────┘
                       ▲                    ▲
                       │                    │
                       │                    │
         ┌─────────────────────┐   ┌─────────────────────┐
         │    Environment      │   │      JS Types       │
         │  (environment.py)   │   │   (js_types.py)     │
         └─────────────────────┘   └─────────────────────┘
                       │                    │
                       └──────────┬─────────┘
                                  │
                                  ▼
                               stdout
```

---

# 2. Working Overview

```markdown
# Working Overview

This project follows the classic interpreter pipeline:

Source Code
    ↓
Lexer
    ↓
Tokens
    ↓
Parser
    ↓
AST
    ↓
Evaluator
    ↓
Output
```


## 1. Lexer (`lexer.py`)

* Converts raw JavaScript text into tokens.
* Uses regular expressions.
* Recognizes:

  * Keywords
  * Operators
  * Identifiers
  * Strings
  * Numbers
  * Comments

Example:

```js
let x = 10;
```

becomes

```python
[
 Token(LET, "let"),
 Token(IDENTIFIER, "x"),
 Token(ASSIGN, "="),
 Token(NUMBER, 10),
 Token(SEMICOLON, ";")
]
```

---

## 2. Parser (`parser_ast.py`)

* Reads token stream.
* Creates AST nodes.
* Preserves program structure.
* Uses Pratt Parsing for operator precedence.

Example:

```js
let x = 10 + 20;
```

becomes

```text
VarDecl
│
├── x
│
└── BinaryExpr(+)
     ├── 10
     └── 20
```

---

## 3. Environment (`environment.py`)

* Stores variables.
* Handles scopes.
* Supports closures.

Example:

```js
let x = 10;
```

creates

```python
{
   "x": 10
}
```

---

## 4. JS Types (`js_types.py`)

Provides JavaScript behavior:

* JSArray
* JSObject
* JSDate
* Math
* Type coercion

Example:

```js
"10" + 20
```

becomes

```js
"1020"
```

through `js_add()`.

---

## 5. Evaluator (`evaluator.py`)

* Walks AST.
* Executes statements.
* Creates function scopes.
* Handles loops and conditionals.
* Calls built-in methods.

Example:

```js
console.log(10 + 20);
```

prints

```text
30
```

---

# 3. End-to-End Example

## Example JS Code

```js
let x = 10;
let y = 20;

function add(a, b) {
    return a + b;
}

let result = add(x, y);

console.log(result);
```

---

# Stage 1: Source Code

Input to interpreter:

```js
let x = 10;
let y = 20;

function add(a, b) {
    return a + b;
}

let result = add(x, y);

console.log(result);
```

---

# Stage 2: Lexer

Lexer converts characters into tokens.

Output:

```python
[
 Token(LET, "let"),
 Token(IDENTIFIER, "x"),
 Token(ASSIGN, "="),
 Token(NUMBER, 10),
 Token(SEMICOLON, ";"),

 Token(LET, "let"),
 Token(IDENTIFIER, "y"),
 Token(ASSIGN, "="),
 Token(NUMBER, 20),
 Token(SEMICOLON, ";"),

 Token(FUNCTION, "function"),
 Token(IDENTIFIER, "add"),
 Token(LPAREN, "("),
 Token(IDENTIFIER, "a"),
 Token(COMMA, ","),
 Token(IDENTIFIER, "b"),
 Token(RPAREN, ")"),

 ...
]
```

Think:

```text
Source Code
    ↓
Words + Symbols
    ↓
Tokens
```

---

# Stage 3: Parser

Parser converts tokens into AST.

Output:

```text
Program
│
├── VarDecl
│     name = x
│     value = 10
│
├── VarDecl
│     name = y
│     value = 20
│
├── FunctionDecl add(a,b)
│      │
│      └── ReturnStmt
│              │
│              └── BinaryExpr(+)
│                     ├── Identifier(a)
│                     └── Identifier(b)
│
├── VarDecl result
│      │
│      └── CallExpr
│             add(x,y)
│
└── ExpressionStmt
        │
        └── CallExpr
               console.log(result)
```

Now the interpreter understands the **structure**.

---

# Stage 4: Evaluator Starts

```python
evaluator.evaluate(program)
```

Calls:

```python
eval_Program()
```

---

# Stage 5: Function Hoisting

Before executing anything:

```js
function add(a,b){...}
```

gets stored first.

Environment becomes:

```python
Global Environment

{
   add : JSFunction
}
```

---

# Stage 6: Execute First Statement

AST:

```text
VarDecl x = 10
```

Runs:

```python
eval_VarDecl()
```

Environment:

```python
{
   add : JSFunction,
   x   : 10
}
```

---

# Stage 7: Execute Second Statement

AST:

```text
VarDecl y = 20
```

Environment:

```python
{
   add : JSFunction,
   x   : 10,
   y   : 20
}
```

---

# Stage 8: Execute Function Call

AST:

```text
add(x,y)
```

Evaluator sees:

```python
CallExpr
```

Runs:

```python
eval_CallExpr()
```

---

## Evaluate Arguments

Gets:

```python
x → 10
y → 20
```

Arguments:

```python
[10, 20]
```

---

## Create Function Scope

```python
call_function()
```

Creates new environment:

```python
Function Environment

{
   a : 10,
   b : 20
}
```

Parent:

```python
Global Environment
```

---

# Stage 9: Execute Function Body

Function AST:

```text
ReturnStmt
    │
    └── BinaryExpr(+)
           ├── a
           └── b
```

Evaluate:

```python
10 + 20
```

Result:

```python
30
```

Return:

```python
ReturnException(30)
```

caught by:

```python
call_function()
```

returns:

```python
30
```

---

# Stage 10: Store Result

AST:

```text
let result = add(x,y)
```

Environment:

```python
{
   add    : JSFunction,
   x      : 10,
   y      : 20,
   result : 30
}
```

---

# Stage 11: console.log(result)

AST:

```text
CallExpr
│
├── console
└── log
```

Evaluator:

```python
eval_CallExpr()
```

Finds:

```python
console.log
```

which is:

```python
lambda *args:
    print(...)
```

Argument:

```python
result → 30
```

---

# Stage 12: Output

Python executes:

```python
print("30")
```

Output:

```text
30
```

---

# Complete Flow Diagram

```text
JS Source
│
│ let x = 10;
│ let y = 20;
│
▼
Lexer
│
▼
Tokens
│
│ [LET, IDENTIFIER(x), ASSIGN, NUMBER(10), ...]
│
▼
Parser
│
▼
AST
│
│ Program
│ ├── VarDecl(x)
│ ├── VarDecl(y)
│ ├── FunctionDecl(add)
│ ├── VarDecl(result)
│ └── console.log(...)
│
▼
Evaluator
│
├── Create Global Environment
│
├── Hoist Function add()
│
├── Store x = 10
│
├── Store y = 20
│
├── Call add(10,20)
│      │
│      ├── Create Function Scope
│      │      a = 10
│      │      b = 20
│      │
│      └── Return 30
│
├── Store result = 30
│
└── console.log(30)
│
▼
stdout
│
▼
30
```

This single flow contains **everything your interpreter does**:
**Source → Tokens → AST → Environment → Evaluation → Output**. This is essentially how real interpreters (Python, Ruby, early JavaScript engines) work internally.
