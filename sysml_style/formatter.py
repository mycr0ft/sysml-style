"""
SML formatter: round-trip via sysmlpy + post-process fixups.

Uses sysmlpy's own unparser for structural normalization, then applies
additional text-level fixes for things the unparser doesn't canonicalize.
"""
from __future__ import annotations
import re


def format_source(source: str) -> tuple[str, list[str]]:
    """
    Format SysML v2 source text.

    Returns:
        (formatted_text, list_of_warning_strings)
        If parse fails, returns (original_source, [error_message]).
    """
    from sysmlpy import parse

    model, errors = parse(source)
    if model is None or errors:
        msg = "; ".join(str(e) for e in errors) if errors else "parse failed"
        return source, [f"[format] Could not parse: {msg}"]

    try:
        formatted = str(model)
    except Exception as e:
        return source, [f"[format] Unparser error: {e}"]

    # Post-process: fix things the unparser leaves imperfect
    formatted = _fix_equals_spacing(formatted)
    formatted = _fix_semicolon_space(formatted)
    formatted = _fix_blank_lines_between_defs(formatted)
    formatted = _ensure_final_newline(formatted)

    return formatted, []


def _fix_equals_spacing(text: str) -> str:
    """Normalize 'foo= bar' and 'foo =bar' to 'foo = bar'."""
    # Match = not preceded/followed by space, excluding ==, :=, >=, <=, =>
    # The unparser produces 'attribute mass= 100' — fix the = side
    lines = []
    for line in text.splitlines():
        # Fix: word= value  →  word = value  (space missing before =)
        line = re.sub(r'(\w)=(?!=)(?= |\d|\w)', r'\1 =', line)
        # Fix: word = value or word =value — ensure space after =
        line = re.sub(r'(?<=[^=!<>])=(?!=)(?=[^ \n])', r'= ', line)
        lines.append(line)
    return '\n'.join(lines)


def _fix_semicolon_space(text: str) -> str:
    """Remove space before ';' — the unparser leaves 'Engine ;' on empty defs."""
    lines = []
    for line in text.splitlines():
        line = re.sub(r'\s+;', ';', line)
        lines.append(line)
    return '\n'.join(lines)


def _fix_blank_lines_between_defs(text: str) -> str:
    """Ensure blank line between top-level definitions."""
    top_def = re.compile(
        r'^(package|part def|item def|action def|port def|interface def|'
        r'attribute def|requirement def|constraint def|state def|'
        r'use case def|analysis def)\b'
    )
    lines = text.splitlines()
    out = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if top_def.match(stripped) and out and out[-1].strip() != '':
            out.append('')
        out.append(line)
    return '\n'.join(out)


def _ensure_final_newline(text: str) -> str:
    return text if text.endswith('\n') else text + '\n'
