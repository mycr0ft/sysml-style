# sysml-style

SysML v2 textual notation style checker and formatter. Lints and auto-formats `.sysml` files using configurable rules.

## Installation

```bash
pip install sysmlpy        # required dependency
pip install tomli           # optional — only needed on Python < 3.11 for pyproject.toml config
```

Then run from the project root:

```bash
python -m sysml_style --help
```

Or install the package in editable mode:

```bash
pip install -e .
sysml-style --help
```

## Usage

```
sysml-style check  [OPTIONS] FILE [FILE ...]
sysml-style format [OPTIONS] FILE [FILE ...]
```

### check — Lint files for style issues

```bash
sysml-style check uav.sysml
sysml-style check --ignore SML401,SML202 uav.sysml
sysml-style check --quiet uav.sysml
```

Issues are printed as:

```
file.sysml:3:5: SML101 expected spaces around '=' operator [fixable]
```

Exit code: `0` if no issues, `1` if issues found.

### format — Auto-format files

```bash
sysml-style format uav.sysml        # rewrites in-place
sysml-style format --check uav.sysml  # exit 1 if would change (for CI)
sysml-style format --diff uav.sysml   # show unified diff, don't write
sysml-style format --quiet uav.sysml
```

Exit code: `0` if no changes, `1` if `--check` would reformat, `2` on parse errors.

## Config

Create a `[tool.sysml-style]` section in your `pyproject.toml`:

```toml
[tool.sysml-style]
max_line_length = 120
indent_size = 4
ignore = ["SML401", "SML202"]
naming_convention = "strict"   # or "relaxed"
```

sysml-style walks up from the target file to find `pyproject.toml`. Use `--config PATH` to point to a specific file. Without a config file, sensible defaults are used.

## Rules

### SML1xx — Whitespace

| Code | Rule | Fixable |
|------|------|---------|
| SML101 | Spaces around `=` operator | yes |
| SML102 | No space before `;` | yes |
| SML103 | No trailing whitespace | yes |
| SML104 | Indentation is a multiple of the detected unit (2/3/4 spaces) | no |
| SML105 | Blank line between top-level definitions | yes |
| SML106 | Space before `{` | yes |

### SML2xx — Naming

| Code | Rule | Fixable |
|------|------|---------|
| SML201 | Definition names should be UpperCamelCase | no |
| SML202 | Usage (feature) names should be lowerCamelCase | no |

In `relaxed` naming mode, single-quoted names like `'My Part'` are allowed without case enforcement.

### SML3xx — Structure

| Code | Rule | Fixable |
|------|------|---------|
| SML301 | `import`/`alias` before definitions | no |
| SML302 | Empty block body `{}` can be omitted | no |

### SML4xx — Idioms

| Code | Rule | Fixable |
|------|------|---------|
| SML401 | Doc comment before element, not after `;` | no |
