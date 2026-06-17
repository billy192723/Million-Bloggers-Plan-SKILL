# Push Channels Configuration

> **NOT IN USE** — by user's choice, `/push` is **manual-trigger only**, no cron auto-push. The function exists; the user activates it when they wire up webhooks.
> 4 channels supported. Each can be enabled/disabled independently.

## Channel 1: 钉钉 (DingTalk)

**Difficulty**: ⭐ (easiest)
**Personal use**: ✅ Yes

### Setup (5 minutes)

1. Open the DingTalk group where you want to receive pushes
2. Group Settings → 智能群助手 → 添加机器人 → Custom (自定义)
3. Security: choose "加签" (recommended) or "自定义关键词"
4. Copy the **webhook URL** (e.g. `https://oapi.dingtalk.com/robot/send?access_token=XXX`)
5. If signed, copy the **secret** too

### Config in `_全局/04-推送配置.md`

```yaml
dingtalk:
  enabled: true
  webhook: "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN"
  secret: ""  # optional, if using 加签
  at_mobiles: []  # phones to @mention, e.g. ["13800138000"]
```

### API Reference

- Endpoint: webhook URL (POST)
- Body format: `{"msgtype": "markdown", "markdown": {"title": "...", "text": "..."}}`
- Sign algo: `https://oapi.dingtalk.com/robot/send?access_token=X&timestamp=TS&sign=SIGN`
- Limits: 20 msg/min per group

## Channel 2: 飞书 (Feishu / Lark)

**Difficulty**: ⭐⭐
**Personal use**: ⚠️ Need Feishu enterprise account (or apply for free developer account)

### Setup (15 minutes)

1. Go to [Feishu Open Platform](https://open.feishu.cn/) → Console
2. Create Enterprise Self-built App (企业自建应用)
3. Permissions: enable `im:message` and `im:message.group_at_msg`
4. Add the app to your target group
5. Get the app's `app_id` and `app_secret`
6. Use Bot Webhook OR use tenant_access_token + chat_id

### Config

```yaml
feishu:
  enabled: true
  webhook: "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_HOOK_TOKEN"  # simpler option
  # OR for app-based:
  # app_id: "cli_XXX"
  # app_secret: "XXX"
  # chat_id: "oc_XXX"
```

### API Reference

- Webhook option: POST JSON `{"msg_type": "interactive", "card": {...}}` (rich card)
- App option: `POST /open-apis/im/v1/messages` with `receive_id_type=chat_id`
- Limits: 5 msg/sec per chat

## Channel 3: 企业微信 (WeCom)

**Difficulty**: ⭐⭐
**Personal use**: ⚠️ Need WeCom enterprise account (free to register)

### Setup (10 minutes)

1. WeCom admin console → 群机器人 → 添加
2. Get the **webhook URL** (e.g. `https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=XXX`)
3. Optional: enable @mention with user IDs

### Config

```yaml
wecom:
  enabled: true
  webhook: "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
  mentioned_user_ids: []  # e.g. ["UserID1"]
```

### API Reference

- Endpoint: webhook URL (POST)
- Body: `{"msgtype": "markdown", "markdown": {"content": "..."}}`
- Limits: 20 msg/min per group

## Channel 4: 微信个人 (via 3rd-party)

**Difficulty**: ⭐⭐⭐
**Personal use**: ✅ Yes (via 3rd-party)

Two options:

### Option A: Server酱 (recommended, simple)

1. Go to [sct.ftqq.com](https://sct.ftqq.com/) → login with GitHub
2. Get your **SendKey**
3. WeChat scan to bind (订阅服务号)

```yaml
serverchan:
  enabled: true
  sendkey: "SCT_YOUR_KEY"
```

API: `GET https://sctapi.ftqq.com/SCT_YOUR_KEY.send?title=X&desp=Y`

### Option B: WxPusher

1. Go to [wxpusher.zjiecode.com](https://wxpusher.zjiecode.com/) → register
2. Create app → get `appToken` and your `uid`

```yaml
wxpusher:
  enabled: true
  app_token: "AT_XXX"
  uid: "UID_XXX"
```

API: `POST https://wxpusher.zjiecode.com/api/send/message`

## Common Pitfalls

1. **Webhook URL leak = spam risk.** Treat the URL like a password. Don't commit to git. Don't paste in public chat.
2. **Test mode first.** All 4 channels support sending to a test group before going live.
3. **Rate limits are real.** Don't blast. Default 1 push/day is well under all limits.
4. **Signature expiry.** DingTalk 加签 timestamps expire in 3 hours. Cache the signature, refresh if older.
5. **Markdown rendering differs.** WeCom has limited markdown (no images in some modes). Feishu uses its own card format, not standard markdown.
6. **Privacy in group chats.** Don't push personal content (like 实际播放数) to a group with non-team members.

## Verification

After configuring, test with:

```
User: /push test
Skill: [sends a test card to all enabled channels]
User: [confirms receipt on phone]
```

If a channel fails:
- Check webhook URL is correct
- Check signature/secret (DingTalk 加签)
- Check group hasn't blocked the bot
- Check rate limit (wait 1 min)
