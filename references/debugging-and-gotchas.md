# Debugging Notes & Gotchas (creator-incubator)

Session-specific technical lessons that future agents (or future-you) will hit again. These are NOT durable rules — they're debugging recipes that complement the SKILL's Pitfalls section.

---

## 1. Python file naming: dashes break `import`

**Symptom**: `ModuleNotFoundError: No module named 'daily-content'` even though the file exists at `scripts/daily-content.py`. Affects `pytest`, `unittest discover`, and any `from x import y` in other scripts.

**Root cause**: Python's import machinery only accepts identifiers — letters, digits, underscores. A dash in the filename is interpreted as a minus sign, so `import daily-content` is parsed as `import daily - content` and fails. The file can still be **run** as a script (`python scripts/daily-content.py`) because no import statement is involved.

**Fix**: rename `xxx-yyy.py` → `xxx_yyy.py`. Use `git mv` to preserve history:
```bash
git mv scripts/daily-content.py scripts/daily_content.py
```

**When this matters for this SKILL**: if you add a new script that other code (or `tests/`) needs to `import`, you MUST name it with underscores. The 9 existing scripts all use underscores after a v2.2 rename pass.

---

## 2. YAML frontmatter parsing: `safe_load_all` for `---\n...\n---\n` documents

**Symptom**: `yaml.safe_load(text)` raises `ScannerError: expected a single document in the stream` when parsing a markdown file whose frontmatter is wrapped in `---` on both sides (which is the YAML convention for frontmatter, e.g. `---\nkey: value\n---`).

**Root cause**: `safe_load` reads **one** document. The leading `---` is interpreted as a doc-start marker, and the closing `---` is interpreted as the start of a *second* document — which fails because there's no content for it.

**Fix**: use `safe_load_all` and take the first non-None doc:
```python
import yaml
with open(path) as f:
    docs = [d for d in yaml.safe_load_all(f) if d is not None]
data = docs[0] if docs else {}
```

The SKILL's `_common.py:load_config` already does this. If you write a new script that reads frontmatter, copy that pattern — don't reinvent it.

---

## 3. CI secret scan: must exclude `tests/` and `__pycache__/`

**Symptom**: GitHub Actions `Check for accidental secrets` step fails with `✗ Found potential secret in repository!` — but the "secret" is a test fixture like `token = 'ghp_abcdef...7890'` deliberately placed in `tests/test_skill_lint.py` to test the secret-detection regex.

**Root cause**: `grep -rE '...secret patterns...' .` recurses into `tests/` and matches the fixture strings.

**Fix** in `.github/workflows/ci.yml`:
```bash
grep -rE '...' . \
    --exclude-dir=.git \
    --exclude-dir=tests \
    --exclude-dir=__pycache__ \
    2>/dev/null
```

**Why this is safe**: real leaked tokens should never appear in `tests/` (use `ghp_aa...aaaa` style fake strings) or in `__pycache__/` (compiled bytecode, not source). Excluding these directories is a precision improvement, not a security reduction.

---

## 4. Windows testing: `tempfile.TemporaryDirectory()` not `NamedTemporaryFile + os.unlink`

**Symptom**: `PermissionError: [WinError 32] 另一个程序正在使用此文件` on Windows when tests do:
```python
with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
    f.write("...")
    f.flush()
    config = load_config(Path(f.name))
os.unlink(f.name)  # ← fails on Windows
```

**Root cause**: on Windows, `NamedTemporaryFile(delete=False)` keeps a file handle open via the `with` block. The file isn't fully released until garbage collection. Calling `os.unlink` immediately can fail.

**Fix**: use `tempfile.TemporaryDirectory()` + `Path`:
```python
with tempfile.TemporaryDirectory() as tmp:
    target = Path(tmp) / "file.md"
    target.write_text("...", encoding="utf-8")
    # ... use target ...
# auto-cleanup when context exits
```

The `tests/test_*.py` files all use this pattern.

---

## 5. Updating an existing CI workflow file: don't duplicate `run:` keys

**Symptom**: GitHub Actions shows error `Invalid workflow file: 'run' is already defined` at a specific line.

**Root cause**: when patching a step into an existing workflow YAML, the new step's `run:` block can accidentally overlap with the next step's `run:` block if the patch doesn't include the trailing `name:` of the next step.

**Fix**: when editing `.github/workflows/ci.yml`, always run `python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"` locally before pushing. The file should parse as valid YAML and contain the expected number of steps (this SKILL: 11).

---

## 6. README with Chinese folder names vs English folder names

