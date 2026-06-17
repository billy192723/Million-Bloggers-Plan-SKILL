---
type: template
template_for: content-calendar
output_path: 博主计划/_全局/03-内容日历.md
used_by: /calendar (R1)
---

# R1 内容日历模板

> **零 API 依赖**。纯 Dataview + 模板。
> 跨平台聚合 `04-内容卡/`,生成月历视图。

## 设计

用 Obsidian Dataview JS 动态渲染月历。用户打开 `03-内容日历.md` 即可看到本月所有平台的发布安排。

## Dataview JS 月历(粘贴到 Obsidian 即可)

```dataviewjs
// 拉所有内容卡(从各平台 04-内容卡/)
const cards = dv.pages('"博主计划"')
  .where(p => p.type === "daily-content-card" && p.status !== "cancelled");

// 按日期分组
const byDate = {};
for (const c of cards) {
  if (!c.date) continue;
  const d = c.date.toFormat("yyyy-MM-dd");
  byDate[d] = byDate[d] || [];
  byDate[d].push(c);
}

// 当前月
const today = dv.date("today");
const monthStart = today.startOf("month");
const daysInMonth = today.daysInMonth;

// 构建月历表
const table = [];
const headers = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];
table.push(headers);

let week = new Array(7).fill("");
let dayCursor = monthStart;
for (let i = 0; i < daysInMonth; i++) {
  const dow = dayCursor.weekday - 1;  // 0-6
  const dateKey = dayCursor.toFormat("yyyy-MM-dd");
  const items = byDate[dateKey] || [];
  if (items.length > 0) {
    const cell = items.map(c => {
      const p = (c.platform || "?").slice(0, 4);
      return `[${p}](${c.file.path})`;
    }).join(" ");
    week[dow] = `${dateKey.slice(5)}\n${cell}`;
  } else {
    week[dow] = dateKey.slice(5);
  }
  if (dow === 6 || i === daysInMonth - 1) {
    table.push(week);
    week = new Array(7).fill("");
  }
  dayCursor = dayCursor.plus({ days: 1 });
}

dv.table(headers, table.slice(1).map(row => row.map(cell => cell || " ")));
```

## 表头说明

| 字段 | 类型 | 来源 |
|---|---|---|
| `date` | date | 内容卡 frontmatter |
| `platform` | string | 内容卡 frontmatter |
| `topic` | string | 内容卡 frontmatter |
| `status` | string | draft / published / cancelled |
| `predicted_views` | string | 预测流量 |
| `actual_views` | number | 发布后回填 |

## 平台颜色(可选,需 Dataview CSS)

```css
/* 03-内容日历.md 的 frontmatter 区域加入 */
.dataview td a[href*="小红书"] { color: #ff2442; }
.dataview td a[href*="抖音"] { color: #000; }
.dataview td a[href*="B站"] { color: #fb7299; }
.dataview td a[href*="视频号"] { color: #07c160; }
.dataview td a[href*="YouTube"] { color: #ff0000; }
.dataview td a[href*="TikTok"] { color: #000; }
.dataview td a[href*="Instagram"] { color: #e1306c; }
.dataview td a[href*="X"] { color: #0077b5; }
```

## 月度汇总(自动算)

```dataview
TABLE WITHOUT ID
  platform as "平台",
  length(rows) as "发布数",
  sum(实际播放) as "总播放",
  mean(实际互动率) as "平均互动率"
FROM "博主计划"
WHERE type = "daily-content-card" AND status = "published"
  AND date.month = (date(today).month)
GROUP BY platform
```

## `/calendar` 命令

用户说 `/calendar`,SKILL:
1. 检查 `03-内容日历.md` 是否存在,不存在则用本模板创建
2. 输出当月概况(待办发布数 / 已发布数 / 命中率)
3. 列出"今天该拍什么" — 从最近 7 天的 `04-内容卡/` 挑 `status=draft` 的卡

## Common Pitfalls

1. **Dataview 不渲染**:确认已装 Dataview 插件;如果用 Dataview JS,需要装 Dataview 1.55+。
2. **跨平台路径不同**:Dataview 的 `FROM` 子句要写 `"博主计划"`(全根目录)而不是具体子目录,因为卡在 `国内/小红书/04-内容卡/` 和 `国外/YouTube/04-内容卡/` 不同位置。
3. **空月**:第 1 周或最后 1 周可能全空,正常,显示空白。
4. **重复卡**:同 idea 在多平台发多张卡,会显示多次。如果只要看 1 个,加 `GROUP BY topic`。
