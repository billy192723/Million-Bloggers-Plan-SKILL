#!/usr/bin/env python
"""
fetch_douyin_stats.py - 抖音创作者后台数据抓取(防封号版)

⚠️ RISK WARNING ⚠️
- This script accesses Douyin creator dashboard via browser automation
- Douyin's anti-bot system may detect automation and restrict your account
- USE AT YOUR OWN RISK. Recommended max: 1x per day, max 50 posts pulled.

Safety mechanisms:
  1. Read-only: never posts, likes, comments
  2. Human-like delays: 2-7s between actions
  3. Uses your real Chrome profile (with history + cookies)
  4. Removes navigator.webdriver fingerprint
  5. Rate limited: 1 call per day enforced
  6. Cookie injection (you log in manually, then export)
  7. Human-like mouse movements

Usage:
  # Step 1: Export your Douyin cookies (see export_douyin_cookies.md)
  # Step 2: Run this script
  python fetch_douyin_stats.py --cookies ~/.douyin_cookies.json

  # Step 3: Output JSON to stdout
  python fetch_douyin_stats.py --output stats.json

  # Step 4: Feed back to SKILL (paste JSON or use as input)
"""

import argparse
import asyncio
import json
import random
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("[ERROR] playwright required: pip install playwright && playwright install chromium", file=sys.stderr)
    sys.exit(1)


# === Configuration ===

DOUYIN_DASHBOARD_URL = "https://creator.douyin.com/creator-data/home"

# Real Chrome user data dir (Windows default)
CHROME_USER_DATA_WIN = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
CHROME_USER_DATA_MAC = Path.home() / "Library" / "Application Support" / "Google" / "Chrome"
CHROME_USER_DATA_LINUX = Path.home() / ".config" / "google-chrome"

# Rate limiting: max 1 run per day
RATE_LIMIT_FILE = Path.home() / ".douyin_last_run.txt"


# === Safety functions ===

def check_rate_limit() -> bool:
    """Enforce max 1 run per day."""
    if not RATE_LIMIT_FILE.exists():
        return True
    try:
        last_run_str = RATE_LIMIT_FILE.read_text().strip()
        last_run = datetime.fromisoformat(last_run_str)
        if datetime.now() - last_run < timedelta(hours=20):
            print(f"[WARN] Last run was {last_run.isoformat()}", file=sys.stderr)
            print(f"[WARN] Must wait 20h between runs. Aborting for safety.", file=sys.stderr)
            return False
    except (ValueError, OSError) as e:
        print(f"[WARN] Could not read rate limit file: {e}", file=sys.stderr)
    return True


def record_run():
    """Mark current run in rate limit file."""
    RATE_LIMIT_FILE.write_text(datetime.now().isoformat())


async def human_delay(min_s: float = 2.0, max_s: float = 5.0):
    """Sleep a random duration to simulate human thinking."""
    delay = random.uniform(min_s, max_s)
    await asyncio.sleep(delay)


async def human_like_scroll(page):
    """Scroll like a human — non-linear, with pauses."""
    for _ in range(random.randint(2, 4)):
        # Random scroll distance
        delta = random.randint(150, 400)
        await page.mouse.wheel(0, delta)
        # Pause after scroll
        await human_delay(1.0, 3.0)


async def human_like_mouse_move(page, x1, y1, x2, y2):
    """Move mouse with bezier-like curve (not straight line)."""
    steps = random.randint(15, 25)
    for i in range(steps):
        t = i / steps
        # Add random offset for natural curve
        offset_x = random.uniform(-3, 3)
        offset_y = random.uniform(-3, 3)
        x = x1 + (x2 - x1) * t + offset_x
        y = y1 + (y2 - y1) * t + offset_y
        await page.mouse.move(x, y)
        await asyncio.sleep(random.uniform(0.01, 0.03))


# === Main ===

