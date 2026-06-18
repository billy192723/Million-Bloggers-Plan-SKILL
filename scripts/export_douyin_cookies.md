# Export Douyin Cookies for fetch_douyin_stats.py

> ⚠️ **READ FIRST**: This involves giving a script access to your logged-in Douyin session. **Only do this on a trusted machine.** Cookies are sensitive — anyone with them can act as you on Douyin until they expire.

## Why this is needed

The `fetch_douyin_stats.py` script cannot log into Douyin directly (anti-bot detection). Instead, you log in manually in your browser, then export the cookies. The script injects those cookies and reads the dashboard **without ever logging in**.

## Step 1: Log into Douyin Creator Dashboard

1. Open **Chrome** (or Edge / Brave — same Chromium base)
2. Go to: https://creator.douyin.com/creator-data/home
3. Log in with QR code (recommended) or phone + SMS
4. Verify you can see your dashboard with video stats

## Step 2: Install a Cookie Export Extension

Pick ONE:

- **EditThisCookie** (Chrome) — https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg
- **Cookie-Editor** (Chrome / Firefox / Edge) — https://cookie-editor.com/
- **Get cookies.txt LOCALLY** (Chrome) — https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbeal

## Step 3: Export Cookies

1. While on the Douyin creator dashboard, click the extension icon
2. Click "Export" → "JSON"
3. Save the file as `~/.douyin_cookies.json` (or any path you choose)

The file should look like:

```json
[
  {
    "name": "sessionid",
    "value": "abc123...",
    "domain": ".douyin.com",
    "path": "/",
    "expires": 1700000000,
    "httpOnly": true,
    "secure": true,
    "sameSite": "Lax"
  },
  {
    "name": "ttwid",
    "value": "...",
    "domain": ".douyin.com",
    ...
  }
]
```

## Step 4: Verify File

```bash
# File should exist
ls -la ~/.douyin_cookies.json

# Should be valid JSON with cookies
python -c "import json; d=json.load(open('~/.douyin_cookies.json')); print(f'{len(d)} cookies loaded')"
```

## Step 5: Run the Fetcher

```bash
# Dry run first (no data extraction, just verify access)
python scripts/fetch_douyin_stats.py --dry-run

# Real run
python scripts/fetch_douyin_stats.py --output stats.json

# Or with custom cookies path
python scripts/fetch_douyin_stats.py --cookies /path/to/cookies.json
```

## Step 6: Send Output to SKILL

After running, you'll have a JSON file with your video stats. Options:

### Option A: Paste JSON
```bash
cat stats.json
```
Then paste the output into chat. I'll parse it and fill the 24h review tables.

### Option B: Auto-fill via script
```bash
# After stats.json exists
python scripts/fill_douyin_cards.py --stats stats.json
```

This will:
- Read all 7 content cards in W1-起号期
- Match videos by title
- Update the 24h review tables with actual data
- Show before/after prediction accuracy

## Security Notes

- **Cookies are sensitive.** Treat `~/.douyin_cookies.json` like a password.
- **Cookies expire.** Re-export every 7-14 days (Douyin rotates session IDs).
- **Don't commit cookies to git.** Already in `.gitignore` (see project root).
- **Use a dedicated Chrome profile** for this if you want extra isolation:
  - `chrome.exe --user-data-dir=D:\douyin-bot-profile`
  - Log in once, export cookies, use that

## Troubleshooting

| Issue | Solution |
|---|---|
| "Captcha detected" | Stop. Wait 24h. Use manual method next time. |
| "0 videos found" | Douyin UI changed. Update CSS selectors in script. |
| "Login required" redirect | Cookies expired. Re-export. |
| "Risk control" message | IP got flagged. Try different network (mobile hotspot). |
| Script crashes immediately | Playwright not installed: `pip install playwright && playwright install chromium` |
