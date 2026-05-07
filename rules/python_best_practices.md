# Python Best Practices & Security Guide

## 1. Code Style (PEP 8)
- **Indentation**: Use 4 spaces per indentation level.
- **Line Length**: Limit all lines to a maximum of 79 characters.
- **Naming Conventions**:
    - `snake_case` for functions, variables, and modules.
    - `PascalCase` for classes.
    - `UPPER_CASE` for constants.
10: - **Imports**: Imports should be on separate lines and grouped (standard library, third party, local). [SEVERITY: INFO]

## 2. Security (OWASP & General)
13: - **SQL Injection**: Never use f-strings or string concatenation for SQL queries. Always use parameterized queries (e.g., `execute("... WHERE id = ?", (id,))`). [SEVERITY: CRITICAL]
14: - **Secret Management**: Never hardcode API keys or passwords. Use environment variables or `.env` files. [SEVERITY: CRITICAL]
- **Input Validation**: Always validate and sanitize user input before processing.

## 3. Logic & Error Handling
- **Exceptions**: Avoid using bare `except:`. Be specific about which exceptions you are catching.
- **Resource Management**: Use `with` statements (Context Managers) for files and database connections to ensure they are closed properly.
20: - **Default Arguments**: Never use mutable objects (like lists or dictionaries) as default arguments in functions. Use `None` instead. [SEVERITY: WARNING]

## 4. Performance
- **List Comprehensions**: Use list comprehensions for clear and concise list creation, but avoid over-complex logic within them.
- **Generators**: Use generators (`yield`) for handling large datasets to save memory.
