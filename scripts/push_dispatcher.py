#!/usr/bin/env python
"""
Push dispatcher for creator-incubator SKILL.

Reads the latest un-pushed content card and pushes a SUMMARY to all enabled
channels configured in _全局/04-推送配置.md.

Modes:
  --test           Send a test message to all enabled channels
  --card PATH      Push a specific card file (default: latest un-pushed)
  --dry-run        Render the message but don't send
  --config PATH    Override config file path

Manual trigger only (per user choice 4B). No cron.
"""

import argparse
import json
import os
import re
import sys
import time
import hmac
import hashlib
import base64
import urllib.parse
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

try:
    import urllib.request
    import urllib.error
except ImportError:
    print("[ERROR] urllib not available", file=sys.stderr)
    sys.exit(1)


# ---------- Config loading ----------

def load_config(config_path: Path) -> dict:
    """Read config from _全局/04-推送配置.md, parse YAML frontmatter."""
    if not config_path or str(config_path) in ("", "."):
        return {"channels": {}}
    if not config_path.exists():
        return {"channels": {}}
    content = config_path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return {"channels": {}}
    try:
        return yaml.safe_load(m.group(1)) or {"channels": {}}
    except yaml.YAMLError as e:
        print(f"[ERROR] Config YAML parse failed: {e}", file=sys.stderr)
        return {"channels": {}}


# ---------- Card loading ----------

def load_card(card_path: Path) -> dict:
    """Read content card, return parsed frontmatter + rendered summary."""
    if not card_path.exists():
        return {}
    content = card_path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return {"_raw": content}
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {"_raw": content}
    meta["_raw"] = content
    return meta


def render_summary(card: dict, obsidian_base_url: str = "") -> str:
    """Render a short, IM-friendly summary from a card's frontmatter."""
    topic = card.get("topic", "Untitled")
    niche = card.get("niche", "")
    platforms = card.get("platforms", [])
    if isinstance(platforms, list):
        platforms = " / ".join(platforms)
    pv = card.get("predicted_views", "-")
    pe = card.get("predicted_engagement_rate", "-")
    pc = card.get("prediction_confidence", "-")
    basis = card.get("prediction_basis", "")

    lines = [
        f"📌 **{topic}**",
        f"🏷 {niche}" if niche else "",
        f"📍 {platforms}" if platforms else "",
        f"📊 预测流量: {pv} | 互动率: {pe} | 置信度: {pc}",
        f"💡 依据: {basis[:120]}" if basis else "",
    ]
    return "\n".join(l for l in lines if l)


def render_markdown(card: dict, link_to_obsidian: str = "") -> str:
    """Render markdown for DingTalk/WeCom-style channels."""
    topic = card.get("topic", "Untitled")
    niche = card.get("niche", "")
    platforms = card.get("platforms", [])
    if isinstance(platforms, list):
        platforms = " / ".join(platforms)
    pv = card.get("predicted_views", "-")
    pe = card.get("predicted_engagement_rate", "-")
    basis = card.get("prediction_basis", "")

    md = f"""# 🪄 博主孵化器 · 今日内容卡

**{topic}**

> 🏷 {niche}
> 📍 平台: {platforms}
> 📊 预测: 流量 {pv} · 互动率 {pe}

"""
    if basis:
        md += f"> 💡 预测依据: {basis[:200]}\n\n"
    if link_to_obsidian:
        md += f"🔗 [在 Obsidian 中查看完整卡片]({link_to_obsidian})\n"
    return md


# ---------- Channel senders ----------

