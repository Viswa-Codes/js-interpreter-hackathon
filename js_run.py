import sys
from lexer import tokenize
from parser_ast import Parser
from evaluator import Evaluator

def main():
    if len(sys.argv) < 2:
        print("Usage: python js_run.py <file.js>")
        sys.exit(1)
        
    filename = sys.argv[1]
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
        
    try:
        tokens = tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse()
        
        evaluator = Evaluator()
        evaluator.evaluate(ast, evaluator.global_env)
    except SyntaxError as se:
        print(f"SyntaxError: {se}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
