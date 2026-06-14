# Custom JavaScript Runtime in Python

This project is a custom, fully-featured JavaScript runtime built from scratch in Python. It parses and executes JavaScript code with standard JS scoping, coercion, control flow, functions, callbacks, closures, and standard library behaviors.

## Project Architecture

The interpreter is divided into clean, modular components:

```
                  +-----------------------------------+
                  |        JavaScript Source          |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------+-----------------+
                  |      Lexical Analyzer (Lexer)     |
                  +-----------------+-----------------+
                                    | Token Stream
                                    v
                  +-----------------+-----------------+
                  |       AST Parser (Pratt)          |
                  +-----------------+-----------------+
                                    | AST (Nodes)
                                    v
+-----------------+       +---------+---------+       +-----------------+
|   Environment   | <---> |   AST Evaluator   | <---> | JS Type Wrappers|
| (Scope Chains)  |       +---------+---------+       |  and Coercion   |
+-----------------+                 |                 +-----------------+
                                    v
                  +-----------------+-----------------+
                  |             stdout                |
                  +-----------------------------------+
```

---

## File Structure

- **`js_run.py`**: The command-line entrypoint. It reads the source JS code, runs tokenization, parses into an AST, and executes it inside the evaluator.
- **`lexer.py`**: A regular-expression-based token compiler. It tokenizes JavaScript keywords, operations, comments, and identifiers.
- **`parser_ast.py`**: Defines AST nodes and implements a Recursive Descent & Pratt Parser to resolve operator precedence and expression hierarchy.
- **`environment.py`**: Handles lexical scope environments, variable bindings, closures, constant safety, and parent scope lookup.
- **`js_types.py`**: Implements JavaScript's coercion rules (e.g. loose `==` vs strict `===` equality, additions) and native type wrappers (`JSArray`, `JSObject`, `JSDate`, `JSMath`).
- **`evaluator.py`**: A visitor-pattern AST evaluator that interprets JS semantics (scoping, functions, hoisting, loops, switch statements, and flow control).

---

## Executing Code

### Prerequisites
- Python 3.x

### Running JavaScript files
To run a JavaScript file with this runtime:
```bash
py js_run.py <path-to-file.js>
```
For example:
```bash
py js_run.py advanced_tests.js
```
---
### Alternative Installation method
This is published in PyPI as well
#### Install from PyPI

```bash
pip install viswa-js-interpreter
```
#### Verify Installation

```bash
jsrun sample.js
```

Example:

```bash
jsrun advanced_tests.js
```
---

## JavaScript Features Supported

1. **Variables & Scoping**: `let`, `const`, and `var` bindings. Supports block scoping, shadowing, and closure scoping.
2. **Control Flow**:
   - `if`, `else if`, `else` conditionals.
   - `for`, `while`, `do...while` loops with full support for `break` and `continue`.
   - `switch`/`case`/`default` statement with fallthrough capabilities.
3. **Data Types**:
   - Primitive types (`number`, `string`, `boolean`, `null`, `undefined`).
   - Reference types (`JSObject`, `JSArray`).
4. **Functions & Closures**:
   - Standard function declarations and function expressions.
   - Arrow functions `(x) => x * 2` (both expression bodies and block bodies).
   - Functions support closure variables, `this` context preservation, callbacks, and rest parameters `(...args)`.
5. **Array Operations**:
   - Methods: `push`, `pop`, `shift`, `unshift`, `slice`, `splice`, `concat`, `includes`, `indexOf`, `join`, `sort`, `reverse`.
   - High-order callback methods: `map`, `filter`, `reduce`, `find`, `some`, `every`.
6. **String Operations**:
   - Methods: `split`, `slice`, `substring`, `trim`, `toUpperCase`, `toLowerCase`, `includes`, `startsWith`, `endsWith`, `indexOf`, `replace`, `replaceAll`.
7. **Built-in Objects**:
   - **`Math`**: constants (`Math.PI`, `Math.E`, etc.) and operations (`Math.floor`, `Math.random`, `Math.max`, `Math.min`, `Math.abs`, `Math.pow`, `Math.sqrt`).
   - **`Date`**: date objects created via `new Date(...)` and getter methods.
8. **Operators & Expressions**:
   - Unary and Binary math operations.
   - Spread operator `[...arr]` in array literals and function call arguments.
   - JavaScript-style type coercions (loose vs strict comparison, string concatenation).

---

## Architectural Highlights (Tie-Breakers)

### Pratt Parsing (Top-Down Operator Precedence)
Instead of a simple naive parser, this project uses a Pratt Parser. This allows elegant handling of complex expressions like `a.b.c() + d ** e * f` by assigning binding powers (precedence) to infix and prefix operators.

### Function Hoisting
The evaluator executes blocks in two passes. The first pass hoists function declarations into their respective block scope environment. The second pass evaluates instructions. This means functions can be called before they are declared, matching native JS behavior.

### JS-Style Scoping & `this` Context
Arrow functions bind `this` lexically (inheriting from the context where they were created). Regular functions establish a new execution scope binding `this` to the executing object context, enabling true OOP capabilities.
