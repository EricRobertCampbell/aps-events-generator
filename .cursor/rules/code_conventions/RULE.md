---
description: "Code conventions for string concatenation and Python style"
alwaysApply: true
---

# Code Conventions

## String Concatenation
- Do not concatenate strings by placing them next to each other (e.g., `"string1" "string2"`)
- Prefer f-strings over `+` operator for string concatenation
- Use explicit `+` concatenation only when f-strings are not practical (e.g., for very long multi-line strings)
- For multi-line strings, prefer triple-quoted f-strings or explicit `+` concatenation

## Code Style
- Use type hints throughout
- Add comprehensive docstrings with examples
- Follow Python best practices and PEP 8

## Function Organization
- Organize functions following clean code principles: more general functions at the top, more specific functions lower down
- Entry point functions (like `main()`) should be at the top
- Functions called by higher-level functions should appear below them in the call hierarchy
- Helper/utility functions should be at the bottom

