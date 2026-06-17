# Installation Guide

This skill works with any LLM-based agent that supports the [Agent Skills spec](https://agentskills.io). Below are installation instructions for the most popular agents.

## Prerequisites

- A modern LLM agent that can read/write files
- A place to store notes (Obsidian vault, plain folder, Notion via API, etc.)
- Optional: Python 3.8+ for the scripts (push-dispatcher, ab-test-tracker, skill-report)

## Standard installation

The standard layout is:

```
<agent-skills-folder>/
└── creator-incubator/
    ├── SKILL.md
    ├── references/
    ├── scripts/
    └── templates/
```

Most agents auto-load any folder under their `skills/` path that contains a `SKILL.md` with valid frontmatter.

## Agent-specific instructions

### Claude Code

```bash
mkdir -p ~/.claude/skills/
cp -r Million-Bloggers-Plan-SKILL ~/.claude/skills/creator-incubator
# Restart Claude Code
# Try: /onboard
```

### Cursor

```bash
mkdir -p ~/.cursor/skills/
cp -r Million-Bloggers-Plan-SKILL ~/.cursor/skills/creator-incubator
# Restart Cursor
# Try: /onboard
```

Cursor also supports per-project skills:

```bash
mkdir -p .cursor/skills/
cp -r Million-Bloggers-Plan-SKILL .cursor/skills/creator-incubator
```

### OpenCode

```bash
mkdir -p ~/.config/opencode/skills/
cp -r Million-Bloggers-Plan-SKILL ~/.config/opencode/skills/creator-incubator
# Restart OpenCode
# Try: /onboard
```

### Codex (OpenAI)

```bash
mkdir -p ~/.codex/skills/
cp -r Million-Bloggers-Plan-SKILL ~/.codex/skills/creator-incubator
# Restart Codex
# Try: /onboard
```

### Hermes Agent

```bash
# User-local
mkdir -p ~/.hermes/skills/social-media/
cp -r Million-Bloggers-Plan-SKILL ~/.hermes/skills/social-media/creator-incubator
# Or: place under a category you prefer
```

### Windsurf

```bash
mkdir -p ~/.windsurf/skills/
cp -r Million-Bloggers-Plan-SKILL ~/.windsurf/skills/creator-incubator
# Restart Windsurf
```

### Continue.dev (VS Code extension)

```bash
mkdir -p ~/.continue/skills/
cp -r Million-Bloggers-Plan-SKILL ~/.continue/skills/creator-incubator
# Reload VS Code window
```

### Cline (VS Code extension)

```bash
mkdir -p ~/Documents/Cline/skills/
cp -r Million-Bloggers-Plan-SKILL ~/Documents/Cline/skills/creator-incubator
# Reload VS Code window
```

### Aider

Aider doesn't have a `SKILL.md` convention, but you can reference this repo in your `.aider.conf.yml`:

```yaml
read:
  - creator-incubator/SKILL.md
```

Or paste the SKILL.md content into your chat as a system prompt.

### Generic Agent Skills Spec

```bash
mkdir -p ~/.agents/skills/
cp -r Million-Bloggers-Plan-SKILL ~/.agents/skills/creator-incubator
```

If your agent follows the [Agent Skills spec](https://agentskills.io), this works out of the box.

---

## Verifying the install

After installation, your agent should:

1. Recognize the trigger phrases in `SKILL.md` frontmatter (`description` field).
2. Load references/ on demand when the relevant command is invoked.
3. Be able to read/write files in the templates/ folder structure.

Quick test:

```
You: /onboard
Agent: Asks 8 questions about time, skills, platforms, etc.
You: [answer]
Agent: Writes files to your notes folder (e.g. _global/00-profile.md, _global/01-niche.md, etc.)
```

If the agent doesn't recognize `/onboard`, check:

- The `SKILL.md` frontmatter is valid (starts with `---`, ends with `\n---\n`, has `name` and `description`).
- The folder is in the agent's skills directory.
- You restarted the agent after copying.

---

## Where should the notes folder live?

The skill is folder-agnostic. Pick one:

| Tool | Best folder location |
|---|---|
| Obsidian | Inside your vault, e.g. `~/Documents/MyVault/Million-Bloggers-Plan/` |
| Plain folder | Anywhere, e.g. `~/Documents/Million-Bloggers-Plan/` |
| Notion | A top-level page in your workspace |
| Logseq | Inside your graph, e.g. `~/Documents/logseq/pages/Million-Bloggers-Plan/` |

Tell the agent where to put the files when you first run `/onboard` (or let it default to a sensible location).

---

## Optional: Python scripts

**9 standalone scripts** live in `scripts/`. All are zero-API, pure-stdlib (only `pyyaml` is optional). They can be called manually, by an LLM agent, or wired into cronjobs.

| Script | What | Example |
|---|---|---|
| `daily-content.py` | Generate today's cards | `python daily-content.py --platform=抖音` |
| `weekly-review.py` | Compute hit rate + recs | `python weekly-review.py --week=2026-W25` |
| `xplatform-roi.py` | Cross-platform ROI ranking | `python xplatform-roi.py --since 2026-06-01` |
| `inspiration-manager.py` | Inspiration pool | `python inspiration-manager.py add "AI 副业" --tags=AI,副业` |
| `failure-manager.py` | Failure log | `python failure-manager.py add 2026-06-15-002 --reason="标题党"` |
| `ab-test-tracker.py` | A/B winner eval | `python ab-test-tracker.py --platform=小红书` |
| `push-dispatcher.py` | IM push | `python push-dispatcher.py --config 04-push-config.md --test` |
| `skill-report.py` | Monthly self-check | `python skill-report.py --month=2026-06` |
| `skill-lint.py` | Validate SKILL structure | `python skill-lint.py --strict` |

Dependencies: `pyyaml` (most agents have it). Install with:

```bash
pip install pyyaml
```

All scripts support `--help` for full options and `--vault <path>` (where applicable) to override the default vault location.

---

## Updating

```bash
cd ~/.claude/skills/creator-incubator  # or wherever you installed
git pull
```

Or re-download from GitHub releases.

---

## Uninstalling

Just delete the folder:

```bash
rm -rf ~/.claude/skills/creator-incubator
```

Your notes are stored separately and won't be touched.

---

## Troubleshooting

**"Agent doesn't recognize /onboard"**
- Verify SKILL.md frontmatter (first 3 chars are `---`)
- Check the agent's skill loader is enabled
- Restart the agent

**"References are not loading"**
- Most agents lazy-load references/ on demand. Check that the agent has filesystem access to the skill folder.
- Some agents require explicit `references: [...]` declaration in the skill metadata.

**"Scripts fail with ModuleNotFoundError: yaml"**
- `pip install pyyaml` (or `uv pip install pyyaml` if you use uv)

**"Obsidian Dataview queries don't work"**
- Install the Dataview plugin in Obsidian (Community plugins)
- Dataview JS requires Dataview 1.55+

**"Push to IM doesn't work"**
- Check webhook URL in `_global/04-push-config.md`
- All channels are `enabled: false` by default — flip to `true` after configuring
- See `references/push-channels.md` for channel-specific setup

---

## Need more help?

Open an issue: https://github.com/billy192723/Million-Bloggers-Plan-SKILL/issues
