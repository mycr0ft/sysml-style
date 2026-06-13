"""CLI integration tests."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent


def test_help():
    result = subprocess.run(
        [sys.executable, "-m", "sysml_style", "--help"],
        capture_output=True, text=True, cwd=PROJECT,
    )
    assert result.returncode == 0
    assert "usage:" in result.stdout
    assert "sysml-style" in result.stdout


def test_check_clean_file(tmp_path):
    f = tmp_path / "clean.sysml"
    f.write_text("package Clean;\n")
    result = subprocess.run(
        [sys.executable, "-m", "sysml_style", "check", str(f)],
        capture_output=True, text=True, cwd=PROJECT,
    )
    assert result.returncode == 0


def test_check_with_issues(tmp_path):
    f = tmp_path / "test.sysml"
    f.write_text("part def engine;\n")
    result = subprocess.run(
        [sys.executable, "-m", "sysml_style", "check", str(f)],
        capture_output=True, text=True, cwd=PROJECT,
    )
    assert result.returncode == 1
    assert "SML201" in result.stdout


def test_check_missing_file(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "sysml_style", "check",
         str(tmp_path / "nope.sysml")],
        capture_output=True, text=True, cwd=PROJECT,
    )
    assert "file not found" in result.stderr


def test_check_with_ignore(tmp_path):
    f = tmp_path / "test.sysml"
    f.write_text("part def engine;\n")
    result = subprocess.run(
        [sys.executable, "-m", "sysml_style", "check",
         "--ignore", "SML201", str(f)],
        capture_output=True, text=True, cwd=PROJECT,
    )
    assert result.returncode == 0


def test_format_clean(tmp_path):
    f = tmp_path / "test.sysml"
    f.write_text("package P;\n")
    result = subprocess.run(
        [sys.executable, "-m", "sysml_style", "format", str(f)],
        capture_output=True, text=True, cwd=PROJECT,
    )
    assert result.returncode == 0


def test_format_check(tmp_path):
    f = tmp_path / "test.sysml"
    f.write_text("package P;\n")
    result = subprocess.run(
        [sys.executable, "-m", "sysml_style", "format",
         "--check", str(f)],
        capture_output=True, text=True, cwd=PROJECT,
    )
    assert result.returncode == 0


def test_format_diff(tmp_path):
    f = tmp_path / "test.sysml"
    f.write_text("package P;\n")
    result = subprocess.run(
        [sys.executable, "-m", "sysml_style", "format",
         "--diff", str(f)],
        capture_output=True, text=True, cwd=PROJECT,
    )
    assert result.returncode == 0


def test_format_bad_syntax(tmp_path):
    f = tmp_path / "test.sysml"
    f.write_text("this is not valid sysml $\n")
    result = subprocess.run(
        [sys.executable, "-m", "sysml_style", "format", str(f)],
        capture_output=True, text=True, cwd=PROJECT,
    )
    assert result.returncode == 2


def test_format_deep_nesting_no_data_loss(tmp_path):
    f = tmp_path / "deep.sysml"
    source = """\
package DeepNesting;

part def Vehicle {
    attribute mass : Real;
    part def Engine {
        attribute power : Real;
        part def Cylinder {
            attribute bore : Real;
            attribute def BoreSpec {
                attribute tolerance : Real;
            }
        }
    }
}
"""
    f.write_text(source)
    result = subprocess.run(
        [sys.executable, "-m", "sysml_style", "format", str(f)],
        capture_output=True, text=True, cwd=PROJECT,
    )
    assert result.returncode == 0, f"format failed: {result.stderr}"
    formatted = f.read_text()
    for token in ["Vehicle", "Engine", "Cylinder", "BoreSpec", "tolerance"]:
        assert token in formatted, f"Missing '{token}' in formatted output"
    assert formatted.count("part def") >= 3
    assert formatted.count("attribute def") >= 1


def test_format_redef_no_double_space(tmp_path):
    f = tmp_path / "RedefTest.sysml"
    source = """\
package RedefTest;

attribute def BaseAttr;

part def MyPart {
    attribute :>> BaseAttr;
}
"""
    f.write_text(source)
    result = subprocess.run(
        [sys.executable, "-m", "sysml_style", "format", str(f)],
        capture_output=True, text=True, cwd=PROJECT,
    )
    assert result.returncode == 0, f"format failed: {result.stderr}"
    formatted = f.read_text()
    assert "  :>>" not in formatted, "Formatter produced double space before :>>"
    result = subprocess.run(
        [sys.executable, "-m", "sysml_style", "check", str(f)],
        capture_output=True, text=True, cwd=PROJECT,
    )
    assert result.returncode == 0, f"checker found issues after format:\n{result.stdout}"
