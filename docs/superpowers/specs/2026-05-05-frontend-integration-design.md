# Frontend Integration Design — UI + Motion Tracks

> Date: 2026-05-05
> Scope: design new screens for Phase 2 backend (RAG Tutor, async upload, assignments, progress, agents)
> Deliverable: parallel design tracks + ready-to-use prompts for design tools (Figma/Midjourney/v0)

---

## Part 0 — Design DNA (现有视觉语言基线)

读了 `tokens.css` + `base.css` + Dashboard/AppShell + AITutorPanel 后总结的当前风格：

**一句话**：学院派 × 极简包豪斯 × Klein 蓝点睛 × 大量负空间 × GSAP 视差。

| 维度 | 当前规范 |
|------|----------|
| 名字 | NeuroAI Studio Design Tokens v4.0 (Academic Light) |
| 主色 | Klein Blue `#0022ff`（点睛色，不是主体色）|
| 中性色 | 真黑 `#000` / 多级灰 `#333/#666/#999` / 真白 `#fff` |
| 表面 | 三层灰白 `#fff / #f8f9fa / #f1f3f5` |
| 字体 | Inter (Display + Body) + Noto Sans SC + JetBrains Mono |
| 字阶 | 12 / 13 / 14 / 16 / 18 / 20 / 24 / 32 / 48 / 72 / 96 px |
| **圆角** | **0px**（除头像/胶囊全圆） — brutalist 立场 |
| 间距 | 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96 / 128 |
| 缓动 | `cubic-bezier(0.16, 1, 0.3, 1)` 出场 expo |
| 时长 | 150 / 300 / 500ms |
| 焦点 | Klein 蓝外描边 2px + 3px offset，**不带圆角** |
| 选中 | Klein 蓝底白字 |

**七个反复出现的视觉招式**：
1. **小字大数字** — `kicker`（uppercase mono 11px 灰）配 4xl-6xl 数字
2. **不对称网格** — 左侧大字标题 + 右侧编号节点
3. **真黑细线** — 1px `#000` 切分关键区域，不用阴影
4. **GSAP 视差** — 鼠标驱动 brain-image / 几何元素 浅深双层 parallax
5. **Three.js HeroScene** — 首页用 three 渲染脑神经几何
6. **章节编号节点** — 大号数字（48-96px）作为视觉锚点
7. **Mono kicker 标签** — 几乎每个 section 标题都先来一个 uppercase mono 小标

**前端栈**：Vue 3 + Vite + GSAP + D3 + Three.js + @vueuse/core + Pinia。
**未引入的库**（不用加）：tailwind / framer-motion / shadcn — 走全自研 CSS。

---

## Part 1 — 缺什么页面（基于 Phase 2 后端）

| 后端能力 | 需要的前端页面 | 优先级 |
|----------|----------------|--------|
| `/api/tutor/ask?stream=1` 流式 | **TutorPanel 升级版**：流式打字 + tool 调用过程可视化 + 引用面板 | 🔥 P0 |
| `/api/materials/upload?async=1` 异步 | **Material Upload Studio**：拖放 + 进度阶段 + 提取预览 | 🔥 P0 |
| `/api/agents/<name>/stream` agent | **Agent Console**：和 tutor 共用，但有 tool_call/tool_result 可视化 | P0 |
| `/api/assignments/*` 作业 | **Teacher Assignments Console**（老师布置/批改）+ **Student Assignment Inbox**（学生提交） | P1 |
| `/api/progress/*` 进度 | **Student Progress Dashboard**（个人）+ **Cohort Heatmap**（班级） | P1 |
| `/api/jobs/<id>` 任务状态 | **Job Toast/Strip**：全局右下角任务流 | P1 |
| `/api/users` 身份 | **Identity Switcher**：顶栏右上角学生/老师切换（MVP 不做登录）| P2 |

---

## Part 2 — UI 设计轨道（视觉/布局）

每个新屏幕给两套：① 文字描述 ② 设计稿 prompt（可直接喂给 Figma AI / v0.dev / Midjourney）

### 2.1 TutorPanel v2 — 流式对话 + Tool 可视化

**布局**（两栏，参考章节工作台的不对称语言）：