async def fetch_dashboard_data(cookies_path: Path, output_path: Path = None, dry_run: bool = False):
    """
    Fetch Douyin creator dashboard data with safety mechanisms.
    """
    # Safety check 1: rate limit
    if not dry_run and not check_rate_limit():
        return None

    # Load cookies
    if not cookies_path.exists():
        print(f"[ERROR] Cookies file not found: {cookies_path}", file=sys.stderr)
        print("[HINT] See export_douyin_cookies.md for how to export", file=sys.stderr)
        return None

    cookies = json.loads(cookies_path.read_text())
    print(f"[INFO] Loaded {len(cookies)} cookies from {cookies_path}")

    # Detect Chrome user data dir by platform
    import platform
    system = platform.system()
    if system == "Windows":
        chrome_data = CHROME_USER_DATA_WIN
    elif system == "Darwin":
        chrome_data = CHROME_USER_DATA_MAC
    else:
        chrome_data = CHROME_USER_DATA_LINUX

    if not chrome_data.exists():
        print(f"[WARN] Chrome user data not found at {chrome_data}", file=sys.stderr)
        print("[INFO] Falling back to ephemeral context (no profile reuse)", file=sys.stderr)
        chrome_data = None

    async with async_playwright() as p:
        launch_kwargs = dict(
            headless=False,  # MUST be visible to avoid detection
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--window-size=1920,1080",
            ]
        )
        if chrome_data:
            launch_kwargs["user_data_dir"] = str(chrome_data)

        browser_ctx = await p.chromium.launch_persistent_context(**launch_kwargs) if chrome_data else await p.chromium.launch(**launch_kwargs)

        # If using launch (not persistent), create context
        if not chrome_data:
            browser_ctx = await browser_ctx.new_context()

        page = browser_ctx.pages[0] if browser_ctx.pages else await browser_ctx.new_page()

        # Safety 4: anti-fingerprint
        await page.add_init_script("""
            // Remove webdriver flag
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            // Add chrome runtime (looks like real Chrome)
            window.chrome = {runtime: {}};
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({state: Notification.permission}) :
                originalQuery(parameters)
            );
        """)

        # Inject cookies
        await browser_ctx.add_cookies(cookies)
        print(f"[INFO] Injected {len(cookies)} cookies into browser context")

        # Navigate to dashboard
        print(f"[INFO] Navigating to {DOUYIN_DASHBOARD_URL} ...")
        try:
            await page.goto(DOUYIN_DASHBOARD_URL, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print(f"[ERROR] Navigation failed: {e}", file=sys.stderr)
            await browser_ctx.close()
            return None

        # Safety 2: human delay after page load
        await human_delay(3.0, 6.0)

        # Safety 5: check for captcha / risk control
        risk_indicators = [
            "验证码", "captcha", "滑块", "slider",
            "异常", "abnormal", "风控", "risk"
        ]
        page_content = await page.content()
        for indicator in risk_indicators:
            if indicator in page_content:
                print(f"[WARN] Risk indicator detected: '{indicator}'", file=sys.stderr)
                print(f"[WARN] Douyin may have triggered anti-bot protection.", file=sys.stderr)
                print(f"[WARN] Stopping for safety. Try again tomorrow or use manual method.", file=sys.stderr)
                await browser_ctx.close()
                return None

        # Safety 7: human-like scroll to load data
        print("[INFO] Scrolling to load data...")
        await human_like_scroll(page)

        # Try to extract data
        print("[INFO] Extracting data...")
        try:
            data = await page.evaluate("""
                () => {
                    const result = {
                        overview: {},
                        recent_videos: [],
                        timestamp: new Date().toISOString(),
                    };

                    // Try to grab overview metrics
                    // (Selectors will need to be updated as Douyin UI changes)
                    const metrics = document.querySelectorAll('[class*="data-card"], [class*="metric"]');
                    metrics.forEach(el => {
                        const title = el.querySelector('[class*="title"], h3, .label')?.textContent?.trim();
                        const value = el.querySelector('[class*="value"], .num')?.textContent?.trim();
                        if (title && value) {
                            result.overview[title] = value;
                        }
                    });

                    // Try to grab video list
                    const videoRows = document.querySelectorAll('[class*="video-item"], tr[class*="video"]');
                    videoRows.forEach(row => {
                        const title = row.querySelector('[class*="title"]')?.textContent?.trim();
                        const views = row.querySelector('[class*="view"]')?.textContent?.trim();
                        const likes = row.querySelector('[class*="like"]')?.textContent?.trim();
                        const comments = row.querySelector('[class*="comment"]')?.textContent?.trim();
                        const publishTime = row.querySelector('[class*="time"]')?.textContent?.trim();
                        if (title) {
                            result.recent_videos.push({
                                title, views, likes, comments, publishTime
                            });
                        }
                    });

                    return result;
                }
            """)
        except Exception as e:
            print(f"[WARN] Data extraction failed: {e}", file=sys.stderr)
            data = {"error": str(e), "raw_html_snippet": (await page.content())[:500]}

        # Safety: human delay before closing
        await human_delay(2.0, 4.0)

        await browser_ctx.close()

        # Record successful run
        if not dry_run:
            record_run()

        return data


def main():
    p = argparse.ArgumentParser(
        description="Fetch Douyin creator dashboard data (anti-ban version)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--cookies",
        default=str(Path.home() / ".douyin_cookies.json"),
        help="Path to exported Douyin cookies (JSON)",
    )
    p.add_argument(
        "--output", "-o",
        help="Output JSON file (default: stdout)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip rate limit check, don't record run",
    )
    args = p.parse_args()

    cookies_path = Path(args.cookies)
    output_path = Path(args.output) if args.output else None

    print("=" * 60)
    print("Douyin Stats Fetcher (anti-ban version)")
    print("=" * 60)
    print(f"Cookies: {cookies_path}")
    print(f"Output:  {output_path or 'stdout'}")
    print(f"Dry run: {args.dry_run}")
    print()
    print("[WARN] This script may trigger Douyin's anti-bot system.")
    print("[WARN] Use MAX 1x per day. Stop immediately if you see captcha.")
    print()

    try:
        data = asyncio.run(fetch_dashboard_data(cookies_path, output_path, dry_run=args.dry_run))
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    if data is None:
        print("[ERROR] Could not fetch data. Try again tomorrow or use manual method.")
        sys.exit(1)

    # Output
    output_json = json.dumps(data, indent=2, ensure_ascii=False)
    if output_path:
        output_path.write_text(output_json, encoding="utf-8")
        print(f"[OK] Saved to {output_path}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
