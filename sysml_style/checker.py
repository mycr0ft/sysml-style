"""
SysML style checker: runs lint rules over source text.
"""
from __future__ import annotations
from .rules import all_rules, Issue


DEFAULT_IGNORE: set[str] = set()


def check_source(
    source: str,
    ignore: set[str] | None = None,
    filename: str = "<string>",
) -> list[Issue]:
    """
    Run all lint rules on source text.

    Args:
        source:   SysML v2 textual source
        ignore:   set of rule codes to skip (e.g. {"SML401", "SML202"})
        filename: used in issue display only

    Returns:
        Sorted list of Issues.
    """
    ignore = ignore or DEFAULT_IGNORE
    lines = source.splitlines(keepends=True)

    issues: list[Issue] = []
    for code, rule_fn in all_rules():
        if code in ignore:
            continue
        try:
            issues.extend(rule_fn(lines, filename=filename))
        except Exception as e:
            # Don't let a buggy rule crash the whole check
            issues.append(Issue(0, 0, code, f"[rule error] {e}"))

    issues.sort(key=lambda x: (x.line, x.col, x.code))
    return issues


def check_file(
    path: str,
    ignore: set[str] | None = None,
) -> list[Issue]:
    with open(path, encoding="utf-8") as f:
        source = f.read()
    return check_source(source, ignore=ignore, filename=path)