def http_post_json(url: str, payload: dict, timeout: int = 10) -> tuple:
    """POST JSON, return (ok, body)."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return True, resp.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)


def http_get(url: str, timeout: int = 10) -> tuple:
    """GET, return (ok, body)."""
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return True, resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return False, str(e)


# ---- DingTalk ----

def dingtalk_sign(secret: str) -> str:
    """Generate DingTalk 加签 signature."""
    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode("utf-8")
    string_to_sign = f"{timestamp}\n{secret}".encode("utf-8")
    hmac_code = hmac.new(secret_enc, string_to_sign, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return timestamp, sign


def send_dingtalk(cfg: dict, message: str, title: str) -> tuple:
    if not cfg.get("enabled"):
        return False, "disabled"
    webhook = cfg.get("webhook", "").strip()
    if not webhook:
        return False, "no webhook"
    secret = cfg.get("secret", "").strip()
    url = webhook
    if secret:
        ts, sign = dingtalk_sign(secret)
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}timestamp={ts}&sign={sign}"
    payload = {
        "msgtype": "markdown",
        "markdown": {"title": title[:64], "text": message},
    }
    if cfg.get("at_mobiles"):
        payload["at"] = {"atMobiles": cfg["at_mobiles"], "isAtAll": False}
    return http_post_json(url, payload)


# ---- Feishu ----

def send_feishu(cfg: dict, message: str, title: str) -> tuple:
    if not cfg.get("enabled"):
        return False, "disabled"
    webhook = cfg.get("webhook", "").strip()
    if not webhook:
        return False, "no webhook"
    payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": title[:60]},
                "template": "blue",
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": message[:4000]},
                }
            ],
        },
    }
    return http_post_json(webhook, payload)


# ---- WeCom ----

def send_wecom(cfg: dict, message: str, title: str) -> tuple:
    if not cfg.get("enabled"):
        return False, "disabled"
    webhook = cfg.get("webhook", "").strip()
    if not webhook:
        return False, "no webhook"
    payload = {
        "msgtype": "markdown",
        "markdown": {"content": f"## {title}\n\n{message}"},
    }
    if cfg.get("mentioned_user_ids"):
        payload["mentioned_list"] = cfg["mentioned_user_ids"]
    return http_post_json(webhook, payload)


# ---- Server酱 ----

def send_serverchan(cfg: dict, message: str, title: str) -> tuple:
    if not cfg.get("enabled"):
        return False, "disabled"
    sendkey = cfg.get("sendkey", "").strip()
    if not sendkey:
        return False, "no sendkey"
    # Server酱: GET /sctapi.ftqq.com/{key}.send?title=X&desp=Y
    url = f"https://sctapi.ftqq.com/{sendkey}.send"
    url += "?" + urllib.parse.urlencode({"title": title[:60], "desp": message[:3000]})
    return http_get(url)


# ---- WxPusher ----

def send_wxpusher(cfg: dict, message: str, title: str) -> tuple:
    if not cfg.get("enabled"):
        return False, "disabled"
    app_token = cfg.get("app_token", "").strip()
    uid = cfg.get("uid", "").strip()
    if not app_token or not uid:
        return False, "missing app_token or uid"
    payload = {
        "appToken": app_token,
        "content": message[:4000],
        "summary": title[:60],
        "contentType": 1,  # 1=markdown, 2=html
        "uids": [uid],
    }
    return http_post_json("https://wxpusher.zjiecode.com/api/send/message", payload)


CHANNEL_SENDERS = {
    "dingtalk": ("钉钉", send_dingtalk),
    "feishu": ("飞书", send_feishu),
    "wecom": ("企业微信", send_wecom),
    "serverchan": ("微信(Server酱)", send_serverchan),
    "wxpusher": ("微信(WxPusher)", send_wxpusher),
}


# ---------- Main ----------

def dispatch(args) -> int:
    config_path = Path(args.config) if args.config else None
    if not config_path:
        # Default: find _全局/04-推送配置.md relative to Obsidian vault
        # Caller is expected to provide --config; otherwise fall back to env
        config_path = Path(os.environ.get("CREATOR_INCUBATOR_CONFIG", ""))

    # In dry-run mode, config is optional (preview only).
    if (not config_path or not config_path.exists()) and not args.dry_run:
        print(f"[ERROR] Config not found: {config_path or '(not set)'}", file=sys.stderr)
        print("Hint: pass --config <path> or set CREATOR_INCUBATOR_CONFIG", file=sys.stderr)
        return 2

    if not args.dry_run:
        config = load_config(config_path)
    else:
        config = {"channels": {}}
    channels = config.get("channels", {})

    # In dry-run or test mode, skip card existence check
    if not (args.dry_run or args.test):
        card_path = Path(args.card) if args.card else None
        if not card_path or not card_path.exists():
            print(f"[ERROR] Card not found: {card_path or '(not specified)'}", file=sys.stderr)
            return 2
        card = load_card(card_path)
        title = f"🪄 博主孵化器 · {card.get('topic', '内容卡')}"
        link = card_path.as_uri() if hasattr(card_path, "as_uri") else str(card_path)
        message = render_markdown(card, link_to_obsidian=link)
    elif args.test:
        title = "🪄 creator-incubator 测试推送"
        message = "如果你看到这条消息,说明推送通道已就位。✅\n\n由 `creator-incubator` skill 触发。"
    else:
        # dry-run: use a sample card or template
        if args.card:
            card_path = Path(args.card)
            if card_path.exists():
                card = load_card(card_path)
            else:
                card = {"topic": "示例 · Claude 4.5 工具对比", "niche": "AI 工具评测",
                        "platforms": ["小红书", "B站", "YouTube"],
                        "predicted_views": "5000-15000", "predicted_engagement_rate": "3.5-6.0%",
                        "prediction_confidence": "low",
                        "prediction_basis": "新号基线 + Claude 4.5 热点 ×3.0"}
            title = f"🪄 博主孵化器 · {card.get('topic', '内容卡')}"
            link = card_path.as_uri() if hasattr(card_path, "as_uri") else str(card_path)
            message = render_markdown(card, link_to_obsidian=link)
        else:
            title = "🪄 creator-incubator DRY RUN"
            message = "这是一条 dry-run 预览。\n\n实际推送时会从 `04-内容卡/` 读最新的内容卡。"

    if args.dry_run:
        print("=== DRY RUN — would send ===")
        print(f"Title: {title}")
        print("---")
        print(message)
        print("=== END ===")
        return 0

    # Dispatch
    enabled_count = 0
    success_count = 0
    for key, (label, sender) in CHANNEL_SENDERS.items():
        cfg = channels.get(key, {})
        if not cfg.get("enabled"):
            continue
        enabled_count += 1
        ok, body = sender(cfg, message, title)
        status = "✅" if ok else "❌"
        print(f"  {status} {label}: {body[:200]}")
        if ok:
            success_count += 1

    if enabled_count == 0:
        print("[WARN] No channels enabled in config.")
        return 1
    print(f"\n[OK] {success_count}/{enabled_count} channels sent.")
    return 0 if success_count > 0 else 3


def main():
    p = argparse.ArgumentParser(description="creator-incubator push dispatcher")
    p.add_argument("--config", help="Path to 04-推送配置.md")
    p.add_argument("--card", help="Path to content card to push")
    p.add_argument("--test", action="store_true", help="Send a test message")
    p.add_argument("--dry-run", action="store_true", help="Render but don't send")
    args = p.parse_args()
    sys.exit(dispatch(args))


if __name__ == "__main__":
    main()
