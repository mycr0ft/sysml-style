from __future__ import annotations

from sysml_style.checker import check_source
from sysml_style.rules import Issue


def assert_issues(source: str, expected: list[dict], filename: str = "test.sysml") -> None:
    """Assert that check_source produces exactly the given issues."""
    issues = check_source(source, filename=filename)
    simplified = [
        {"line": i.line, "col": i.col, "code": i.code, "message": i.message}
        for i in issues
    ]
    assert simplified == expected, (
        f"Expected:\n  {expected}\nGot:\n  {simplified}"
    )


def assert_issue_count(source: str, code: str, count: int, filename: str = "test.sysml") -> None:
    """Assert that a specific rule fires exactly `count` times."""
    issues = check_source(source, filename=filename)
    matches = [i for i in issues if i.code == code]
    assert len(matches) == count, (
        f"Expected {count} issue(s) for {code}, got {len(matches)}: "
        + ", ".join(f"L{i.line}:{i.col}" for i in matches)
    )


def assert_clean(source: str, filename: str = "test.sysml") -> None:
    """Assert no issues at all."""
    issues = check_source(source, filename=filename)
    assert not issues, f"Expected no issues, got: {issues}"
