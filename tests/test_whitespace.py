"""Tests for SML1xx — whitespace rules."""
from __future__ import annotations

from .conftest import assert_clean, assert_issue_count


class TestSML101:
    """Spaces around '=' operator."""

    def test_correct(self):
        assert_clean("attribute mass = 100;")

    def test_missing_before(self):
        assert_issue_count('attribute mass= 100;', "SML101", 1)

    def test_missing_after(self):
        assert_issue_count('attribute mass =100;', "SML101", 1)

    def test_missing_both(self):
        assert_issue_count('attribute mass=100;', "SML101", 1)

    def test_skip_comparison(self):
        assert_clean("if x == 5 then y;")

    def test_skip_assignment(self):
        assert_clean("attribute x := 5;")

    def test_redef_correct(self):
        assert_clean("attribute :>> BaseAttr;")

    def test_redef_missing_before(self):
        assert_issue_count("attribute:>> BaseAttr;", "SML101", 1)

    def test_redef_missing_after(self):
        assert_issue_count("attribute :>>BaseAttr;", "SML101", 1)


class TestSML102:
    """No space before ';'."""

    def test_correct(self):
        assert_clean("part def Engine;")

    def test_space_before(self):
        assert_issue_count("part def Engine ;", "SML102", 1)

    def test_multiple(self):
        assert_issue_count("a = 1 ; b = 2 ;", "SML102", 2)

    def test_string_before_semicolon(self):
        assert_clean('attribute x = "hello";')


class TestSML103:
    """No trailing whitespace."""

    def test_clean(self):
        assert_clean("part def Engine;\n")

    def test_trailing_space(self):
        assert_issue_count("part def Engine; \n", "SML103", 1)

    def test_trailing_tab(self):
        assert_issue_count("part def Engine;\t\n", "SML103", 1)


class TestSML104:
    """Indentation multiple of detected unit."""

    def test_4_space_indent(self):
        assert_clean("    part def Engine;")

    def test_3_space_indent(self):
        assert_clean("   part def Engine;")

    def test_bad_indent(self):
        assert_issue_count(
            "    part def Engine;\n  part def Other;", "SML104", 1,
        )

    def test_continuation_line_skipped(self):
        # Continuation lines are not checked for indent when the previous
        # line doesn't end with ; or }
        assert_clean("    connect\n      a to b;")


class TestSML105:
    """Blank line between top-level definitions."""

    def test_correct(self):
        assert_clean("part def A;\n\npart def B;")

    def test_missing_blank(self):
        assert_issue_count("part def A;\npart def B;", "SML105", 1)


class TestSML106:
    """Space before '{'."""

    def test_correct(self):
        assert_clean("part def Engine {")

    def test_missing(self):
        assert_issue_count("part def Engine{", "SML106", 1)
