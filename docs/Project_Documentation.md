# C-like Compiler Project Documentation

## Overview
This project implements a recursive descent parser for a C-like language, built upon a custom scanner.

## Recent Changes (Refactoring)
The project file structure has been reorganized to follow software engineering best practices:

- **Source Code (`src/`)**:
  - `scanner.py`: The lexical analyzer.
  - `parser.py`: The syntax analyzer (Parser).
- **Tests (`tests/`)**:
  - `test_parser.py`: Automated test suite verifying the parser against various code samples.
- **Documentation (`docs/`)**:
  - `grammar_rules.txt`: The original grammar definition.
  - `Project_Documentation.md`: This file.
- **Legacy (`legacy/`)**:
  - Files from previous iterations (`parser_implement.py`, `parser_v1.py`).
- **Logs (`logs/`)**:
  - Output logs from test runs.

## Architecture

1.  **Scanner (`src/scanner.py`)**:
    -   Reads raw C-like source code.
    -   Produces a stream of `Token` objects (Keywords, Identifiers, Operators, etc.).

2.  **Parser (`src/parser.py`)**:
    -   Consumes the stream of tokens.
    -   Implements a Recursive Descent strategy matching the grammar rules.
    -   Grammar includes:
        -   Variable Declarations (`int x;`)
        -   Assignments (`x = 5;`)
        -   Control Flow (`if`, `while`, `for`)
        -   Blocks (`{ ... }`)
        -   Expressions (Arithmetic, Relational, Logical)

## How to Run

### Interactive Mode
To run the parser interactively:
```bash
python src/parser.py
```

### Running Tests
To run the verification suite:
```bash
python tests/test_parser.py
```
This will generate/update the log file at `logs/test_log.txt`.
