"""Tests for SML2xx — naming rules."""
from __future__ import annotations

from .conftest import assert_clean, assert_issue_count


class TestSML201:
    """Definition names should be UpperCamelCase."""

    def test_correct(self):
        assert_clean("part def Engine;")

    def test_body_correct(self):
        assert_issue_count("part def Engine {}", "SML201", 0)

    def test_lowercase(self):
        assert_issue_count("part def engine;", "SML201", 1)

    def test_quoted(self):
        assert_issue_count("part def 'my part';", "SML201", 1)


class TestSML202:
    """Usage names should be lowerCamelCase."""

    def test_correct(self):
        assert_clean("part myPart : Engine;")

    def test_uppercase(self):
        assert_issue_count("part MyPart : Engine;", "SML202", 1)

    def test_skip_def(self):
        assert_clean("part def Engine;")


class TestSML203:
    """Port names should end with 'Port'."""

    def test_correct(self):
        assert_clean("port def PowerPort;\nport powerPort : PowerPort;")

    def test_def_missing_suffix(self):
        assert_issue_count("port def Fuel;", "SML203", 1)

    def test_usage_missing_suffix(self):
        assert_issue_count("port fuel : FuelPort;", "SML203", 1)


class TestSML204:
    """No spaces in element names."""

    def test_unquoted(self):
        assert_clean("part def MyPart;")

    def test_quoted_with_spaces(self):
        assert_issue_count("part def 'My Part';", "SML204", 1)

    def test_quoted_no_spaces(self):
        assert_clean("part def 'MyPart';")
