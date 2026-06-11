"""
sysml-style: SysML v2 textual notation style checker and formatter.

Usage:
    sysml-style check  [OPTIONS] FILE [FILE ...]
    sysml-style format [OPTIONS] FILE [FILE ...]
    sysml-style diff   [OPTIONS] FILE [FILE ...]

Options:
    --ignore CODE,CODE,...   Comma-separated rule codes to skip
    --config PATH            Path to pyproject.toml (default: auto-detect)
    --check                  (format mode) Exit nonzero if formatting would change file
    --diff                   Show unified diff instead of rewriting
    -q / --quiet             Suppress summary line
"""
from __future__ import annotations
import argparse
import difflib
import sys
from pathlib import Path


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sysml-style",
        description="SysML v2 textual notation style checker and formatter",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # ── check ──
    check_p = sub.add_parser("check", help="Lint files for style issues")
    check_p.add_argument("files", nargs="+", metavar="FILE")
    check_p.add_argument("--ignore", default="", metavar="CODES",
                         help="Comma-separated codes to ignore (e.g. SML401,SML202)")
    check_p.add_argument("--config", default=None, metavar="PATH")
    check_p.add_argument("-q", "--quiet", action="store_true")

    # ── format ──
    fmt_p = sub.add_parser("format", help="Auto-format files via sysmlpy round-trip")
    fmt_p.add_argument("files", nargs="+", metavar="FILE")
    fmt_p.add_argument("--check", action="store_true",
                       help="Exit nonzero if any file would be changed")
    fmt_p.add_argument("--diff", action="store_true",
                       help="Show unified diff instead of writing")
    fmt_p.add_argument("--config", default=None, metavar="PATH")
    fmt_p.add_argument("-q", "--quiet", action="store_true")

    return p


def cmd_check(args: argparse.Namespace) -> int:
    from .checker import check_source
    from .config import load_config

    cfg = load_config(args.config or ".")
    ignore = cfg.ignore.copy()
    if args.ignore:
        ignore.update(c.strip() for c in args.ignore.split(",") if c.strip())

    total_issues = 0
    for filepath in args.files:
        path = Path(filepath)
        if not path.exists():
            print(f"sysml-style: {filepath}: file not found", file=sys.stderr)
            continue
        source = path.read_text(encoding="utf-8")
        issues = check_source(source, ignore=ignore, filename=filepath)
        for issue in issues:
            fix_tag = " [fixable]" if issue.fixable else ""
            print(f"{filepath}:{issue.line}:{issue.col}: {issue.code} {issue.message}{fix_tag}")
        total_issues += len(issues)

    if not args.quiet:
        file_count = len(args.files)
        print(f"\n{'✓' if total_issues == 0 else '✗'} {total_issues} issue(s) in {file_count} file(s)")

    return 0 if total_issues == 0 else 1


def cmd_format(args: argparse.Namespace) -> int:
    from .formatter import format_source

    changed = 0
    errored = 0

    for filepath in args.files:
        path = Path(filepath)
        if not path.exists():
            print(f"sysml-style: {filepath}: file not found", file=sys.stderr)
            continue

        original = path.read_text(encoding="utf-8")
        formatted, warnings = format_source(original)

        for w in warnings:
            print(f"sysml-style: {filepath}: {w}", file=sys.stderr)
            if w.startswith("[format] Could not parse") or w.startswith("[format] Parse errors"):
                errored += 1
                continue

        if formatted == original:
            if not args.quiet:
                print(f"  unchanged  {filepath}")
            continue

        changed += 1

        if args.diff:
            diff = difflib.unified_diff(
                original.splitlines(keepends=True),
                formatted.splitlines(keepends=True),
                fromfile=f"a/{filepath}",
                tofile=f"b/{filepath}",
            )
            sys.stdout.writelines(diff)
        elif args.check:
            print(f"  would reformat  {filepath}")
        else:
            path.write_text(formatted, encoding="utf-8")
            if not args.quiet:
                print(f"  reformatted  {filepath}")

    if not args.quiet:
        print(f"\n{'✓' if changed == 0 else '✗'} {changed} file(s) reformatted")

    if args.check and changed > 0:
        return 1
    return 0 if errored == 0 else 2


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "check":
        return cmd_check(args)
    elif args.command == "format":
        return cmd_format(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
