"""Shared helpers for JS source content assertions across UI test files."""

import re


def _extract_function_body(content: str, fn_name: str) -> str:
    """Extract the body of a named function from JS source using brace-matching.

    Handles both declaration form (function name(...) {) and assignment form
    (name = function(...) { or async function name(...) {).
    Returns the text between the outermost braces (exclusive).
    Returns an empty string if the function is not found.
    """
    pattern = (
        rf"(?:async\s+)?(?:function\s+{fn_name}\s*\([^)]*\)"
        rf"|{fn_name}\s*=\s*(?:async\s+)?(?:function\s*\([^)]*\)|\([^)]*\)\s*=>))"
        rf"\s*\{{"
    )
    match = re.search(pattern, content)
    if match is None:
        return ""
    start = match.end() - 1
    depth = 0
    for i, ch in enumerate(content[start:]):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return content[start + 1 : start + i]
    return ""
