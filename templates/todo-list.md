---
type: template
template_for: todo-list
output_path: 博主计划/_全局/03-本周任务.md
used_by: /todo (R8)
---

# R8 拍摄清单 ToDo 化

> **零 API**。纯模板 + Dataview。
> 自动汇总所有平台 `04-内容卡/` 里的"拍摄清单"成可勾选 ToDo。

## 触发

```
/todo                  # 今日 + 未来 3 天的所有任务
/todo --week          # 本周所有任务
/todo --platform=小红书  # 单平台任务
```

## 每日任务视图(放到 `_全局/03-本周任务.md` 顶部)

```dataview
TASK
FROM "博主计划"
WHERE !completed AND text != ""
```

## 按平台分组(更清晰)

```dataviewjs
const tasks = dv.pages('"博主计划"')
  .file.tasks
  .where(t => !t.completed);

const byPlatform = {};
for (const t of tasks) {
  const file = t.path.split("/").slice(0, -1).join("/");
  // 平台 = 父目录的第 3 层(博主计划/{region}/{platform}/...)
  const platform = t.path.split("/")[2] || "unknown";
  byPlatform[platform] = byPlatform[platform] || [];
  byPlatform[platform].push(t);
}

for (const [platform, ts] of Object.entries(byPlatform)) {
  dv.header(3, `📍 ${platform} (${ts.length} 待办)`);
  dv.taskList(ts);
}
```

## 按优先级排序

每张内容卡的 frontmatter 加 `priority` 字段(1-5,5 最高),任务视图按优先级排:

```dataview
TABLE priority, topic, date, status
FROM "博主计划"
WHERE type = "daily-content-card" AND status = "draft"
SORT priority DESC
LIMIT 20
```

## 拍摄清单自动汇总示例

每张内容卡有"拍摄清单"小节,Dataview 能拉到所有未完成项:

```dataviewjs
const allCards = dv.pages('"博主计划"')
  .where(p => p.type === "daily-content-card" && p.status === "draft");

const allTasks = [];
for (const card of allCards) {
  const file = app.vault.getAbstractFileByPath(card.file.path);
  const cache = app.metadataCache.getFileCache(file);
  const tasks = (cache?.listItems || []).filter(li => li.task);
  for (const t of tasks) {
    allTasks.push({
      card: card.file.link,
      topic: card.topic,
      platform: card.platform,
      text: t.text,
      completed: false,
    });
  }
}

dv.taskList(allTasks);
```

## 每日提醒模板(SKILL 自动生成)

```markdown
## 2026-06-17 拍摄清单

📍 小红书
- [ ] 录屏:Claude 4.5 vs 5 工具对比
- [ ] 真人出镜 3 秒开场
- [ ] 整理桌面图标(5 个被砍工具)
- [ ] 制作封面图
- [ ] 写 3 个标题候选

📍 YouTube
- [ ] 8 分钟完整版脚本撰写
- [ ] 录屏 + 录人声
- [ ] 字幕
- [ ] 缩略图 3 张

🎬 预计总时长: 2-3 小时
🎯 今天目标: 完成 1 张卡的拍摄 + 后期
```

## 任务状态机

每张内容卡有 5 个状态:

```yaml
status: draft      # 草稿,SKILL 刚生成
status: filming    # 拍摄中
status: editing    # 剪辑中
status: scheduled  # 已排期
status: published  # 已发布
```

`/todo` 默认只显示 `filming` + `editing` + `scheduled` 的任务。

## 周报自动生成(`/weekly-todo-review`)

```markdown
## 本周完成度

| 平台 | 应发布 | 实际发布 | 完成度 |
|---|---|---|---|
| 小红书 | 5 | 4 | 80% |
| YouTube | 2 | 1 | 50% |
| 总计 | 7 | 5 | 71% |

## 未完成项(下周补)

- [ ] 卡片 #003 缺封面
- [ ] 卡片 #005 还差 1 个镜头

## 建议

- 周末 1 天专攻剪辑,清空 editing 状态
- 下周小红书频次提到 6 条/周
```

## Common Pitfalls

1. **任务不收敛**:每天 10+ 待办,什么都想做 → 没一个完成。建议每天上限 5 个。
2. **任务粒度太粗**:"拍完所有内容"不是任务,应该是"录完 3 段素材"。
3. **跨平台任务混在一起**:抖音拍摄和小红书拍摄节奏不同,分开看。
4. **不勾选**:Dataview 任务勾选后会自动存档,但用户经常忘。设置 Obsidian reminder plugin 提醒。
