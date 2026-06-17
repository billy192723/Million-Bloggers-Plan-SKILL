# GitHub Actions workflows

CI for the Creator Incubator SKILL.

## Workflows

### `ci.yml` — Validate SKILL

Triggers on every push to `main` and every PR. Runs:

1. **SKILL.md frontmatter validation** — checks `name`, `description`, size limits per Agent Skills spec.
2. **All markdown frontmatter validation** — every `templates/*.md`, `references/*.md`, plus top-level `*.md`.
3. **Python syntax check** — `python -m py_compile` on every `scripts/*.py`.
4. **Python `--help` smoke test** — ensures every script is runnable.
5. **File size audit** — warns if any file exceeds 100 KB.
6. **Secret leak detection** — fails the build if `ghp_*`, `sk-*`, or `AKIA*` patterns are found.

Required dependencies: `pyyaml` (auto-installed in CI).

## Local equivalent

Run the same checks before pushing:

```bash
# Frontmatter + Python
for f in templates/*.md references/*.md SKILL.md; do
  python -c "
import yaml, re, pathlib
p = pathlib.Path('$f')
c = p.read_text(encoding='utf-8')
if not c.startswith('---'):
    print('skip: $f')
    continue
m = re.search(r'\n---\s*\n', c[3:])
fm = yaml.safe_load(c[3:m.start()+3])
print(f'OK: $f')
"
done

for f in scripts/*.py; do
  python -m py_compile "$f" && echo "OK: $f"
done
```

## Adding a new check

Add a step to `ci.yml`. Keep total runtime under 2 minutes.
