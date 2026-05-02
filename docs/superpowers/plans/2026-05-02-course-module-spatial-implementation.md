# Course Module Spatial Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the A+C course module redesign: an editorial syllabus path canvas with an attached, usable chapter workbench and restrained spatial camera motion.

**Architecture:** Keep data loading in `CourseView.vue`, move small display normalization into a testable helper, and keep `ChapterWorkspace`, `AITutorPanel`, and `GraphPanel` as focused workbench tools. CSS owns the spatial path layout, responsive vertical journey, and reduced-motion behavior.

**Tech Stack:** Vue 3 composition API, Vite, Vitest, D3 graph rendering, CSS custom properties, optional existing GSAP dependency for route/chapter camera motion.

---

## File Structure

- Create `frontend/src/views/courseViewState.js`: pure helpers for chapter labels, subtopics, and path position classes.
- Create `frontend/src/views/courseViewState.test.js`: Vitest coverage for those helpers.
- Modify `frontend/src/views/CourseView.vue`: replace card-stack layout with syllabus path canvas and attached workbench.
- Modify `frontend/src/components/ChapterWorkspace.vue`: make chapter content fit the workbench visual system and keep `select-question` behavior.
- Modify `frontend/src/components/AITutorPanel.vue`: compact the tutor into a tool panel and keep request behavior unchanged.
- Modify `frontend/src/components/GraphPanel.vue`: keep current graph behavior, adjust labels/classes if needed for course workbench integration.
- Modify `frontend/src/styles/app.css`: add spatial course module, workbench, camera, graph, and responsive styles.
- Avoid editing `frontend/src/views/DashboardView.vue` unless a build error directly requires it.

## Task 1: Course View State Helpers

**Files:**
- Create: `frontend/src/views/courseViewState.js`
- Create: `frontend/src/views/courseViewState.test.js`

- [ ] **Step 1: Write helper tests**

Create `frontend/src/views/courseViewState.test.js`:

```js
import { describe, expect, it } from 'vitest';
import { chapterDisplayTitle, chapterNodeClass, chapterSubtopics } from './courseViewState';

describe('course view state helpers', () => {
  it('builds readable chapter titles with fallbacks', () => {
    expect(chapterDisplayTitle({ title: 'Search and Problem Solving' })).toBe('Search and Problem Solving');
    expect(chapterDisplayTitle({ name: 'Brain and Cognition' })).toBe('Brain and Cognition');
    expect(chapterDisplayTitle({ id: 'chapter-4' })).toBe('chapter-4');
  });

  it('extracts up to four subtopics from chapter metadata', () => {
    expect(chapterSubtopics({
      sections: ['Agents', 'Search', 'Heuristics', 'Optimization', 'Planning']
    })).toEqual(['Agents', 'Search', 'Heuristics', 'Optimization']);

    expect(chapterSubtopics({
      objectives: ['Understand attention', 'Explain memory']
    })).toEqual(['Understand attention', 'Explain memory']);
  });

  it('falls back to a learning action when no subtopics exist', () => {
    expect(chapterSubtopics({})).toEqual(['进入章节工作台']);
  });

  it('cycles path position classes for long courses', () => {
    expect(chapterNodeClass(0)).toBe('course-path-node path-node-1');
    expect(chapterNodeClass(4)).toBe('course-path-node path-node-5');
    expect(chapterNodeClass(5)).toBe('course-path-node path-node-1');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && npm test -- courseViewState.test.js`

Expected: FAIL because `frontend/src/views/courseViewState.js` does not exist.

- [ ] **Step 3: Implement helpers**

Create `frontend/src/views/courseViewState.js`:

