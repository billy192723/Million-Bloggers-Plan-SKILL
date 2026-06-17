"""
_common.py - Shared utilities for all creator-incubator scripts.

Provides:
  - setup_logging()    - consistent logger across all scripts
  - handle_errors()    - decorator for friendly error messages
  - load_config()      - safe YAML config loading
  - VaultPath          - typed path helper for the user's notes folder
  - format_table()     - pretty table output
"""

import logging
import os
import sys
import traceback
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# ---- Logger setup ----

def setup_logging(verbose: bool = False, log_file: Optional[Path] = None) -> logging.Logger:
    """
    Configure a consistent logger across all scripts.
    Returns a logger named after the calling script.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logger = logging.getLogger("creator-incubator")
    logger.setLevel(level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console = logging.StreamHandler(sys.stderr)
    console.setLevel(level)
    console.setFormatter(formatter)
    logger.addHandler(console)

    # Optional file handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# ---- Error handling decorator ----

def handle_errors(func: Callable) -> Callable:
    """
    Decorator that catches exceptions and prints user-friendly messages.
    Logs full traceback to debug log.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger("creator-incubator")
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            logger.warning("Interrupted by user (Ctrl+C)")
            return 130  # Standard SIGINT exit code
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            logger.info("Hint: Check the file path. Use --vault to override the default vault location.")
            return 2
        except PermissionError as e:
            logger.error(f"Permission denied: {e}")
            logger.info("Hint: Check file permissions or run with appropriate privileges.")
            return 3
        except yaml.YAMLError as e:
            logger.error(f"YAML parse error: {e}")
            logger.info("Hint: Check the .md file for unquoted colons or invalid YAML.")
            return 4
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(traceback.format_exc())
            else:
                logger.info("Run with --verbose for full traceback.")
            return 1
    return wrapper


# ---- Config loader ----

DEFAULT_VAULT = Path(os.environ.get("CREATOR_INCUBATOR_VAULT", "E:/知识库/博主计划"))


def load_config(path: Optional[Path], logger: Optional[logging.Logger] = None) -> dict:
    """
    Safely load a YAML config file. Returns empty dict if not found or invalid.
    Handles both single-doc and multi-doc YAML (returns the first non-empty doc).
    """
    if not path:
        return {}
    if not str(path) or str(path) == ".":
        return {}
    if not path.exists():
        if logger:
            logger.debug(f"Config not found: {path}")
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            # Use safe_load_all to handle both single-doc and multi-doc YAML
            # Returns list; pick the first non-empty one
            docs = [d for d in yaml.safe_load_all(f) if d is not None]
            if not docs:
                return {}
            data = docs[0]
            return data if isinstance(data, dict) else {}
    except yaml.YAMLError as e:
        if logger:
            logger.error(f"Invalid YAML in {path}: {e}")
        return {}


# ---- Vault path helper ----

class VaultPath:
    """
    Type-safe path helper for the user's vault structure.

    Usage:
        v = VaultPath("E:/知识库/博主计划")
        v.global_file("06-inspiration.md")  # → E:/.../博主计划/_global/06-inspiration.md
        v.platform_dir("CN", "xiaohongshu") # → E:/.../博主计划/CN/xiaohongshu
    """

    CN = "国内"
    INTL = "国外"

    PLATFORMS_CN = ["小红书", "抖音", "B站", "视频号", "公众号"]
    PLATFORMS_INTL = ["YouTube", "TikTok", "Instagram", "X"]

    REGION_ALIASES = {
        "国内": "国内", "CN": "国内", "cn": "国内", "china": "国内",
        "国外": "国外", "INTL": "国外", "intl": "国外", "international": "国外",
    }

    def __init__(self, root: Path):
        self.root = Path(root)

    @property
    def exists(self) -> bool:
        return self.root.exists()

    def _normalize_region(self, region: str) -> str:
        """Accept CN/INTL/中文/英文, return 国内/国外."""
        return self.REGION_ALIASES.get(region, region)

    def global_file(self, name: str) -> Path:
        return self.root / "_global" / name

    def platform_dir(self, region: str, platform: str) -> Path:
        return self.root / self._normalize_region(region) / platform

    def cards_dir(self, region: str, platform: str, week_tag: str = "") -> Path:
        d = self.platform_dir(region, platform) / "04-内容卡"
        if week_tag:
            d = d / week_tag
        return d

    def trends_dir(self, region: str, platform: str) -> Path:
        return self.platform_dir(region, platform) / "03-热点日志"

    def weekly_dir(self, region: str, platform: str) -> Path:
        return self.platform_dir(region, platform) / "05-周复盘"

    def cross_platform_compare(self) -> Path:
        return self.global_file("05-跨平台对比.md")

    def failures(self) -> Path:
        return self.global_file("07-failures.md")

    def inspirations(self) -> Path:
        return self.global_file("06-inspiration.md")

    def profile(self) -> Path:
        return self.global_file("00-profile.md")

    def platform_profile(self, region: str, platform: str) -> Path:
        return self.platform_dir(region, platform) / "00-平台档案.md"

    def platform_dashboard(self, region: str, platform: str) -> Path:
        return self.platform_dir(region, platform) / "06-数据看板.md"

    def __repr__(self) -> str:
        return f"VaultPath({self.root!r})"


# ---- Pretty table formatter ----

def format_table(headers: list, rows: list, max_col_width: int = 40) -> str:
    """
    Pretty-print a markdown-style table with column widths capped.
    """
    # Cap column widths
    cap = lambda s: (s[:max_col_width-1] + "…") if len(s) > max_col_width else s
    headers = [cap(str(h)) for h in headers]
    rows = [[cap(str(c)) for c in row] for row in rows]

    # Compute column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    # Format
    def fmt_row(row):
        return "| " + " | ".join(cell.ljust(w) for cell, w in zip(row, col_widths)) + " |"

    sep = "|" + "|".join("-" * (w + 2) for w in col_widths) + "|"
    lines = [fmt_row(headers), sep]
    lines.extend(fmt_row(row) for row in rows)
    return "\n".join(lines)


# ---- Common CLI helpers ----

def positive_int(value: str) -> int:
    """argparse type for positive integers."""
    try:
        n = int(value)
        if n < 1:
            raise ValueError
        return n
    except (ValueError, TypeError):
        raise argparse_error(f"expected positive integer, got {value!r}")


def argparse_error(msg: str):
    """Helper to raise argparse errors with consistent format."""
    import argparse
    raise argparse.ArgumentTypeError(msg)


import argparse  # Late import to avoid circular


# ---- Frontmatter parser (used by multiple scripts) ----

def parse_frontmatter(path: Path) -> dict:
    """
    Parse YAML frontmatter from a markdown file.
    Returns {} if no frontmatter or invalid YAML.
    """
    if not path or not Path(path).exists():
        return {}
    try:
        text = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {}
    import re
    m = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", text, re.DOTALL)
    if not m:
        return {}
    try:
        meta = yaml.safe_load(m.group(1)) or {}
        return meta if isinstance(meta, dict) else {}
    except yaml.YAMLError:
        return {}


# ---- Convenience: write file safely ----

def safe_write(path: Path, content: str, logger: Optional[logging.Logger] = None, overwrite: bool = False) -> bool:
    """
    Write content to path, creating parent dirs.
    Returns True if written, False if file exists and overwrite=False.
    """
    path = Path(path)
    if path.exists() and not overwrite:
        if logger:
            logger.warning(f"File exists, skipping: {path}")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if logger:
        logger.info(f"Wrote {path}")
    return True
