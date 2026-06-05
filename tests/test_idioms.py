"""Tests for SML4xx — idioms."""
from __future__ import annotations

from .conftest import assert_clean, assert_issue_count


class TestSML401:
    """Doc comment before element, not after ';'."""

    def test_correct(self):
        assert_issue_count("/* comment */\npart def Engine;", "SML401", 0)

    def test_after_semicolon(self):
        assert_issue_count("part def Engine; /* comment */", "SML401", 1)


class TestSML402:
    """Use 'doc' keyword for documentation comments."""

    def test_with_doc(self):
        assert_clean("doc /* documented */")

    def test_without_doc(self):
        assert_issue_count("/* undocumented */", "SML402", 1)

    def test_inline_comment_untouched(self):
        assert_clean("part def Engine;  // inline note")
