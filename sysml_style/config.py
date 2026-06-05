"""
Config loader for sysml-style.

Reads [tool.sysml-style] from pyproject.toml if present, or accepts
inline kwargs. Falls back to sensible defaults.
"""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    max_line_length: int = 120
    indent_size: int = 4
    ignore: set[str] = field(default_factory=set)
    # "strict" | "relaxed" — relaxed allows quoted names like 'My Part'
    naming_convention: str = "strict"


def load_config(start_dir: str = ".") -> Config:
    """Walk up from start_dir looking for pyproject.toml."""
    path = _find_pyproject(start_dir)
    if path is None:
        return Config()
    try:
        return _parse_pyproject(path)
    except Exception:
        return Config()


def _find_pyproject(start: str) -> Path | None:
    current = Path(start).resolve()
    for parent in [current, *current.parents]:
        candidate = parent / "pyproject.toml"
        if candidate.exists():
            return candidate
    return None


def _parse_pyproject(path: Path) -> Config:
    # Use tomllib (Python 3.11+) or fall back to tomli
    try:
        import tomllib  # type: ignore
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore
            with open(path, "rb") as f:
                data = tomllib.load(f)
        except ImportError:
            # No TOML library available — return defaults
            return Config()

    section = data.get("tool", {}).get("sysml-style", {})
    cfg = Config()
    if "max_line_length" in section:
        cfg.max_line_length = int(section["max_line_length"])
    if "indent_size" in section:
        cfg.indent_size = int(section["indent_size"])
    if "ignore" in section:
        ignore_val = section["ignore"]
        if isinstance(ignore_val, list):
            cfg.ignore = set(ignore_val)
        elif isinstance(ignore_val, str):
            cfg.ignore = {s.strip() for s in ignore_val.split(",")}
    if "naming_convention" in section:
        cfg.naming_convention = section["naming_convention"]
    return cfg
