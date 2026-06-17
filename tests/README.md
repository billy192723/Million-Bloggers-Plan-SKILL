# Tests

Unit tests for the creator-incubator SKILL scripts.

## Running

```bash
# All tests
python -m unittest discover tests

# Specific file
python -m unittest tests.test_common

# Verbose
python -m unittest discover tests -v
```

No external dependencies beyond `pyyaml` (already required by the scripts).

## Test files

| File | Tests | Coverage |
|---|---|---|
| `test_common.py` | 18 | VaultPath, load_config, parse_frontmatter, format_table, safe_write, setup_logging |
| `test_daily_content.py` | 9 | find_active_platforms, find_upcoming_holidays, auto_categorize, render_card_template |
| `test_skill_lint.py` | 9 | check_skill_md, check_secrets, check_scripts |

Total: 36 unit tests.

## What's tested

### `test_common.py`
- `VaultPath`: path construction for global files, platform dirs, cards/trends/weekly dirs
- `load_config`: None / empty / nonexistent / valid YAML / invalid YAML
- `parse_frontmatter`: no frontmatter / valid / nonexistent file / invalid YAML
- `format_table`: basic / truncation / empty
- `safe_write`: new file / skip existing / overwrite
- `setup_logging`: returns logger / verbose level / idempotent

### `test_daily_content.py`
- `find_active_platforms`: no profile / frontmatter / checkbox fallback
- `find_upcoming_holidays`: results within days_ahead, no negative days
- `auto_categorize` (via failure_manager): clickbait / timing / hook / other
- `render_card_template`: minimal render produces valid output

### `test_skill_lint.py`
- `check_skill_md`: valid / missing name / invalid name / long description / missing file
- `check_secrets`: detect GitHub token / no secrets / detect OpenAI key
- `check_scripts`: missing dir / valid / syntax error

## Adding new tests

1. Create `tests/test_<module>.py`
2. Import the module: `sys.path.insert(0, "../scripts")`
3. Subclass `unittest.TestCase`
4. Run with `python -m unittest tests.test_<module>`
5. Update this README

## CI integration

Tests run automatically in `.github/workflows/ci.yml` on every push.
