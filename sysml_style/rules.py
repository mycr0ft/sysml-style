"""
SML style lint rules.

Each rule is a function:
    rule(lines: list[str]) -> list[Issue]

Issue = (line_no: int, col: int, code: str, message: str)

Each rule function may accept keyword arguments (e.g. ``filename``).
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass
class Issue:
    line: int       # 1-based
    col: int        # 1-based, 0 = whole line
    code: str
    message: str
    fixable: bool = False

    def __str__(self) -> str:
        return f"line {self.line}:{self.col}: {self.code} {self.message}"


Rule = Callable[..., list[Issue]]
_registry: list[tuple[str, Rule]] = []


def rule(code: str):
    """Decorator to register a rule function."""
    def decorator(fn: Rule) -> Rule:
        _registry.append((code, fn))
        return fn
    return decorator


def all_rules() -> list[tuple[str, Rule]]:
    return list(_registry)


# ─── SML1xx — Whitespace ──────────────────────────────────────────────────────

@rule("SML101")
def check_operator_spacing(lines: list[str], **kwargs: object) -> list[Issue]:
    """Operators =, ->, ~>, :>> should have exactly one space on each side."""
    issues = []
    # = sign: not preceded/followed by space (but skip ==, :=, <=, >=, =>)
    for i, line in enumerate(lines, 1):
        stripped = _strip_strings_and_comments(line)
        # attribute mass=100  or  mass =100  or  mass= 100
        for m in re.finditer(r'(?<![=!<>:])=(?!=)', stripped):
            pos = m.start()
            before = stripped[pos-1] if pos > 0 else ' '
            after = stripped[pos+1] if pos+1 < len(stripped) else ' '
            if before != ' ' or after != ' ':
                issues.append(Issue(i, pos+1, "SML101",
                    "expected spaces around '=' operator", fixable=True))
    return issues


@rule("SML102")
def check_semicolon_spacing(lines: list[str], **kwargs: object) -> list[Issue]:
    """No space before ';'."""
    issues = []
    for i, line in enumerate(lines, 1):
        stripped = _strip_strings_and_comments(line)
        for m in re.finditer(r' +;', stripped):
            issues.append(Issue(i, m.start()+1, "SML102",
                "unexpected space before ';'", fixable=True))
    return issues


@rule("SML103")
def check_trailing_whitespace(lines: list[str], **kwargs: object) -> list[Issue]:
    """No trailing whitespace."""
    issues = []
    for i, line in enumerate(lines, 1):
        if line != line.rstrip('\n') and line.rstrip('\n') != line.rstrip():
            issues.append(Issue(i, len(line.rstrip())+1, "SML103",
                "trailing whitespace", fixable=True))
    return issues


@rule("SML104")
def check_indentation(lines: list[str], **kwargs: object) -> list[Issue]:
    """Indentation should be a multiple of 4 spaces (or consistent 3-space)."""
    issues = []
    # Detect dominant indent unit from file
    indent_counts: dict[int, int] = {}
    for line in lines:
        s = line.rstrip('\n')
        if s and s[0] == ' ':
            n = len(s) - len(s.lstrip(' '))
            if n > 0:
                indent_counts[n] = indent_counts.get(n, 0) + 1

    # Guess indent size: most common small indent
    unit = 4
    for size in [2, 3, 4]:
        if indent_counts.get(size, 0) > indent_counts.get(unit, 0):
            unit = size

    prev_ended = True
    for i, line in enumerate(lines, 1):
        s = line.rstrip('\n')
        stripped = s.strip()
        if not stripped:
            continue
        if not prev_ended:
            prev_ended = stripped.endswith(";") or stripped.endswith("}")
            continue
        if s[0] == ' ':
            n = len(s) - len(s.lstrip(' '))
            if n % unit != 0:
                issues.append(Issue(i, 1, "SML104",
                    f"indentation {n} is not a multiple of {unit}"))
        prev_ended = stripped.endswith(";") or stripped.endswith("}")
    return issues


@rule("SML105")
def check_blank_lines_between_defs(lines: list[str], **kwargs: object) -> list[Issue]:
    """Top-level definitions should be separated by a blank line."""
    issues = []
    top_def_keywords = re.compile(
        r'^\s{0,4}(package|part def|item def|action def|port def|'
        r'interface def|attribute def|requirement def|constraint def|'
        r'state def|use case def|analysis def)\b'
    )
    prev_def_line = None
    for i, line in enumerate(lines, 1):
        if top_def_keywords.match(line):
            if prev_def_line is not None:
                # Check if there's a blank line between them
                between = lines[prev_def_line:i-1]  # 0-based slice
                if not any(l.strip() == '' for l in between):
                    issues.append(Issue(i, 1, "SML105",
                        "missing blank line before top-level definition",
                        fixable=True))
            prev_def_line = i - 1  # store 0-based index
    return issues


@rule("SML106")
def check_opening_brace_spacing(lines: list[str], **kwargs: object) -> list[Issue]:
    """Opening brace '{' should be preceded by exactly one space."""
    issues = []
    for i, line in enumerate(lines, 1):
        stripped = _strip_strings_and_comments(line)
        for m in re.finditer(r'\S\{', stripped):
            # Allow: ::{ or ){ or similar grammar constructs? No — always space.
            issues.append(Issue(i, m.start()+1, "SML106",
                "missing space before '{'", fixable=True))
    return issues


# ─── SML2xx — Naming ──────────────────────────────────────────────────────────

_DEF_KEYWORDS = (
    'part def', 'item def', 'action def', 'port def', 'interface def',
    'attribute def', 'requirement def', 'constraint def', 'state def',
    'use case def', 'analysis def', 'package',
)

_USAGE_KEYWORDS = (
    'part ', 'item ', 'action ', 'port ', 'attribute ', 'ref ',
    'state ', 'flow ', 'connection ', 'binding ',
)

_UPPER_CAMEL = re.compile(r"^[A-Z][a-zA-Z0-9]*$|^'[^']+'$")
_LOWER_CAMEL = re.compile(r"^[a-z_][a-zA-Z0-9_]*$|^'[^']+'$")


@rule("SML201")
def check_def_naming(lines: list[str], **kwargs: object) -> list[Issue]:
    """Definition names should be UpperCamelCase."""
    issues = []
    # Match: <def keyword> <name>
    pattern = re.compile(
        r'\b(part def|item def|action def|port def|interface def|'
        r'attribute def|requirement def|constraint def|state def|'
        r'use case def|analysis def|package)\s+(\'[^\']+\'|[A-Za-z_]\w+)'
    )
    for i, line in enumerate(lines, 1):
        stripped = _strip_strings_and_comments(line)
        for m in pattern.finditer(stripped):
            name = m.group(2)
            if not _UPPER_CAMEL.match(name):
                col = m.start(2) + 1
                issues.append(Issue(i, col, "SML201",
                    f"definition name '{name}' should be UpperCamelCase"))
    return issues


@rule("SML202")
def check_usage_naming(lines: list[str], **kwargs: object) -> list[Issue]:
    """Usage (feature) names should be lowerCamelCase."""
    issues = []
    # Match usage keyword followed by name, but not 'def'
    pattern = re.compile(
        r'(?<!\w)(part|item|action|port|attribute|ref)\s+(?!def\b)(\'[^\']+\'|[a-zA-Z_]\w*)'
    )
    for i, line in enumerate(lines, 1):
        stripped = _strip_strings_and_comments(line)
        for m in pattern.finditer(stripped):
            name = m.group(2)
            # Skip 'def' keyword itself
            if name == 'def':
                continue
            if not _LOWER_CAMEL.match(name):
                col = m.start(2) + 1
                issues.append(Issue(i, col, "SML202",
                    f"usage name '{name}' should be lowerCamelCase"))
    return issues


# ─── SML3xx — Structure ───────────────────────────────────────────────────────

@rule("SML301")
def check_import_order(lines: list[str], **kwargs: object) -> list[Issue]:
    """import/alias statements should precede definitions in a namespace body."""
    issues = []
    import_pattern = re.compile(r'^\s*(import|alias)\b')
    def_pattern = re.compile(
        r'^\s*(part def|item def|action def|port def|interface def|'
        r'attribute def|requirement def|constraint def|state def|package)\b'
    )
    seen_def = False
    for i, line in enumerate(lines, 1):
        if def_pattern.match(line):
            seen_def = True
        elif import_pattern.match(line) and seen_def:
            issues.append(Issue(i, 1, "SML301",
                "import/alias should appear before definitions"))
    return issues


@rule("SML302")
def check_empty_body(lines: list[str], **kwargs: object) -> list[Issue]:
    """Empty block bodies '{ }' or '{}' can be omitted (style warning)."""
    issues = []
    empty_body = re.compile(r'\{\s*\}')
    for i, line in enumerate(lines, 1):
        if empty_body.search(_strip_strings_and_comments(line)):
            issues.append(Issue(i, 1, "SML302",
                "empty block body '{}' can be omitted"))
    return issues


@rule("SML303")
def check_file_package_match(lines: list[str], **kwargs: object) -> list[Issue]:
    """Filename stem should match the outermost package name."""
    issues: list[Issue] = []
    filename: str = kwargs.get("filename", "")
    if not filename or filename == "<string>":
        return issues
    stem = Path(filename).stem
    for i, line in enumerate(lines, 1):
        stripped = _strip_strings_and_comments(line)
        m = re.match(r"^\s*package\s+([A-Za-z_]\w*)", stripped)
        if m:
            pkg_name = m.group(1)
            if pkg_name != stem:
                issues.append(Issue(i, m.start(1) + 1, "SML303",
                    f"file name '{stem}.sysml' does not match package name '{pkg_name}'"))
            return issues
    return issues


# ─── SML4xx — Idioms ──────────────────────────────────────────────────────────

@rule("SML401")
def check_doc_comment_placement(lines: list[str], **kwargs: object) -> list[Issue]:
    """Doc comment /* */ should precede its element, not follow it."""
    issues = []
    doc_inline = re.compile(r';\s*/\*')
    for i, line in enumerate(lines, 1):
        if doc_inline.search(line):
            issues.append(Issue(i, 1, "SML401",
                "doc comment after ';' — place doc comments before the element"))
    return issues


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _strip_strings_and_comments(line: str) -> str:
    """Replace string literals and line comments with spaces (preserve positions)."""
    result = list(line)
    i = 0
    while i < len(result):
        # Line comment
        if i+1 < len(result) and result[i] == '/' and result[i+1] == '/':
            for j in range(i, len(result)):
                result[j] = ' '
            break
        # Block comment (single line only for now)
        if i+1 < len(result) and result[i] == '/' and result[i+1] == '*':
            j = i + 2
            while j+1 < len(result) and not (result[j] == '*' and result[j+1] == '/'):
                j += 1
            for k in range(i, min(j+2, len(result))):
                result[k] = ' '
            i = j + 2
            continue
        # String literal
        if result[i] == '"':
            j = i + 1
            while j < len(result) and result[j] != '"':
                if result[j] == '\\':
                    j += 1
                j += 1
            for k in range(i, min(j+1, len(result))):
                result[k] = ' '
            i = j + 1
            continue
        i += 1
    return ''.join(result)