```js
export function chapterDisplayTitle(chapter = {}) {
  return chapter.title || chapter.name || chapter.id || '未命名章节';
}

export function chapterSubtopics(chapter = {}) {
  const source = Array.isArray(chapter.sections)
    ? chapter.sections
    : Array.isArray(chapter.objectives)
      ? chapter.objectives
      : Array.isArray(chapter.topics)
        ? chapter.topics
        : [];

  const topics = source
    .filter((item) => typeof item === 'string' && item.trim().length > 0)
    .map((item) => item.trim())
    .slice(0, 4);

  return topics.length > 0 ? topics : ['进入章节工作台'];
}

export function chapterNodeClass(index) {
  return `course-path-node path-node-${(index % 5) + 1}`;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd frontend && npm test -- courseViewState.test.js`

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add frontend/src/views/courseViewState.js frontend/src/views/courseViewState.test.js
git commit -m "feat: add course path view helpers"
```

## Task 2: Spatial Course Path Canvas

**Files:**
- Modify: `frontend/src/views/CourseView.vue`
- Modify: `frontend/src/styles/app.css`
- Test: `frontend/src/views/courseViewState.test.js`

- [ ] **Step 1: Replace course page markup with path canvas**

In `frontend/src/views/CourseView.vue`, import helpers:

```js
import { chapterDisplayTitle, chapterNodeClass, chapterSubtopics } from './courseViewState';
```

Replace the loaded-course branch with:

```vue
<div v-else-if="course" class="course-spatial-shell">
  <aside class="course-spatial-intro">
    <p class="kicker course-kicker">COURSE SYLLABUS</p>
    <h1 class="course-spatial-title">
      {{ course?.title || course?.name || courseId }}
    </h1>
    <div class="course-blue-rule"></div>
    <p class="course-spatial-copy">
      {{ course?.summary || course?.description || '沿着章节路径进入阅读、AI 导师、知识图谱与复习任务。' }}
    </p>
  </aside>

  <section class="course-path-stage" aria-label="课程章节路径">
    <div class="course-path-line line-1"></div>
    <div class="course-path-line line-2"></div>
    <div class="course-path-line line-3"></div>
    <div class="course-path-line line-4"></div>

    <button
      v-for="(chapter, index) in chapters"
      :key="chapter.id || index"
      type="button"
      :class="[chapterNodeClass(index), { 'is-active': activeChapter?.id === chapter.id }]"
      @click="loadChapter(chapter.id)"
    >
      <span class="course-node-head">
        <span class="course-node-number">{{ String(index + 1).padStart(2, '0') }}</span>
        <span class="course-node-rule"></span>
        <span class="course-node-pin"></span>
      </span>
      <span class="course-node-title">{{ chapterDisplayTitle(chapter) }}</span>
      <span class="course-node-topics">
        <span v-for="(topic, topicIndex) in chapterSubtopics(chapter)" :key="topic">
          <b>{{ index + 1 }}.{{ topicIndex + 1 }}</b>{{ topic }}
        </span>
      </span>
    </button>

    <section class="course-workbench" aria-live="polite">
      <div v-if="chapterLoading" class="panel">
        <p class="status-message">正在加载章节…</p>
      </div>
      <div v-else-if="chapterError" class="panel">
        <p class="status-message error">{{ chapterError }}</p>
      </div>
      <ChapterWorkspace
        v-else-if="activeChapter"
        :chapter="activeChapter"
        @select-question="selectTutorQuestion"
      />
      <div v-else class="panel">
        <p class="status-message">请选择一个章节开始。</p>
      </div>

      <AITutorPanel
        :course-id="courseId"
        :chapter-id="activeChapter?.id || ''"
        :initial-question="selectedQuestion"
      />

      <div v-if="graphLoading" class="panel">
        <p class="status-message">正在加载图谱…</p>
      </div>
      <template v-else-if="graphError">
        <p class="status-message warning">{{ graphError }}</p>
        <GraphPanel :graph="graph" />
      </template>
      <GraphPanel v-else :graph="graph" />
    </section>
  </section>
</div>
```

- [ ] **Step 2: Add spatial canvas CSS**

Add to `frontend/src/styles/app.css`:

```css
.course-spatial-shell {
  display: grid;
  grid-template-columns: minmax(280px, 0.72fr) minmax(640px, 1.28fr);
  gap: clamp(48px, 7vw, 112px);
  align-items: start;
}

.course-spatial-title {
  max-width: 620px;
  color: var(--text-1);
  font-size: clamp(3.5rem, 7vw, 7rem);
  font-weight: 500;
  letter-spacing: 0.08em;
  line-height: 0.98;
  text-transform: uppercase;
}

.course-blue-rule {
  width: 52px;
  height: 4px;
  margin: 34px 0;
  background: var(--primary);
}

.course-spatial-copy {
  max-width: 360px;
  color: var(--text-3);
  font-size: 14px;
  line-height: 1.85;
}

.course-path-stage {
  position: relative;
  min-height: 1040px;
  perspective: 1200px;
}

.course-path-node {
  position: absolute;
  z-index: 2;
  width: 320px;
  min-height: 180px;
  padding: 0;
  text-align: left;
  color: var(--text-1);
  transform: translateZ(0);
  transition: transform var(--dur-3) var(--ease-out-expo), opacity var(--dur-3) var(--ease-out-expo);
}

.course-path-node.is-active {
  transform: translate3d(0, -8px, 80px) scale(1.035);
}

.course-node-head {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 14px;
}

.course-node-number {
  font-size: 4rem;
  font-weight: 300;
  line-height: 0.9;
}

