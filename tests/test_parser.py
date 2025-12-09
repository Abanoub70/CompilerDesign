import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from parser import Parser
from scanner import tokenize

test_cases = [
    {
        "name": "Simple Declaration and Assignment",
        "code": """
        int x;
        float y;
        x = 5;
        y = 3.14;
        """,
        "should_pass": True
    },
    {
        "name": "Arithmetic Precedence",
        "code": """
        int x;
        x = 5 + 3 * 2;
        """,
        "should_pass": True
    },
    {
        "name": "Complex Logic and Parentheses",
        "code": """
        bool val;
        val = (5 > 3) == true;
        """,
        "should_pass": True
    },
    {
        "name": "If Else",
        "code": """
        int x;
        if (x > 10) {
            x = 0;
        } else {
            x = 1;
        }
        """,
        "should_pass": True
    },
    {
        "name": "While Loop",
        "code": """
        int i;
        i = 0;
        while (i < 10) {
            i = i + 1;
        }
        """,
        "should_pass": True
    },
    {
        "name": "For Loop",
        "code": """
        int i;
        int max;
        for (i = 0; i < 10; i = i + 1) h = 5;
        """,
        "should_pass": True
    },
    {
        "name": "Nested Blocks",
        "code": """
        {
            int x;
            x = 1;
            {
                x = 2;
            }
        }
        """,
        "should_pass": True
    },
    {
        "name": "Syntax Error - Missing Semicolon",
        "code": """
        int x
        """,
        "should_pass": False
    },
    {
        "name": "Syntax Error - Bad Expression",
        "code": """
        x = 5 + * 3;
        """,
        "should_pass": False
    },
    {
        "name": "Syntax Error - Unbalanced Braces",
        "code": """
        if (true) {
            x = 1;
        
        """,
        "should_pass": False
    }
]

def run_tests():
    log_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'test_log.txt')
    with open(log_path, "w") as f:
        f.write("Running Tests...\n\n")
        passed = 0
        failed = 0
        
        for case in test_cases:
            f.write(f"Test: {case['name']}\n")
            code = case['code']
            should_pass = case['should_pass']
            
            try:
                tokens = tokenize(code)
                # f.write(f"Tokens: {tokens}\n")
                parser = Parser(tokens)
                result = parser.parse()
                if should_pass:
                    f.write("Result: PASSED (Accepted)\n")
                    passed += 1
                else:
                    f.write(f"Result: FAILED (Accepted but expected Error)\n")
                    failed += 1
            except SyntaxError as e:
                if not should_pass:
                    f.write(f"Result: PASSED (Caught expected error: {e})\n")
                    passed += 1
                else:
                    f.write(f"Result: FAILED (Unexpected error: {e})\n")
                    failed += 1
            except Exception as e:
                f.write(f"Result: FAILED (System Error: {e})\n")
                failed += 1
            f.write("-" * 30 + "\n")
        
        f.write(f"\nTotal: {passed + failed}, Passed: {passed}, Failed: {failed}\n")
        print(f"Tests completed. Total: {passed + failed}, Passed: {passed}, Failed: {failed}")

if __name__ == "__main__":
    run_tests()
