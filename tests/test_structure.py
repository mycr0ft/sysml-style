"""Tests for SML3xx — structure rules."""
from __future__ import annotations

from .conftest import assert_clean, assert_issue_count


class TestSML301:
    """Import/alias before definitions."""

    def test_correct(self):
        assert_clean("public import SI::*;\npart def Engine;")

    def test_import_after_def(self):
        assert_issue_count("part def Engine;\nimport SI::*;", "SML301", 1)


class TestSML302:
    """Empty block body can be omitted."""

    def test_with_body(self):
        assert_clean("part def Engine;\nattribute mass = 100;")

    def test_empty_body(self):
        assert_issue_count("part def Engine {}", "SML302", 1)

    def test_empty_with_space(self):
        assert_issue_count("part def Engine { }", "SML302", 1)


class TestSML303:
    """Filename matches package name."""

    def test_matching(self):
        assert_clean("package RadarSystem;", filename="RadarSystem.sysml")

    def test_not_matching(self):
        assert_issue_count(
            "package FooSystem;", "SML303", 1, filename="RadarSystem.sysml",
        )

    def test_matching_quoted(self):
        assert_issue_count(
            "package 'Radar System';", "SML303", 0, filename="radar_system.sysml",
        )

    def test_matching_short_name(self):
        assert_issue_count(
            "package <UAVSBA> 'UAV System Base Architecture';",
            "SML303", 0, filename="uavsba.sysml",
        )

    def test_no_filename(self):
        assert_clean("package Foo;", filename="<string>")


class TestSML304:
    """No unnamed usages."""

    def test_named_usage(self):
        assert_clean("part battery : Battery;")

    def test_unnamed(self):
        assert_issue_count("part : Battery;", "SML304", 1)

    def test_unnamed_attribute(self):
        assert_issue_count("attribute : Mass;", "SML304", 1)

    def test_skip_def(self):
        assert_clean("part def Engine;")


class TestSML305:
    """Import must have visibility parameter."""

    def test_public_import(self):
        assert_clean("public import SI::*;")

    def test_private_import(self):
        assert_clean("private import SI::*;")

    def test_protected_import(self):
        assert_clean("protected import SI::*;")

    def test_bare_import(self):
        assert_issue_count("import SI::*;", "SML305", 1)

    def test_bare_import_after_def(self):
        assert_issue_count("part def Engine;\nimport SI::*;", "SML305", 1)

    def test_indented_bare_import(self):
        assert_issue_count("    import SI::*;", "SML305", 1)

    def test_public_import_all(self):
        assert_clean("public import all SI::*;")

    def test_bare_import_all(self):
        assert_issue_count("import all SI::*;", "SML305", 1)

    def test_import_in_string_untouched(self):
        assert_clean("doc /* use import to load */")