.course-node-rule {
  flex: 1;
  height: 1px;
  background: var(--border-strong);
}

.course-node-pin {
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background: var(--text-1);
}

.course-path-node.is-active .course-node-pin {
  background: var(--primary);
  box-shadow: 0 0 0 14px var(--primary-soft);
}

.course-node-title {
  display: block;
  margin-bottom: 14px;
  font-size: 1.35rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  line-height: 1.25;
  text-transform: uppercase;
}

.course-node-topics {
  display: grid;
  gap: 4px;
  color: var(--text-3);
  font-size: 13px;
  line-height: 1.55;
}

.course-node-topics span {
  display: grid;
  grid-template-columns: 42px 1fr;
  gap: 8px;
}

.course-node-topics b {
  color: var(--text-4);
  font-family: var(--font-mono);
  font-size: 11px;
}

.path-node-1 { top: 0; left: 5%; }
.path-node-2 { top: 88px; right: 4%; }
.path-node-3 { top: 360px; left: 0; }
.path-node-4 { top: 430px; right: 18%; }
.path-node-5 { top: 660px; left: 28%; }

.course-path-line {
  position: absolute;
  z-index: 1;
  height: 1px;
  background: var(--border-strong);
  opacity: 0.86;
}

.course-path-line.line-1 { top: 44px; left: 22%; width: 36%; }
.course-path-line.line-2 { top: 312px; left: 24%; width: 42%; }
.course-path-line.line-3 { top: 454px; left: 14%; width: 38%; }
.course-path-line.line-4 { top: 704px; left: 48%; width: 30%; border-top: 1px dashed var(--border-strong); background: transparent; }
```

- [ ] **Step 3: Run helper tests and build**

Run:

```bash
cd frontend && npm test -- courseViewState.test.js
cd frontend && npm run build
```

Expected: tests pass and build succeeds.

- [ ] **Step 4: Commit**

Run:

```bash
git add frontend/src/views/CourseView.vue frontend/src/styles/app.css
git commit -m "feat: add spatial course path canvas"
```

## Task 3: Attached Chapter Workbench Tools

**Files:**
- Modify: `frontend/src/components/ChapterWorkspace.vue`
- Modify: `frontend/src/components/AITutorPanel.vue`
- Modify: `frontend/src/styles/app.css`
- Test: `frontend/src/api/course-workspace.test.js`

- [ ] **Step 1: Update chapter workspace markup**

Change `ChapterWorkspace.vue` root classes and section labels to:

```vue
<article class="panel chapter-workspace course-tool-panel">
  <header class="panel-header course-tool-header">
    <p class="kicker">Selected Chapter</p>
    <h2>{{ chapter.title || '未命名章节' }}</h2>
  </header>
```

Change the ask tutor button class:

```vue
<button type="button" class="btn btn-outline btn-sm" @click="$emit('select-question', item.prompt)">
  问导师
</button>
```

- [ ] **Step 2: Update tutor panel markup**

Change `AITutorPanel.vue` root/header/button classes:

```vue
<aside class="panel tutor-panel course-tool-panel">
  <header class="panel-header course-tool-header">
    <p class="kicker">AI Tutor</p>
    <h2>就本章内容提问</h2>
  </header>
```

Change textarea class and submit button:

```vue
<textarea
  id="tutor-question"
  v-model="question"
  class="form-control"
  rows="5"
  placeholder="就当前章节提出你的问题"
/>
<button type="submit" class="btn btn-primary" :disabled="isAskDisabled">
  {{ loading ? '正在提问…' : '提问' }}
</button>
```

- [ ] **Step 3: Add workbench CSS**

Add to `frontend/src/styles/app.css`:

```css
.course-workbench {
  position: absolute;
  right: 0;
  top: 760px;
  z-index: 4;
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(280px, 0.75fr);
  gap: 18px;
  width: min(920px, 92%);
  transform: translateZ(120px);
}

.course-workbench .graph-panel {
  grid-column: 1 / -1;
}

.course-tool-panel {
  border-color: var(--border-strong);
  box-shadow: 0 18px 70px rgba(8, 12, 20, 0.06);
}

.course-tool-header .kicker {
  color: var(--primary);
}

.content-block {
  display: grid;
  gap: 12px;
  padding-top: 22px;
  border-top: 1px solid var(--border-default);
}

.content-block + .content-block {
  margin-top: 22px;
}