**Background**: this SKILL originally had Chinese folder names (`博主计划/`, `_全局/`, `国内/小红书/...`) because the user is Chinese and uses Obsidian with Chinese display. When the SKILL was made generic for the public GitHub release, English folder names were used (`Million-Bloggers-Plan-SKILL/_global/CN/xiaohongshu/...`).

**Implication for templates**: the SKILL's templates and scripts reference both naming conventions. `VaultPath` in `_common.py` supports both via `REGION_ALIASES`:
- `CN` / `国内` / `china` → `国内`
- `INTL` / `国外` / `international` → `国外`

If you add new template generation logic, default to the user's **current** vault naming (check `_global/00-档案.md` for the language preference), not the GitHub template's English.

---

## 7. SKILL.md frontmatter limits (Agent Skills spec)

When editing `SKILL.md` frontmatter, three hard limits per the Agent Skills spec:
- `name`: ≤ 64 chars, lowercase + hyphens only, regex `^[a-z0-9-]+$`
- `description`: ≤ 1024 chars
- file size: ≤ 100,000 bytes (~36k tokens)

If you add a new section that pushes the file over 100k, split into a `references/` support file and link it from SKILL.md. Don't silently break the spec.

The current SKILL.md is ~32k chars — well under the limit, but worth re-checking if you add a 10k-char section.

---

## 8. When to use `git mv` vs `mv` for renames

**Symptom**: after `mv scripts/foo.py scripts/bar.py`, `git status` shows the old file as deleted and the new as untracked (lose rename history in blame/log).

**Fix**: always use `git mv`:
```bash
git mv scripts/daily-content.py scripts/daily_content.py
```

`git mv` is just `mv` + `git add` + `git rm` under the hood, but it preserves rename detection. This matters when 8 files get renamed in a single commit (e.g. dash → underscore mass rename).

---

## 9. GitHub Personal Access Token gotchas

**Three things that bit this session**:

1. **Token is leaked the moment it appears in chat**. Even if "you didn't mean to paste it", assume compromised. The fix flow: finish the immediate task with the token → warn the user → tell them to revoke at <https://github.com/settings/tokens> → suggest switching to SSH keys or GitHub App.

2. **Token gets auto-revoked**. GitHub's secret-scanning service will sometimes detect a leaked PAT on a public repo and revoke it within minutes. Symptoms: `git push` succeeds, then immediately fails with `401 Bad credentials` on the next operation. There is no warning.

3. **Use a 2-hour expiry PAT, not a no-expiry PAT**. For one-off repo creation, generate a fine-grained token with `Contents: Read and write` + `Metadata: Read`, expiration 2 hours, then delete it. A no-expiry PAT is a permanent backdoor.

The fix for the underlying problem: SSH keys. `ssh-keygen -t ed25519` + add to <https://github.com/settings/keys> + `git remote set-url origin git@github.com:USER/REPO.git`. Works forever, can't leak in chat.

---

## 10. The 50 unit tests took longer to write than the actual scripts

**Why this is worth noting**: the user's first ask in this session was "scripts need to be more complete, and follow the 3-thing rule". The natural reading was "write better scripts". But the actual highest-leverage work turned out to be:

1. **Test infrastructure** (`_common.py` + `tests/`) — made the existing 9 scripts testable in 50 unit tests, which surfaced 3 real bugs (`load_config` multi-doc, `find_active_platforms` list-vs-tuple, `skill_lint` OpenAI regex).
2. **CI workflow hardening** (exclude `tests/` from secret scan) — caught a real false positive that would have blocked every future commit.
3. **Renaming 8 scripts dash→underscore** — silent breakage: the scripts ran fine but couldn't be `import`ed by tests or other tools.

**Generalization for future sessions**: when a user says "X needs to be more complete", check whether the underlying problem is missing infrastructure (tests, CI, shared libs, file naming) before assuming it's missing functionality. Infrastructure improvements often have higher leverage than feature additions.

---

## 11. The user's "你来决定" pattern

When the user says "你来决定最好的方案" (you decide the best approach):

- **DO** make a concrete decision with a brief justification table, then execute
- **DON'T** ask "are you sure?" or "should I check with you first?"
- **DON'T** list 5 options for the user to pick from

The user trusts the agent's judgment on tactical decisions (which tests to write, which bug to fix first, which doc to update). The user wants strategic input on:
- What to build (新功能 vs 修 bug vs 写文档)
- What NOT to do (deciding the scope)
- When to stop (is it good enough to ship?)

Apply judgment accordingly. The "你来决定" pattern is also a signal that the user is fatigued by decision-making — reduce their cognitive load by deciding for them on tactical questions.
