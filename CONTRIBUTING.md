# Contributing

PRs welcome. Please match the existing tone and structure.

## What we'd love help with

### New platform specs (high priority)
- Threads (Meta)
- Substack (Newsletter)
- Pinterest
- YouTube Shorts (different from YouTube long form)
- 小红书国际版 / RedNote
- 即刻 / Jike (Chinese)
- Medium
- 知乎 / Zhihu

Add a new `references/platforms/<name>.md` file matching the structure of `platform-specs.md`.

### New niche templates
- Geographic / regional niches (local food, local travel)
- Industry-vertical (legal, medical, real estate, finance)
- Hobby-specific (board games, knitting, woodworking)

Add to `references/niche-templates.md`.

### Better traffic prediction
- More calibration data points
- Per-niche benchmarks
- Per-time-of-day multipliers
- Account-age penalty curves

Edit `references/traffic-prediction-model.md`.

### More scripts
- `scripts/auto-publish.py` — push to platform API (when APIs exist)
- `scripts/data-scraper.py` — fetch real metrics from platform dashboards
- `scripts/competitor-monitor.py` — subscribe to N accounts, alert on new viral
- `scripts/cover-generator.py` — generate thumbnail variants (needs API)

### Improved frontmatter schema
- Cross-platform comparison fields
- Failure log taxonomy
- A/B test significance calculations

## Style guide

- **Tone**: friendly, direct, opinionated. Not corporate.
- **Format**: Markdown with YAML frontmatter. Tables over paragraphs.
- **Length**: keep individual files focused (one concern per file).
- **Code**: Python 3.8+, stdlib only (pyyaml is the only optional dep).
- **No emoji in code or frontmatter**. Emojis in user-facing markdown are fine.

## How to contribute

1. Fork the repo
2. Create a branch: `git checkout -b feature/new-platform-threads`
3. Make your changes
4. Validate:
   ```bash
   python -c "import yaml, re, pathlib; \
     p = pathlib.Path('SKILL.md'); \
     c = p.read_text(); \
     m = re.search(r'\n---\s*\n', c[3:]); \
     fm = yaml.safe_load(c[3:m.start()+3]); \
     assert 'name' in fm and 'description' in fm; \
     assert len(fm['description']) <= 1024; \
     assert len(c) <= 100000; \
     print('OK')"
   ```
5. Commit: `git commit -m "Add Threads platform spec"`
6. Push: `git push origin feature/new-platform-threads`
7. Open a PR

## Reporting bugs

Open an issue with:
- Agent you're using (Claude Code / Cursor / etc.)
- OS and version
- Command that failed (`/onboard`, `/daily`, etc.)
- Relevant files (card content, config, etc.)
- Expected vs actual behavior

## Roadmap discussions

For larger changes (new top-level command, schema changes, etc.), open an issue first to discuss before PR.