.content-block h3,
.tutor-answer h3 {
  margin: 0;
  color: var(--text-1);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.objective-list,
.clean-list {
  display: grid;
  gap: 10px;
  padding: 0;
  list-style: none;
}

.chapter-body,
.tutor-answer p,
.quiz-details {
  color: var(--text-2);
  font-size: 14px;
  line-height: 1.75;
}

.quiz-list {
  display: grid;
  gap: 10px;
}

.quiz-item {
  border: 1px solid var(--border-default);
  padding: 14px;
}

.quiz-item summary {
  cursor: pointer;
  color: var(--text-1);
  font-weight: 600;
}

.tutor-form {
  display: grid;
  gap: 12px;
}

.tutor-answer,
.citations {
  display: grid;
  gap: 12px;
  margin-top: 20px;
}
```

- [ ] **Step 4: Run existing behavior tests**

Run: `cd frontend && npm test -- course-workspace.test.js`

Expected: PASS. The UI class changes must not break helper/API behavior.

- [ ] **Step 5: Commit**

Run:

```bash
git add frontend/src/components/ChapterWorkspace.vue frontend/src/components/AITutorPanel.vue frontend/src/styles/app.css
git commit -m "feat: attach chapter workbench tools"
```

## Task 4: Graph Integration, Responsive Layout, And Verification

**Files:**
- Modify: `frontend/src/components/GraphPanel.vue`
- Modify: `frontend/src/styles/app.css`
- Test: `frontend/src/components/graphTransform.test.js`

- [ ] **Step 1: Align graph labels with course language**

In `GraphPanel.vue`, keep the current behavior and ensure the root/header remain:

```vue
<article class="panel graph-panel graph-workbench course-tool-panel">
  <header class="graph-toolbar graph-workbench-toolbar">
    <div>
      <p class="kicker">Knowledge Graph</p>
      <h2>知识图谱</h2>
    </div>
```

- [ ] **Step 2: Add graph and responsive CSS**

Add to `frontend/src/styles/app.css`:

```css
.graph-workbench {
  display: grid;
  gap: 18px;
}

.graph-workbench-toolbar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
}

.graph-controls,
.graph-stats,
.graph-type-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.graph-search {
  min-height: 44px;
  width: min(280px, 100%);
  border: 1px solid var(--border-default);
  padding: 0 14px;
}

.graph-toggle,
.graph-type-chip,
.graph-stage-tools button,
.graph-neighbor,
.graph-relation-row,
.graph-detail-close {
  min-height: 44px;
  border: 1px solid var(--border-default);
  padding: 0 12px;
  background: var(--surface-0);
}

.graph-type-chip[data-active="true"],
.graph-relation-row[data-active="true"] {
  border-color: var(--primary);
  color: var(--primary);
}

.graph-workbench-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(260px, 0.42fr);
  gap: 18px;
}

.graph-stage-tools {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 2;
  display: flex;
  gap: 8px;
}

.graph-inspector,
.graph-detail,
.graph-neighborhood,
.graph-relations {
  display: grid;
  gap: 12px;
}

@media (max-width: 980px) {
  .course-spatial-shell {
    grid-template-columns: 1fr;
  }

  .course-path-stage {
    min-height: auto;
  }

  .course-path-node,
  .course-path-node.is-active {
    position: relative;
    inset: auto;
    width: 100%;
    margin-bottom: 36px;
    transform: none;
  }

  .course-path-line {
    display: none;
  }

  .course-workbench {
    position: relative;
    top: auto;
    right: auto;
    width: 100%;
    grid-template-columns: 1fr;
    transform: none;
  }

  .graph-workbench-toolbar,
  .graph-workbench-grid {
    grid-template-columns: 1fr;
    display: grid;
  }
}

@media (prefers-reduced-motion: reduce) {
  .course-path-node,
  .course-workbench {
    transition: opacity var(--dur-1) ease;
    transform: none;
  }
}
```

- [ ] **Step 3: Run tests and build**

Run:

```bash
cd frontend && npm test -- graphTransform.test.js course-workspace.test.js courseViewState.test.js
cd frontend && npm run build
```

Expected: all listed tests pass and build succeeds.

- [ ] **Step 4: Run visual verification**

Start or reuse the frontend/backend dev services. Then capture desktop and mobile screenshots for `/courses/ai-intro`.

Use the existing approved visual check script if it still matches the page:

```bash
python3 tmp_visual_check.py
```

Expected:

- Desktop: no text overlap, course path visible, selected chapter workbench readable.
- Mobile: vertical chapter journey, workbench below active chapter, no horizontal overflow.
- Graph: nonblank SVG with selectable nodes and readable inspector.

- [ ] **Step 5: Commit**

Run:

```bash
git add frontend/src/components/GraphPanel.vue frontend/src/styles/app.css
git commit -m "feat: integrate spatial course graph"
```