```
┌────────────────────────────────────────────────────────────────┐
│  AI TUTOR · 智能学习助手                                        │
│  ─────────────────────────────────────                          │
│  就本章内容提问                                                  │
│                                                                 │
│  ┌──────────────────────────┐  ┌─────────────────────────────┐ │
│  │ 对话流（左 65%）          │  │ 引用 + 工具栏（右 35%）       │ │
│  │                          │  │                             │ │
│  │ [01] 学生：什么是注意力机制? │  │ TOOL CALLS                   │ │
│  │                          │  │ ─ search_materials          │ │
│  │ [02] AI：(打字中...)      │  │ ─ search_concept_graph      │ │
│  │   注意力机制是...          │  │                             │ │
│  │   ▌                      │  │ CITATIONS                   │ │
│  │                          │  │ [01] Ch.3 - Attention       │ │
│  │                          │  │ [02] 概念图: Self-Attention  │ │
│  │ ─────────────────        │  │                             │ │
│  │ [输入框 - 占满底部]       │  │                             │ │
│  └──────────────────────────┘  └─────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

**核心视觉规则**：
- 消息无气泡、无圆角、用 1px 黑细线分隔（接现有 brutalist）
- 学生消息：`mono kicker` 编号 [01] + 黑色正文
- AI 消息：Klein 蓝 kicker AI · 时间戳 + 黑色正文 + 实时光标 `▌`
- Tool calls 用 mono 字体折叠展开（默认收起，hover 展开 JSON）
- Citation 卡片用真黑 1px 边 + 编号大写 [01]，hover 时 Klein 蓝下划线

**设计稿 Prompt（喂给 v0.dev 或 Figma AI）**：
```
Design a chat interface for an AI tutor in a Chinese university course platform.
Style: brutalist academic, sharp corners (0px radius), heavy use of negative space,
Inter typography, JetBrains Mono for labels and metadata.
Color palette: white background (#ffffff), black text (#000000),
Klein blue accent (#0022ff) used sparingly, multi-tier grays (#333/#666/#999).

Layout: two columns at 65/35 split.
Left column: conversation thread.
- Each message starts with a mono uppercase numbered label like [01] 学生 or [01] AI · 11:42
- No message bubbles. Messages are separated by hairline horizontal rules (1px solid black).
- Student messages have black labels.
- AI messages have a Klein blue square (8px) before the label.
- During streaming, show a blinking 2px wide block cursor (▌) at the end of incomplete text.

Right column: tool call inspector + citation panel.
- "TOOL CALLS" section with mono uppercase header.
- Each tool call is a collapsed strip: ─ search_materials({query: "..."}). Hover expands to show JSON.
- "CITATIONS" section below.
- Each citation is a 1px solid black bordered card, with a numbered uppercase label [01],
  source title in 14px black, snippet in 13px gray (#666), hover adds Klein blue 2px underline on the title.

Bottom: a 56px height input bar spanning the full width, 1px solid black top border.
- No rounded corners on the textarea.
- Submit button is a 48px tall pill (border-radius: 999px) with Klein blue background, white text "提问".
- Disabled state: 50% opacity.

Negative space: at least 32px padding around all sections, 24px between messages.
Display the empty state with a Klein blue dashed border (1px dashed #0022ff) saying:
"询问关于本章的任何问题 — Tutor 会引用课程材料和知识图谱回答。"
```

---

### 2.2 Material Upload Studio — 拖放 + 异步进度

**布局**（三段式垂直流，配合后端 4 阶段进度：保存 → 提取 → 嵌入 → LLM 提取）：

```
┌────────────────────────────────────────────────────────────────┐
│  MATERIALS · 上传与解析                                          │
│  ──────────────                                                 │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐│
│  │   [拖放区 - 200px 高，Klein 蓝 1px dashed border]            ││
│  │                                                            ││
│  │              拖放文件至此 / 点击选择                         ││
│  │              支持 PDF / TXT / MD                            ││
│  └────────────────────────────────────────────────────────────┘│
│                                                                 │
│  PROCESSING QUEUE                                               │
│  ──────                                                         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 01  neural-networks.pdf                                  │  │
│  │     ●●●●○                40%   嵌入向量中                  │  │
│  │     ─────────────────────────                             │  │
│  │     SAVE → EXTRACT → EMBED ← LLM EXTRACT                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 02  attention-mechanisms.pdf                             │  │
│  │     ●●●●●               100%   完成 · 12 chunks · 8 概念   │  │
│  │     ─────────────────────────                             │  │
│  │     SAVE · EXTRACT · EMBED · LLM EXTRACT                 │  │
│  │     [查看提取结果] →                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

**核心视觉规则**：
- 拖放区不要 background fill，只用 `1px dashed var(--primary)` + 大字提示
- 拖入时 dashed 变 solid，背景填充 `--primary-soft`
- 进度阶段用 4 个方块（每个方块 12×12px），未完成是 1px 黑边空心，完成实心黑，当前阶段 Klein 蓝实心 + 呼吸动画
- 进度文字用 mono `40%`，阶段名用 mono uppercase `EMBED`
- 完成卡片可展开预览：提取出的 chunk 列表（前 3 条）+ 概念列表（标签云）

**设计稿 Prompt**：
```
Design a material upload screen for a Chinese course platform.
Style: brutalist academic, 0px border radius, generous negative space (40-80px between sections),
Inter + JetBrains Mono typography. Background white, text black, accent Klein blue (#0022ff).

Top section: drag-and-drop zone, full-width, 200px tall.
- 1px dashed Klein blue border, no fill.
- Centered: 24px black "拖放文件至此 / 点击选择",
  beneath in 12px mono uppercase #999999 "支持 PDF / TXT / MD"
- On hover/dragover: border becomes 2px solid Klein blue, background subtle Klein-blue tint (rgba(0,34,255,0.04)).

Middle section: header "PROCESSING QUEUE" in 11px mono uppercase #666, followed by a 1px black hairline.

Below header: vertical stack of upload cards.
Each card layout:
- Left: a 24px tall mono uppercase number label like "01", "02".
- Center: filename in 16px black, beneath a 4-block progress indicator
  (each block 12x12px, 8px gap; pending = white with 1px black border,
   completed = filled black, in-progress = filled Klein blue with subtle pulse animation).
- Right: percentage in mono 14px (#000) and current stage label in mono 11px uppercase.

Below the progress row, a row of stage names:
"SAVE → EXTRACT → EMBED → LLM EXTRACT" in mono 10px,
- Completed stages have black text and a · separator,
- Current stage Klein blue + ← arrow,
- Future stages #999 + → arrow.

Card padding: 24px. Card separators: 1px black hairline.

For completed cards, add a small 13px Klein blue link "[查看提取结果] →" at bottom right.
On click, the card expands inline to show:
- "CHUNKS PREVIEW" header (mono uppercase 11px), 3 chunk previews stacked,
- "CONCEPTS EXTRACTED" header, concepts shown as inline text separated by · dots.

Empty state for the queue: a single line of #999 text "尚无材料 — 拖放上方区域开始".
```

---

### 2.3 Teacher Assignments Console — 布置 + 批改

**布局**（左导航 + 右工作区）：

```
┌────────────────────────────────────────────────────────────────┐
│  ASSIGNMENTS · 教师作业台                                        │
│  ──────────────                                                 │
│                                                                 │
│  ┌──────────┐  ┌────────────────────────────────────────────┐  │
│  │ 课程过滤   │  │ 03   阅读：注意力机制基础                   │  │
│  │ ─        │  │      ai-intro · ch.3 · 已发布 · 截止 5/12  │  │
│  │ 全部 (12) │  │      ────                                  │  │
│  │ AI (7)   │  │      24 / 30 已提交     12 已批改           │  │
│  │ 脑认知 (5)│  │                                            │  │
│  │          │  │      ┌─ 提交列表 ─────────────────────────┐ │  │
│  │ 状态过滤  │  │      │ 01  Alice    已交  9.2  [批改]    │ │  │
│  │ ─        │  │      │ 02  Bob      已批改 8.5  [查看]    │ │  │
│  │ 草稿(3)  │  │      │ 03  Charlie  已交  --  [批改]      │ │  │
│  │ 已发(8)  │  │      └────────────────────────────────────┘ │  │
│  │ 归档(1)  │  │                                            │  │
│  │          │  │      [+ 新建作业]                           │  │
│  └──────────┘  └────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

**设计稿 Prompt**：
```
Design a teacher assignments console for a Chinese university course platform.
Style: brutalist academic, 0px border radius, Inter + JetBrains Mono typography.
Background white, text black, accent Klein blue (#0022ff).

Layout: left sidebar (240px wide, 1px black right border) + main work area.

Left sidebar:
- "COURSE FILTER" header in mono uppercase 11px gray.
- Vertical list of courses, each row 40px tall:
  text in 14px black, count in mono 12px gray right-aligned, e.g. "全部     12".
- Active filter: Klein blue 2px left border, Klein blue text.
- Below, "STATUS FILTER" with same pattern: 草稿/已发布/归档.

Main work area (40px padding):
- Page title "ASSIGNMENTS · 教师作业台" in 32px Inter 800 weight, kerning -0.03em.
- 1px black hairline below.

Assignment list, each item is a card:
- Top row: large mono number 01-99 (32px black), then title in 20px black.
- Subtitle in 13px gray: "course · chapter · status · due-date" separated by ·.
- A 1px black hairline.
- Stats row: "24 / 30 已提交 · 12 已批改" in 14px black, mono numbers.
- Inside the card, a sub-table of submissions:
  - Header in 11px mono uppercase: 编号 / 学生 / 状态 / 分数 / 操作.
  - Each row 36px tall, separated by 1px gray (#e9ecef) hairline.
  - Score column: mono 14px black for graded, "--" gray for ungraded.
  - Action column: text link "批改" in Klein blue with no underline,
    underline appearing on hover.

Cards separated by 32px vertical gap.
Each card has 24px padding.

Top right of the work area: a "+ 新建作业" button — 48px tall pill (border-radius 999px),
Klein blue background, white text.

Empty state for an empty filter: a centered 13px gray message "尚无作业".
```

---

### 2.4 Student Progress Dashboard — 个人学习画像

**布局**（三段：状态条 + 学习活动热图 + 推荐路径）：

```
┌────────────────────────────────────────────────────────────────┐
│  PROGRESS · 学习画像                                              │
│  ──────────────                                                 │
│                                                                 │
│  Alice · 学生  ·  注册 14 天                                      │
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ 24       │ │ 8 / 12   │ │ 18       │ │ 4        │            │
│  │ 总事件    │ │ 章节完成  │ │ Tutor 提问│ │ 实验     │            │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘            │
│                                                                 │
│  ACTIVITY HEATMAP · 过去 30 天                                   │
│  ──────                                                          │
│  [GitHub-style 热图，每格 12×12]                                  │
│                                                                 │
│  RECENT EVENTS                                                  │
│  ──────                                                          │
│  10:24  asked_tutor    AI · ch.3 · "什么是 Self-Attention?"     │
│  10:18  completed      AI · ch.3                               │
│  09:55  viewed         AI · ch.3                               │
│                                                                 │
│  RECOMMENDED NEXT                                                │
│  ──────                                                          │
│  ┌──────────────────────────────────┐                           │
│  │ ai-intro · 第4章 反向传播          │                           │
│  │ 前置已完成 · 预计 25 分钟           │                           │
│  │ [开始学习] →                      │                           │
│  └──────────────────────────────────┘                           │
└────────────────────────────────────────────────────────────────┘
```

**设计稿 Prompt**：
```
Design a student learning progress dashboard.
Style: brutalist academic minimalism, 0px radius, white BG, black text, Klein blue (#0022ff) accents.
Inter + JetBrains Mono. Negative space heavy.

Top: page title "PROGRESS · 学习画像" 32px black 800 weight.
Beneath: student name + role + "注册 14 天" in 14px gray.

Stat tiles row: 4 tiles in a row, each 1px solid black border, 24px padding, no fill.
Each tile:
- Top: huge number in 56px black, mono variant. e.g. 24, 8/12, 18.
- Bottom: 11px mono uppercase gray label, e.g. "总事件", "章节完成".
- Hover: invert (black BG, white text) with 200ms ease.

Section "ACTIVITY HEATMAP · 过去 30 天":
- Header in 11px mono uppercase gray, hairline 1px black below.
- A GitHub-style heatmap: 30 columns × 1 row (or 7 rows if weekly grouped).
- Each cell 12x12px with 2px gap.
- Empty cell: #f1f3f5. Low: #c5cdd6. Medium: #6b7986. High: Klein blue (#0022ff).
- On hover, show a tooltip "5/3 · 4 events" in mono 11px.

Section "RECENT EVENTS":
- Vertical list of event rows, each 32px tall, separated by 1px hairline gray.
- Each row: time in mono 12px (e.g. "10:24"),
  event_type in mono uppercase 11px Klein blue ("ASKED_TUTOR"),
  context in 14px black ("AI · ch.3 · '什么是 Self-Attention?'").

Section "RECOMMENDED NEXT":
- A single recommended chapter card, 1px solid black border.
- Title in 18px black, subtitle 13px gray.
- Bottom right: text link "开始学习 →" in Klein blue.
```

---

### 2.5 Cohort Heatmap (Teacher) — 班级聚合视图

**布局**（章节×学生矩阵 + 事件分布柱状图）：

```
┌────────────────────────────────────────────────────────────────┐
│  COHORT · 班级仪表盘                                             │
│  ──────────────                                                 │
│  ai-intro · 30 学生 · 12 章节                                   │
│                                                                 │
│  ENGAGEMENT MATRIX                                              │
│  ──────                                                          │
│       ch1  ch2  ch3  ch4  ch5  ch6  ch7  ch8  ch9 ch10         │
│  ─────────────────────────────────────────────────              │
│  Alice ■   ■   ■   ■   □   .   .   .   .   .                  │
│  Bob   ■   ■   ■   ■   ■   ■   .   .   .   .                  │
│  Carl  ■   ■   ■   .   .   .   .   .   .   .                  │
│   ...                                                           │
│                                                                 │
│  EVENT DISTRIBUTION (柱状图)                                     │
│  ──────                                                          │
│  viewed       ████████████████████████  142                     │
│  completed    ████████████  72                                  │
│  asked_tutor  ████████  48                                      │
│  ...                                                            │
└────────────────────────────────────────────────────────────────┘
```

**设计稿 Prompt**：
```
Design a teacher cohort dashboard for a Chinese course.
Style: brutalist academic, 0px radius, Inter + JetBrains Mono, white/black/Klein blue (#0022ff).

Header: "COHORT · 班级仪表盘" 32px black 800.
Subtitle: "ai-intro · 30 students · 12 chapters" 14px gray.

Engagement matrix:
- Header "ENGAGEMENT MATRIX" 11px mono uppercase gray, 1px black hairline.
- Grid: rows = students (each 24px tall), columns = chapters (each 32px wide).
- Column headers: "ch1", "ch2", ... in 11px mono uppercase gray, top of grid.
- Row labels: student names in 13px black, left of grid.
- Cell states (each 16x16px centered in cell):
  - Empty (no view): 1px gray dot, 4x4px, centered.
  - Viewed: 1px black square outline, 12x12px.
  - Completed: filled black square, 12x12px.
  - In progress: filled Klein blue square with subtle 2s pulse animation.
- 1px gray hairlines between rows. No vertical lines.

Event distribution chart:
- Header "EVENT DISTRIBUTION" 11px mono uppercase gray + hairline.
- Horizontal bar chart, each bar 24px tall.
- Label (left): event_type in mono uppercase 12px black.
- Bar: filled with Klein blue, height = count proportional, no rounded corners.
- Right of bar: count in mono 14px black.
- Bars separated by 8px vertical gap.

Bottom CTA: link "→ 导出 CSV" in mono Klein blue at the right.

Negative space: 64px between sections, 32px page padding.
```

---

### 2.6 Job Toast Strip — 全局右下角任务流

**布局**（右下角浮动条）：

```
                                   ┌──────────────────────────────┐
                                   │ ●●●●○  上传 neural-net.pdf    │
                                   │ ─                            │
                                   │ 嵌入向量中 · 40%              │
                                   │                       [×]    │
                                   └──────────────────────────────┘
                                   ┌──────────────────────────────┐
                                   │ ●●●●●  上传 attention.pdf     │
                                   │ ─                            │
                                   │ 完成 · 12 chunks              │
                                   │                       [查看]   │
                                   └──────────────────────────────┘
```

**设计稿 Prompt**：
```
Design floating job-status toasts for the bottom-right corner of an academic web app.
Style: brutalist, 0px radius, Inter + JetBrains Mono, white BG, black border (1px solid).
Stack vertically with 12px gap, 24px from screen edges.

Each toast: 320px wide, ~80px tall, 16px padding.
Layout per toast:
- Top row: 4-block progress indicator (12x12, 4 px gap) on left,
  filename in 13px black on right.
- Hairline 1px gray.
- Bottom row: status text in 13px (#666), e.g. "嵌入向量中" left,
  percentage in mono 13px black right.
- Top-right corner: × close button 16px (only after completion).
- For completed jobs: replace × with text link "查看" in Klein blue 13px.

In-progress toast: blocks 1-N filled black, current block Klein blue with pulse,
remaining blocks 1px black outline.
Failed toast: replace progress blocks with a single Klein-red 1px solid square
and red error message "解析失败".

Slide-in animation: from x:+20 to x:0 over 300ms, easing cubic-bezier(0.16,1,0.3,1).
Auto-dismiss completed toasts after 6 seconds with a fade-out 200ms.
```

---

## Part 3 — Motion / Interaction 设计轨道

每个组件给两个：① 状态变化时的动画规则 ② Prompt 风格的 motion 描述（喂给 motion designer 或 GSAP 实现者）

### Motion Tokens（在 tokens.css 基础上扩展，建议加进去）

```css
/* === Motion v2 ===  */
--motion-snap: 120ms;            /* 即时反馈：按钮按下、tab 切换 */
--motion-quick: 200ms;           /* 短交互：toast 入场、card hover */
--motion-flow: 360ms;            /* 主动作：页面切换、模态出现 */
--motion-cinematic: 720ms;       /* 仪式感：路由切换、首屏 reveal */

--ease-snap: cubic-bezier(0.32, 0, 0.32, 1);     /* iOS 触感 */
--ease-flow: cubic-bezier(0.16, 1, 0.3, 1);       /* 已有 expo */
--ease-decel: cubic-bezier(0, 0, 0.2, 1);         /* material decel */
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1); /* 轻微回弹 */
```

### 3.1 Tutor 流式打字 + Tool 调用动画

**6 个动画时刻（按事件顺序）**：

1. **提交问题** —— 输入框 1px 黑色 underline 收缩到 0，用户消息从下方 16px 滑入并淡入，160ms snap
2. **思考态** —— Klein 蓝 [AI] 标签出现，下方一个 3 字符 mono 省略号 `· · ·`，每个点错相 200ms 淡入淡出（呼吸感）
3. **Tool call 触发** —— 右栏从右侧 20px 滑入一个 mono 单行 `─ search_materials({...})`，背景色 200ms 内从 Klein 蓝闪烁回白
4. **Tool result 返回** —— 工具行右侧出现 mono 灰色 `✓ 5 results` 字样，左侧蓝色方块变实心（脉冲一次）
5. **Token 流入** —— 每个 token 落位时，下方 1px 高的 Klein 蓝光标 `▌` 跟随移动；行尾时光标 1.0s 周期闪烁（不要 50% 闪烁，要 600ms 显 + 400ms 隐，更显机械）
6. **完成态** —— 引用面板从右侧逐项滑入，每项错相 80ms；最后输入框边框淡回，260ms

**Motion Prompt**：
```
Design micro-animations for an AI tutor streaming chat.
Brand: brutalist academic, sharp edges, Klein blue (#0022ff), motion is restrained but precise.

Sequence on submit:
1. SUBMIT (160ms, ease-snap): input field's 1px black underline shrinks from full width to 0.
   The user's question message slides up 16px and fades from 0 to 1 opacity.
2. THINKING (loop until first token): a 3-dot mono ellipsis "· · ·" beneath an [AI] label.
   Each dot fades 0.2 → 1 → 0.2 in a 600ms cycle, 200ms staggered between dots. No bouncing.
3. TOOL_CALL_FIRED (180ms): a single-line tool entry slides in from the right (+20px → 0).
   Brief Klein-blue flash on the row's background (alpha 0.12 → 0 over 200ms).
4. TOOL_RESULT (snappy, 100ms): on the row, a mono "✓ 5 results" appears with a 12% scale-down spring,
   and the small Klein-blue square at the row start pulses (scale 1 → 1.15 → 1 over 200ms).
5. TOKEN_STREAM: each token appears instantly (no per-character anim — too slow for Chinese).
   A 2px wide × 16px tall Klein blue caret "▌" sits at the end of the latest text run.
   Caret blink: 600ms visible + 400ms hidden (mechanical, not 50/50).
6. COMPLETE (340ms total): citation cards on the right slide in from x: +20 to 0, fade in,
   stagger 80ms between cards. The input bottom-line returns to full width with ease-flow.

All animations honor prefers-reduced-motion: any movement collapses to opacity-only fades at 200ms.
No bouncing. No springs except the brief tool-result pulse. Flat brutalist, but alive.
```

### 3.2 Material Upload — 4 阶段进度脉动

**核心规则**：
- 当前阶段方块呼吸：scale 1.0 → 1.08 → 1.0，opacity 1.0 → 0.7 → 1.0，1.4s 周期 ease-in-out
- 阶段切换：刚完成的方块 200ms 填充黑色 + 微 1.05 弹一下；下一个方块开始 Klein 蓝呼吸
- 拖入文件：dashed 边框转 solid，0.2s ease，背景色 `--primary-soft` 渐入
- 失败：方块变红 `#dc2626` 同时整个 card 左右 4px shake（120ms × 2 次）
- 完成：进度行整行从下到上扫一道 Klein 蓝 1px 线，200ms

**Motion Prompt**：
```
Design progress animations for an async file upload pipeline with 4 stages.

States per block:
- Pending: 12x12px square, 1px black outline, no fill.
- Active: filled Klein blue (#0022ff), continuous pulse (scale 1 → 1.08 → 1, opacity 1 → 0.7 → 1, 1.4s ease-in-out).
- Completed: fill snaps from Klein blue to solid black (180ms), then a quick 1.05 pop (160ms ease-spring).
- Failed: fills with #dc2626 (red), then the entire card shakes ±4px on x-axis, twice, total 240ms.

Drop zone:
- Idle: 1px dashed Klein blue border.
- Drag-over: border becomes 2px solid Klein blue (200ms ease-flow),
  background fades from transparent to rgba(0,34,255,0.04) over 200ms.
- Drop: border bounces back to 1px dashed (340ms cubic-bezier(0.34,1.56,0.64,1)).

Card lifecycle:
- Enter: from y:+12, opacity 0 → 1, 280ms ease-flow.
- Stage transition: a 1px Klein blue line wipes left → right across the progress row in 200ms,
  then settles into the next block's pulse.
- Complete: 1px Klein blue line wipes top → bottom across the entire card in 240ms,
  then card subtitle text "完成 · 12 chunks · 8 概念" cross-fades in over 200ms.

reduced-motion: all pulses and shakes become static; transitions become 100ms opacity fades.
```

### 3.3 Heatmap 入场 + 悬停

**规则**：
- 入场：从左到右瀑布式填色，每列错相 12ms，每个 cell 自身从 `#f1f3f5` 100ms ease-out 过渡到目标色
- 悬停：cell `outline: 2px solid #000` 出现（不填充，不变形），同时 tooltip 从下方 4px 滑入 + 淡入 140ms
- 点击：弹出 detail drawer 从右侧 360ms 滑入

**Motion Prompt**：
```
Design entry and interaction animations for a 30-column heatmap.

Entry (one-time on mount):
- Cells start at #f1f3f5.
- Sequential fill: each column N starts its color transition at delay = N * 12ms.
- Each cell transitions its background color over 100ms with ease-out (cubic-bezier(0,0,0.2,1)).
- Total duration ≈ 460ms for 30 columns.

Hover:
- A 2px solid black outline appears on the cell (no fill change, no scale).
- 80ms ease-snap.
- A tooltip slides up from below by 4px and fades in over 140ms.
  Tooltip is 1px solid black, white background, no shadow, mono 11px text.

Click:
- A detail drawer slides in from the right edge over 360ms ease-flow.
- Width: min(480px, 40vw).
- Body scroll is locked while drawer is open.
- Backdrop is rgba(0,0,0,0.04), no blur (kept brutalist).
- Close: same 360ms in reverse + Esc key support.

reduced-motion: entry becomes a single 200ms opacity fade for the whole grid;
hover removes outline animation (instant); drawer slides become 200ms opacity fade.
```

### 3.4 章节路径导航 — Spatial Camera 升级版（已有，扩展用于 progress）

**规则**：
- 当前章节节点：放大 1.15 + Klein 蓝填充 + 周围 32px 半径柔光（不是 box-shadow，是 `radial-gradient` mask）
- 已完成节点：填充黑色 + 编号变白
- 未开始节点：1px 黑边空心 + 灰色编号
- 切换章节：不是简单淡入淡出，而是「相机推进」：当前活动节点平移到屏幕中心（720ms cinematic），其他节点错相位移

**Motion Prompt**：
```
Extend the existing "spatial camera" course path canvas to also visualize progress.

Node states:
- Locked (prerequisite not done): outline 1px solid #999, number in 32px gray (#999).
- Unstarted: outline 1px solid black, number in 32px black, 1.0 scale.
- Active (currently studying): scale 1.15, fill Klein blue, number white, with a soft radial halo
  (radial-gradient from rgba(0,34,255,0.18) at center to transparent at 32px) — no box-shadow.
- Completed: fill black, number white, scale 1.0, no halo.

Transition between active chapters (when a student progresses):
- The newly-active node animates: scale 1 → 1.15, fill 0 → Klein blue (240ms).
- The previously-active node settles: scale 1.15 → 1.0, fill Klein blue → black (320ms).
- Camera push: the entire SVG container translates so the new active node lands at viewport center,
  720ms cubic-bezier(0.16,1,0.3,1).
- Other nodes ease into their new offsets in parallel, no individual stagger (preserves the
  "we are pulling the world, not the nodes" feeling).

reduced-motion: collapse the camera push to an instant scroll, halve all durations.
```

---

## Part 4 — 实施路线（前端 4 阶段）

```
Phase F1 — Tutor v2 + Material Studio (P0, 估计 2 sessions)
├── 装 marked + dompurify（流式 markdown 渲染）
├── api/tutor.js 加 streamAsk()
├── api/materials.js 加 uploadAsync()
├── api/jobs.js 新建 pollJob()
├── 重写 AITutorPanel.vue（流式 + tool 可视化）
├── 新建 MaterialUploadStudio.vue
└── 新建 JobToastStrip.vue（全局挂载到 AppShell）

Phase F2 — Agent Console (P0, 1 session)
├── api/agents.js 新建
├── 新建 AgentConsoleView.vue
└── 路由 /agent 接 AgentConsole

Phase F3 — Assignments (P1, 2 sessions)
├── api/assignments.js
├── api/users.js（含 IdentitySwitcher）
├── 新建 TeacherAssignmentsView.vue
├── 新建 StudentAssignmentInbox.vue
└── 新建 AssignmentDetailDrawer.vue

Phase F4 — Progress (P1, 2 sessions)
├── api/progress.js
├── 新建 StudentProgressView.vue（含 ActivityHeatmap 组件）
├── 新建 CohortDashboardView.vue
└── 集成到 Dashboard
```

---

## Part 5 — 你拿去做设计稿的清单

复制下面这 6 个 prompt 直接喂给 v0.dev / Figma AI / Midjourney（注明 web UI design）：

1. ✅ **TutorPanel v2** — 见 §2.1
2. ✅ **Material Upload Studio** — 见 §2.2
3. ✅ **Teacher Assignments Console** — 见 §2.3
4. ✅ **Student Progress Dashboard** — 见 §2.4
5. ✅ **Cohort Heatmap** — 见 §2.5
6. ✅ **Job Toast Strip** — 见 §2.6

每个 prompt 都已内嵌：
- 配色规范（white/black/Klein blue + 灰阶）
- 字体系统（Inter + Mono）
- 圆角 = 0 的 brutalist 立场
- 元素尺寸（精确 px）
- 状态规则（hover/active/empty）

如果用 Midjourney，把 prompt 末尾加一句：
`--style raw --ar 16:9 --no shadows blur soft-edges rounded-corners`

如果用 v0.dev / Cursor，直接粘贴并加一句：
"Use Vue 3 + plain CSS variables matching tokens.css (Klein blue #0022ff, 0px radius), no Tailwind."

如果用 Figma AI，加一句：
"Generate a desktop frame at 1440x900, use Auto-layout for stacks, components for repeating elements."

---

## 我的建议

先做 **Tutor v2 + Material Upload Studio**（Phase F1）。两个理由：

1. **可视回报最高** — 流式打字 + 进度条是用户最直观感受到"AI 在工作"的两个时刻
2. **后端已就绪** — `?stream=1` 和 `?async=1` 都已经能用，前端做完立刻能跑

要我下手开始实现 Phase F1 吗？还是你先拿这套 prompt 去出设计稿？
