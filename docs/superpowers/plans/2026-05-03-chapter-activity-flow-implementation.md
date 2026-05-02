# Chapter Activity Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a dedicated chapter activity flow route that turns a selected chapter into a sequential lecture/lab/experiment/quiz learning path.

**Architecture:** Keep the existing course syllabus canvas as the outer navigation layer and add a new Vue route for chapter-level learning. Put activity normalization, fallback synthesis, progress, and concept trace data in a tested state helper; keep the view and visual components focused on rendering and interaction.

**Tech Stack:** Vue 3, Vue Router, Vite, Vitest, existing Flask APIs for courses, chapters, activities, and graph data.

---

## File Structure

- Create `frontend/src/views/chapterActivityFlowState.js`: pure helpers for activity flow construction, chapter identity, route paths, progress, active details, and concept trace data.
- Create `frontend/src/views/chapterActivityFlowState.test.js`: Vitest coverage for all pure helpers used by the route.
- Create `frontend/src/components/ChapterConceptTrace.vue`: lightweight SVG concept trace driven by graph nodes and active activity concept IDs.
- Create `frontend/src/views/ChapterActivityFlowView.vue`: route view for `/courses/:courseId/chapters/:chapterId`; loads course, chapter, activities, and graph data; renders the editorial chapter activity flow.
- Modify `frontend/src/router/index.js`: register the chapter route.
- Modify `frontend/src/views/CourseView.vue`: navigate chapter node clicks to the new chapter route.
- Modify `frontend/src/styles/app.css`: add responsive editorial styles for the chapter flow route.

---

### Task 1: Chapter Activity Flow State Helpers

**Files:**
- Create: `frontend/src/views/chapterActivityFlowState.js`
- Create: `frontend/src/views/chapterActivityFlowState.test.js`

- [ ] **Step 1: Write the failing tests**

Create `frontend/src/views/chapterActivityFlowState.test.js`:

```js
import { describe, expect, it } from 'vitest';
import {
  ACTIVITY_FLOW_ORDER,
  buildActivityFlow,
  buildChapterActivityPath,
  buildChapterIdentity,
  buildConceptTrace,
  findActiveActivity,
  progressFromActivities
} from './chapterActivityFlowState';

describe('chapter activity flow state', () => {
  it('builds canonical activity flow with published activities and graceful fallback items', () => {
    const chapter = {
      id: 'ai-search',
      title: 'Search and Problem Solving',
      body: 'Search frames intelligence as finding paths.',
      quiz_items: [
        { id: 'quiz-1', prompt: 'What is a heuristic?', answer: 'An estimate.' }
      ]
    };
    const activities = [
      {
        id: 'activity-ai-search-lab',
        chapter_id: 'ai-search',
        title: 'Code Lab: Heuristic Search Sandbox',
        type: 'code_lab',
        summary: 'Compare search strategies.',
        status: 'published',
        provider: 'jupyterlite',
        estimated_minutes: 40,
        linked_concept_ids: ['concept-search']
      },
      {
        id: 'draft-activity',
        chapter_id: 'ai-search',
        title: 'Draft Deck',
        type: 'lecture_deck',
        status: 'draft'
      },
      {
        id: 'other-chapter',
        chapter_id: 'ai-learning',
        title: 'Other Lab',
        type: 'code_lab',
        status: 'published'
      }
    ];

    const flow = buildActivityFlow({ chapter, activities });

    expect(flow).toHaveLength(ACTIVITY_FLOW_ORDER.length);
    expect(flow.map((item) => item.type)).toEqual([
      'lecture_deck',
      'code_lab',
      'cognitive_experiment',
      'bci_dataset_lab',
      'quiz_reflection'
    ]);
    expect(flow[0]).toMatchObject({
      id: 'ai-search-lecture_deck-generated',
      source: 'generated',
      title: 'Lecture',
      status: 'available',
      estimated_minutes: 32
    });
    expect(flow[1]).toMatchObject({
      id: 'activity-ai-search-lab',
      source: 'activity',
      title: 'Code Lab: Heuristic Search Sandbox',
      status: 'published',
      estimated_minutes: 40,
      provider: 'jupyterlite'
    });
    expect(flow[4]).toMatchObject({
      source: 'quiz',
      title: 'Quiz / Reflection',
      summary: '1 review prompt available for this chapter.'
    });
  });

  it('builds chapter identity and route paths', () => {
    const course = { id: 'ai-intro', title: '人工智能导论', summary: 'Course summary' };
    const chapter = {
      id: 'ai-learning',
      title: 'Learning and Neural Networks',
      order: 3,
      body: 'Neural networks learn layered representations from data.'
    };

    expect(buildChapterActivityPath('ai-intro', 'ai-learning')).toBe('/courses/ai-intro/chapters/ai-learning');
    expect(buildChapterIdentity({ course, chapter, chapterIndex: 2 })).toEqual({
      courseLabel: 'AI INTRODUCTION',
      chapterNumber: '03',
      title: 'Learning and Neural Networks',
      description: 'Neural networks learn layered representations from data.',
      backPath: '/courses/ai-intro'
    });
  });

  it('computes progress and active activity details', () => {
    const flow = [
      { id: 'a', status: 'completed' },
      { id: 'b', status: 'published' },
      { id: 'c', status: 'available' },
      { id: 'd', status: 'locked' }
    ];

    expect(progressFromActivities(flow)).toBe(25);
    expect(findActiveActivity(flow, 'b')).toBe(flow[1]);
    expect(findActiveActivity(flow, 'missing')).toBe(flow[0]);
  });

  it('builds a concept trace from graph data and active activity concept ids', () => {
    const graph = {
      nodes: [
        { id: 'concept-search', label: 'Heuristic Search' },
        { id: 'concept-rl', label: 'Reinforcement Learning' },
        { id: 'concept-attention', label: 'Attention' }
      ],
      edges: [
        { id: 'edge-1', source: 'concept-search', target: 'concept-rl', relationship: 'PREREQUISITE_OF' },
        { id: 'edge-2', source: 'concept-rl', target: 'concept-attention', relationship: 'RELATED_TO' }
      ]
    };

    const trace = buildConceptTrace(graph, ['concept-search']);

    expect(trace.nodes).toHaveLength(3);
    expect(trace.nodes[0]).toMatchObject({ id: 'concept-search', label: 'Heuristic Search', active: true });
    expect(trace.edges).toEqual([
      { id: 'edge-1', source: 'concept-search', target: 'concept-rl', active: true },
      { id: 'edge-2', source: 'concept-rl', target: 'concept-attention', active: false }
    ]);
  });
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```bash
npm --prefix frontend run test -- chapterActivityFlowState.test.js
```

Expected: FAIL because `frontend/src/views/chapterActivityFlowState.js` does not exist.

- [ ] **Step 3: Implement the state helper**

Create `frontend/src/views/chapterActivityFlowState.js`:

```js
const COURSE_LABELS = {
  'ai-intro': 'AI INTRODUCTION',
  'brain-cog-intro': 'NEUROSCIENCE 101'
};

export const ACTIVITY_FLOW_ORDER = [
  {
    type: 'lecture_deck',
    title: 'Lecture',
    displayTitle: 'LECTURE',
    estimatedMinutes: 32,
    provider: 'course notes',
    summary: 'Open the guided lecture for this chapter.'
  },
  {
    type: 'code_lab',
    title: 'Code Lab',
    displayTitle: 'CODE LAB',
    estimatedMinutes: 45,
    provider: 'browser lab',
    summary: 'Practice the chapter idea in an executable lab.'
  },
  {
    type: 'cognitive_experiment',
    title: 'Cognitive Experiment',
    displayTitle: 'COGNITIVE EXPERIMENT',
    estimatedMinutes: 25,
    provider: 'browser experiment',
    summary: 'Run a short experiment and connect the result to the chapter.'
  },
  {
    type: 'bci_dataset_lab',
    title: 'Neuro / EEG Data Lab',
    displayTitle: 'NEURO / EEG DATA LAB',
    estimatedMinutes: 45,
    provider: 'data notebook',
    summary: 'Inspect neuroscience data linked to this chapter.'
  },
  {
    type: 'quiz_reflection',
    title: 'Quiz / Reflection',
    displayTitle: 'QUIZ / REFLECTION',
    estimatedMinutes: 15,
    provider: 'course check',
    summary: 'Check understanding and send questions to the tutor.'
  }
];

function safeArray(value) {
  return Array.isArray(value) ? value : [];
}

function firstText(value, fallback) {
  if (typeof value !== 'string') return fallback;
  const text = value.trim();
  return text.length > 0 ? text : fallback;
}

function chapterActivities(activities, chapterId) {
  return safeArray(activities).filter((activity) =>
    activity?.chapter_id === chapterId && activity.status === 'published'
  );
}

function quizItems(chapter) {
  return safeArray(chapter?.quiz_items);
}

function generatedActivity(chapter, definition) {
  const quizCount = quizItems(chapter).length;
  const isQuiz = definition.type === 'quiz_reflection';
  return {
    id: `${chapter?.id || 'chapter'}-${definition.type}-generated`,
    type: definition.type,
    title: definition.title,
    displayTitle: definition.displayTitle,
    summary: isQuiz && quizCount > 0
      ? `${quizCount} review prompt${quizCount === 1 ? '' : 's'} available for this chapter.`
      : definition.summary,
    status: isQuiz && quizCount === 0 ? 'available' : 'available',
    provider: definition.provider,
    estimated_minutes: definition.estimatedMinutes,
    linked_concept_ids: [],
    source: isQuiz && quizCount > 0 ? 'quiz' : 'generated',
    quiz_items: isQuiz ? quizItems(chapter) : []
  };
}

function normalizeActivity(activity, definition) {
  return {
    ...activity,
    type: activity.type || definition.type,
    title: firstText(activity.title, definition.title),
    displayTitle: definition.displayTitle,
    summary: firstText(activity.summary, definition.summary),
    status: activity.status || 'published',
    provider: firstText(activity.provider, definition.provider),
    estimated_minutes: activity.estimated_minutes || definition.estimatedMinutes,
    linked_concept_ids: safeArray(activity.linked_concept_ids),
    source: 'activity'
  };
}

export function buildActivityFlow({ chapter, activities }) {
  const published = chapterActivities(activities, chapter?.id);
  return ACTIVITY_FLOW_ORDER.map((definition) => {
    const match = published.find((activity) => activity.type === definition.type);
    return match ? normalizeActivity(match, definition) : generatedActivity(chapter, definition);
  });
}

export function buildChapterActivityPath(courseId, chapterId) {
  return `/courses/${courseId}/chapters/${chapterId}`;
}

export function buildChapterIdentity({ course, chapter, chapterIndex = 0 }) {
  const courseId = course?.id || chapter?.course_id || '';
  const chapterNumber = String(chapter?.order || chapterIndex + 1).padStart(2, '0');
  return {
    courseLabel: COURSE_LABELS[courseId] || firstText(course?.title, 'COURSE'),
    chapterNumber,
    title: firstText(chapter?.title, 'Untitled Chapter'),
    description: firstText(chapter?.body, firstText(course?.summary, 'Continue the chapter activity flow.')),
    backPath: `/courses/${courseId}`
  };
}

export function progressFromActivities(flow) {
  const items = safeArray(flow);
  if (items.length === 0) return 0;
  const completed = items.filter((item) => item.status === 'completed').length;
  return Math.round((completed / items.length) * 100);
}

export function findActiveActivity(flow, activeActivityId) {
  const items = safeArray(flow);
  return items.find((item) => item.id === activeActivityId) || items[0] || null;
}

export function buildConceptTrace(graph, activeConceptIds = []) {
  const activeSet = new Set(safeArray(activeConceptIds));
  const nodes = safeArray(graph?.nodes).slice(0, 7).map((node, index) => ({
    id: node.id,
    label: node.label || node.id,
    active: activeSet.has(node.id),
    x: 56 + (index % 3) * 72,
    y: 38 + index * 42
  }));
  const nodeIds = new Set(nodes.map((node) => node.id));
  const edges = safeArray(graph?.edges)
    .filter((edge) => nodeIds.has(edge.source) && nodeIds.has(edge.target))
    .slice(0, 8)
    .map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      active: activeSet.has(edge.source) || activeSet.has(edge.target)
    }));

  return { nodes, edges };
}
```

- [ ] **Step 4: Run the focused tests**

Run:

```bash
npm --prefix frontend run test -- chapterActivityFlowState.test.js
```

Expected: PASS for `chapterActivityFlowState.test.js`.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/chapterActivityFlowState.js frontend/src/views/chapterActivityFlowState.test.js
git commit -m "feat: add chapter activity flow state"
```

---

### Task 2: Route Wiring And Course Map Navigation

**Files:**
- Modify: `frontend/src/router/index.js`
- Modify: `frontend/src/views/CourseView.vue`
- Test: `frontend/src/views/chapterActivityFlowState.test.js`

- [ ] **Step 1: Extend the existing state test with route encoding coverage**

Add this assertion inside the `builds chapter identity and route paths` test in `frontend/src/views/chapterActivityFlowState.test.js`:

```js
expect(buildChapterActivityPath('brain-cog-intro', 'brain attention')).toBe('/courses/brain-cog-intro/chapters/brain%20attention');
```

- [ ] **Step 2: Update the helper to encode chapter ids**

Change `buildChapterActivityPath` in `frontend/src/views/chapterActivityFlowState.js`:

```js
export function buildChapterActivityPath(courseId, chapterId) {
  return `/courses/${courseId}/chapters/${encodeURIComponent(chapterId)}`;
}
```

- [ ] **Step 3: Run the focused test**

Run:

```bash
npm --prefix frontend run test -- chapterActivityFlowState.test.js
```

Expected: PASS with encoded chapter route coverage.

- [ ] **Step 4: Register the chapter route**

Modify `frontend/src/router/index.js`:

```js
import { createRouter, createWebHistory } from 'vue-router';
import DashboardView from '../views/DashboardView.vue';
import CourseView from '../views/CourseView.vue';
import ChapterActivityFlowView from '../views/ChapterActivityFlowView.vue';
import TeacherStudioView from '../views/TeacherStudioView.vue';

const routes = [
  {
    path: '/',
    name: 'dashboard',
    component: DashboardView
  },
  {
    path: '/courses/:courseId',
    name: 'course',
    component: CourseView,
    props: true
  },
  {
    path: '/courses/:courseId/chapters/:chapterId',
    name: 'chapter-activity-flow',
    component: ChapterActivityFlowView,
    props: true
  },
  {
    path: '/teacher',
    name: 'teacher',
    component: TeacherStudioView
  }
];

export default createRouter({
  history: createWebHistory(),
  routes
});
```

- [ ] **Step 5: Navigate chapter node clicks to the new route**

Modify the script block in `frontend/src/views/CourseView.vue`:

```js
import { computed, nextTick, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useWindowScroll, useWindowSize } from '@vueuse/core';
import { getCourse } from '../api/courses';
import { buildChapterActivityPath } from './chapterActivityFlowState';
import { chapterDisplayTitle, chapterNodeClass, chapterSubtopics } from './courseViewState';
import gsap from 'gsap';
```

Then add after props:

```js
const router = useRouter();
```

Replace `selectChapter` with:

```js
function selectChapter(chapterId) {
  if (!chapterId) return;
  router.push(buildChapterActivityPath(props.courseId, chapterId));
}
```

- [ ] **Step 6: Remove unreachable active-camera code from `CourseView.vue`**

Delete the `activeChapterId`, `resetCamera`, and node blur code paths that are only used by the old same-page selection behavior. Keep mouse parallax and SVG line animation.

- [ ] **Step 7: Build check route wiring**

Run:

```bash
npm --prefix frontend run build
```

Expected: PASS and Vite emits a production build without unresolved `ChapterActivityFlowView.vue` import once Task 4 creates the view. During this task, if the view has not been created yet, create a temporary route view with the exact content below and replace it in Task 4:

```vue
<template>
  <main class="chapter-flow-view container">
    <RouterLink :to="`/courses/${courseId}`">Back to course</RouterLink>
    <h1>{{ chapterId }}</h1>
  </main>
</template>

<script setup>
defineProps({
  courseId: {
    type: String,
    required: true
  },
  chapterId: {
    type: String,
    required: true
  }
});
</script>
```

- [ ] **Step 8: Commit**

```bash
git add frontend/src/router/index.js frontend/src/views/CourseView.vue frontend/src/views/ChapterActivityFlowView.vue frontend/src/views/chapterActivityFlowState.js frontend/src/views/chapterActivityFlowState.test.js
git commit -m "feat: route chapters to activity flow"
```

---

### Task 3: Concept Trace Component

**Files:**
- Create: `frontend/src/components/ChapterConceptTrace.vue`
- Test: `frontend/src/views/chapterActivityFlowState.test.js`

- [ ] **Step 1: Verify trace helper coverage exists**

Run:

```bash
npm --prefix frontend run test -- chapterActivityFlowState.test.js
```

Expected: PASS for the `builds a concept trace from graph data and active activity concept ids` test from Task 1.

- [ ] **Step 2: Create the component**

Create `frontend/src/components/ChapterConceptTrace.vue`:

```vue
<template>
  <aside class="chapter-concept-trace" aria-label="Chapter concept trace">
    <svg viewBox="0 0 260 420" role="img" aria-label="Concept relationships">
      <path
        v-for="edge in renderedEdges"
        :key="edge.id"
        :d="edge.path"
        :class="['concept-trace-edge', { 'is-active': edge.active }]"
      />
      <g
        v-for="node in nodes"
        :key="node.id"
        :class="['concept-trace-node', { 'is-active': node.active }]"
      >
        <circle :cx="node.x" :cy="node.y" :r="node.active ? 7 : 4" />
        <text :x="node.x + 12" :y="node.y + 4">{{ node.label }}</text>
      </g>
    </svg>
  </aside>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  trace: {
    type: Object,
    default: () => ({ nodes: [], edges: [] })
  }
});

const nodes = computed(() => Array.isArray(props.trace.nodes) ? props.trace.nodes : []);

const nodeMap = computed(() =>
  nodes.value.reduce((map, node) => {
    map.set(node.id, node);
    return map;
  }, new Map())
);

const renderedEdges = computed(() => {
  const edges = Array.isArray(props.trace.edges) ? props.trace.edges : [];
  return edges
    .map((edge) => {
      const source = nodeMap.value.get(edge.source);
      const target = nodeMap.value.get(edge.target);
      if (!source || !target) return null;
      const midX = (source.x + target.x) / 2 + 36;
      const midY = (source.y + target.y) / 2;
      return {
        ...edge,
        path: `M ${source.x} ${source.y} C ${midX} ${source.y}, ${midX} ${target.y}, ${target.x} ${target.y}`
      };
    })
    .filter(Boolean);
});
</script>
```

- [ ] **Step 3: Add build verification**

Run:

```bash
npm --prefix frontend run build
```

Expected: PASS with `ChapterConceptTrace.vue` compiled.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/ChapterConceptTrace.vue
git commit -m "feat: add chapter concept trace"
```

---

### Task 4: Chapter Activity Flow Route View

**Files:**
- Create or replace: `frontend/src/views/ChapterActivityFlowView.vue`
- Modify: `frontend/src/views/chapterActivityFlowState.js`
- Test: `frontend/src/views/chapterActivityFlowState.test.js`

- [ ] **Step 1: Add active detail copy coverage**

Append this test to `frontend/src/views/chapterActivityFlowState.test.js`:

```js
it('keeps launch copy concrete for each flow type', () => {
  const flow = buildActivityFlow({
    chapter: {
      id: 'brain-attention',
      title: 'Attention',
      quiz_items: [{ id: 'q1', prompt: 'How does attention select information?' }]
    },
    activities: []
  });

  expect(flow.map((item) => item.launchLabel)).toEqual([
    'Open lecture',
    'Open lab',
    'Start experiment',
    'Open data lab',
    'Start check'
  ]);
});
```

- [ ] **Step 2: Add `launchLabel` to generated and normalized activities**

Add `launchLabel` to each item in `ACTIVITY_FLOW_ORDER` in `frontend/src/views/chapterActivityFlowState.js`:

```js
launchLabel: 'Open lecture'
```

Use these values by type:

- `lecture_deck`: `Open lecture`
- `code_lab`: `Open lab`
- `cognitive_experiment`: `Start experiment`
- `bci_dataset_lab`: `Open data lab`
- `quiz_reflection`: `Start check`

Then add this field in both `generatedActivity` and `normalizeActivity`:

```js
launchLabel: definition.launchLabel,
```

- [ ] **Step 3: Run the focused tests**

Run:

```bash
npm --prefix frontend run test -- chapterActivityFlowState.test.js
```

Expected: PASS and launch labels are stable.

- [ ] **Step 4: Create the full route view**

Create or replace `frontend/src/views/ChapterActivityFlowView.vue`:

```vue
<template>
  <main class="chapter-flow-view">
    <div v-if="loading" class="chapter-flow-status container">
      <p class="status-message">正在加载章节活动流...</p>
    </div>

    <div v-else-if="error" class="chapter-flow-status container">
      <p class="status-message error">{{ error }}</p>
      <button type="button" class="btn btn-outline" @click="loadChapterFlow">重试</button>
    </div>

    <section v-else class="chapter-flow-shell container">
      <aside class="chapter-flow-identity">
        <RouterLink :to="identity.backPath" class="chapter-flow-back mono">← COURSE MAP</RouterLink>
        <p class="chapter-flow-course mono">{{ identity.courseLabel }}</p>
        <p class="chapter-flow-kicker mono">CHAPTER {{ identity.chapterNumber }}</p>
        <h1>{{ identity.title }}</h1>
        <div class="chapter-flow-rule"></div>
        <p class="chapter-flow-description">{{ identity.description }}</p>
        <div class="chapter-flow-progress" aria-label="Chapter progress">
          <div class="chapter-flow-progress-head mono">
            <span>CHAPTER PROGRESS</span>
            <span>{{ progress }}%</span>
          </div>
          <div class="chapter-flow-progress-track">
            <span :style="{ width: `${progress}%` }"></span>
          </div>
        </div>
      </aside>

      <section class="chapter-flow-main" aria-label="Chapter activities">
        <button
          v-for="(activity, index) in flow"
          :key="activity.id"
          type="button"
          :class="['chapter-flow-step', { 'is-active': activeActivity?.id === activity.id }]"
          @click="activeActivityId = activity.id"
        >
          <span class="chapter-flow-step-number">{{ String(index + 1).padStart(2, '0') }}</span>
          <span class="chapter-flow-step-line" aria-hidden="true"></span>
          <span class="chapter-flow-step-copy">
            <span class="chapter-flow-step-title">{{ activity.displayTitle }}</span>
            <span class="chapter-flow-step-meta mono">{{ activity.estimated_minutes }} MIN / {{ activity.provider }}</span>
            <span class="chapter-flow-step-summary">{{ activity.summary }}</span>
          </span>
          <span class="chapter-flow-step-launch" aria-hidden="true">→</span>
        </button>

        <article v-if="activeActivity" class="chapter-flow-detail">
          <p class="chapter-flow-detail-label mono">ACTIVE ACTIVITY</p>
          <h2>{{ activeActivity.title }}</h2>
          <p>{{ activeActivity.summary }}</p>
          <dl>
            <div>
              <dt>Type</dt>
              <dd>{{ activeActivity.displayTitle }}</dd>
            </div>
            <div>
              <dt>Duration</dt>
              <dd>{{ activeActivity.estimated_minutes }} min</dd>
            </div>
            <div>
              <dt>Source</dt>
              <dd>{{ activeActivity.source }}</dd>
            </div>
          </dl>
          <button type="button" class="chapter-flow-primary">{{ activeActivity.launchLabel }}</button>
        </article>
      </section>

      <ChapterConceptTrace :trace="conceptTrace" />
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import { RouterLink } from 'vue-router';
import { listCourseActivities } from '../api/activities';
import { getChapter, getCourse } from '../api/courses';
import { getGraph } from '../api/graph';
import ChapterConceptTrace from '../components/ChapterConceptTrace.vue';
import {
  buildActivityFlow,
  buildChapterIdentity,
  buildConceptTrace,
  findActiveActivity,
  progressFromActivities
} from './chapterActivityFlowState';

const props = defineProps({
  courseId: {
    type: String,
    required: true
  },
  chapterId: {
    type: String,
    required: true
  }
});

const loading = ref(false);
const error = ref('');
const course = ref(null);
const chapter = ref(null);
const activities = ref([]);
const graph = ref({ nodes: [], edges: [] });
const activeActivityId = ref('');

const chapterIndex = computed(() =>
  (course.value?.chapters || []).findIndex((item) => item.id === props.chapterId)
);

const flow = computed(() => buildActivityFlow({
  chapter: chapter.value,
  activities: activities.value
}));

const activeActivity = computed(() => findActiveActivity(flow.value, activeActivityId.value));
const progress = computed(() => progressFromActivities(flow.value));
const identity = computed(() => buildChapterIdentity({
  course: course.value,
  chapter: chapter.value,
  chapterIndex: chapterIndex.value >= 0 ? chapterIndex.value : 0
}));

const conceptTrace = computed(() =>
  buildConceptTrace(graph.value, activeActivity.value?.linked_concept_ids || [])
);

async function loadChapterFlow() {
  loading.value = true;
  error.value = '';

  try {
    const [courseResult, chapterResult, activityResult, graphResult] = await Promise.all([
      getCourse(props.courseId),
      getChapter(props.chapterId),
      listCourseActivities(props.courseId),
      getGraph(props.courseId)
    ]);

    course.value = courseResult;
    chapter.value = chapterResult;
    activities.value = activityResult;
    graph.value = graphResult || { nodes: [], edges: [] };
    activeActivityId.value = '';
  } catch (caughtError) {
    error.value = caughtError?.message || '章节活动流加载失败。';
  } finally {
    loading.value = false;
  }
}

watch(
  () => [props.courseId, props.chapterId],
  () => {
    loadChapterFlow();
  }
);

onMounted(loadChapterFlow);
</script>
```

- [ ] **Step 5: Run tests and build**

Run:

```bash
npm --prefix frontend run test -- chapterActivityFlowState.test.js
npm --prefix frontend run build
```

Expected: PASS for the state tests and Vite build.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/views/ChapterActivityFlowView.vue frontend/src/views/chapterActivityFlowState.js frontend/src/views/chapterActivityFlowState.test.js
git commit -m "feat: build chapter activity flow view"
```

---

### Task 5: Editorial Responsive Styling

**Files:**
- Modify: `frontend/src/styles/app.css`
- Test: build and browser visual check

- [ ] **Step 1: Add desktop and mobile styles**

Append to `frontend/src/styles/app.css`:

```css
.chapter-flow-view {
  min-height: 100vh;
  padding-top: var(--nav-height);
  background: var(--surface-0);
  color: var(--text-1);
}

.chapter-flow-status {
  padding-top: 96px;
}

.chapter-flow-shell {
  display: grid;
  grid-template-columns: minmax(260px, 0.82fr) minmax(420px, 1.18fr) minmax(180px, 0.58fr);
  gap: clamp(36px, 5vw, 80px);
  min-height: calc(100vh - var(--nav-height));
  padding-top: clamp(64px, 8vw, 118px);
  padding-bottom: 72px;
}

.chapter-flow-identity {
  position: sticky;
  top: calc(var(--nav-height) + 44px);
  align-self: start;
  min-width: 0;
}

.chapter-flow-back,
.chapter-flow-course,
.chapter-flow-kicker,
.chapter-flow-detail-label,
.chapter-flow-progress-head,
.chapter-flow-step-meta {
  letter-spacing: 0.24em;
  text-transform: uppercase;
}

.chapter-flow-back {
  display: inline-flex;
  min-height: 44px;
  align-items: center;
  color: var(--text-2);
  font-size: 0.72rem;
  font-weight: 800;
}

.chapter-flow-course {
  margin: 0 0 clamp(120px, 16vh, 210px);
  color: var(--text-1);
  font-size: 0.74rem;
  font-weight: 850;
}

.chapter-flow-kicker {
  margin: 0 0 24px;
  color: var(--text-1);
  font-size: 0.78rem;
  font-weight: 850;
}

.chapter-flow-identity h1 {
  max-width: 9ch;
  margin: 0;
  color: var(--text-1);
  font-size: clamp(3.4rem, 5.7vw, 6.5rem);
  line-height: 0.95;
  letter-spacing: 0;
}

.chapter-flow-rule {
  width: 42px;
  height: 3px;
  margin: 36px 0 28px;
  background: var(--text-1);
}

.chapter-flow-description {
  max-width: 30ch;
  margin: 0;
  color: var(--text-3);
  font-size: 1rem;
  line-height: 1.75;
}

.chapter-flow-progress {
  margin-top: clamp(80px, 14vh, 180px);
}

.chapter-flow-progress-head {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 14px;
  color: var(--text-2);
  font-size: 0.68rem;
  font-weight: 850;
}

.chapter-flow-progress-track {
  height: 3px;
  background: rgba(17, 24, 39, 0.12);
}

.chapter-flow-progress-track span {
  display: block;
  height: 100%;
  background: var(--text-1);
}

.chapter-flow-main {
  display: grid;
  gap: clamp(32px, 5vh, 64px);
  align-content: start;
}

.chapter-flow-step {
  position: relative;
  display: grid;
  grid-template-columns: minmax(150px, 0.72fr) minmax(72px, 0.25fr) minmax(220px, 1fr) 52px;
  align-items: center;
  width: 100%;
  min-height: 142px;
  padding: 0;
  border: 0;
  background: transparent;
  color: inherit;
  text-align: left;
  cursor: pointer;
}

.chapter-flow-step:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 8px;
}

.chapter-flow-step-number {
  color: rgba(17, 24, 39, 0.1);
  font-size: clamp(5.5rem, 11vw, 9.5rem);
  font-weight: 250;
  line-height: 0.85;
}

.chapter-flow-step-line {
  position: relative;
  height: 1px;
  background: rgba(17, 24, 39, 0.35);
}

.chapter-flow-step-line::before {
  content: "";
  position: absolute;
  left: -5px;
  top: -5px;
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background: var(--text-1);
}

.chapter-flow-step-copy {
  display: grid;
  gap: 12px;
  min-width: 0;
}

.chapter-flow-step-title {
  color: var(--text-1);
  font-size: clamp(1.5rem, 2.25vw, 2.45rem);
  font-weight: 900;
  letter-spacing: 0.22em;
  line-height: 1.15;
}

.chapter-flow-step-meta {
  color: var(--text-3);
  font-size: 0.75rem;
  font-weight: 800;
}

.chapter-flow-step-summary {
  max-width: 42ch;
  color: var(--text-3);
  font-size: 0.92rem;
  line-height: 1.55;
}

.chapter-flow-step-launch {
  display: inline-grid;
  width: 46px;
  height: 46px;
  place-items: center;
  border: 1px solid rgba(17, 24, 39, 0.4);
  border-radius: 50%;
  color: var(--text-1);
  font-size: 1.5rem;
}

.chapter-flow-step.is-active .chapter-flow-step-number,
.chapter-flow-step:hover .chapter-flow-step-number {
  color: rgba(0, 87, 255, 0.14);
}

.chapter-flow-step.is-active .chapter-flow-step-line,
.chapter-flow-step:hover .chapter-flow-step-line {
  background: var(--primary);
}

.chapter-flow-step.is-active .chapter-flow-step-line::before,
.chapter-flow-step:hover .chapter-flow-step-line::before {
  background: var(--primary);
}

.chapter-flow-detail {
  margin-top: 10px;
  padding: 28px 0 0;
  border-top: 1px solid rgba(17, 24, 39, 0.18);
}

.chapter-flow-detail-label {
  margin: 0 0 14px;
  color: var(--primary);
  font-size: 0.68rem;
  font-weight: 850;
}

.chapter-flow-detail h2 {
  margin: 0 0 12px;
  color: var(--text-1);
  font-size: 1.45rem;
}

.chapter-flow-detail p {
  max-width: 58ch;
  margin: 0;
  color: var(--text-3);
  line-height: 1.65;
}

.chapter-flow-detail dl {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  margin: 22px 0;
}

.chapter-flow-detail dt {
  color: var(--text-4);
  font-size: 0.72rem;
  font-weight: 850;
  text-transform: uppercase;
}

.chapter-flow-detail dd {
  margin: 4px 0 0;
  color: var(--text-2);
}

.chapter-flow-primary {
  min-height: 44px;
  padding: 0 18px;
  border: 1px solid var(--text-1);
  background: var(--text-1);
  color: var(--surface-0);
  font-weight: 850;
}

.chapter-concept-trace {
  min-width: 0;
  opacity: 0.9;
}

.chapter-concept-trace svg {
  width: 100%;
  max-width: 280px;
  height: min(56vh, 520px);
  overflow: visible;
}

.concept-trace-edge {
  fill: none;
  stroke: rgba(17, 24, 39, 0.22);
  stroke-width: 1;
}

.concept-trace-edge.is-active {
  stroke: var(--primary);
  stroke-width: 1.5;
}

.concept-trace-node circle {
  fill: var(--text-1);
}

.concept-trace-node.is-active circle {
  fill: var(--primary);
}

.concept-trace-node text {
  fill: var(--text-3);
  font-size: 10px;
  font-weight: 700;
}

@media (prefers-reduced-motion: reduce) {
  .chapter-flow-step,
  .chapter-flow-step * {
    transition: none;
  }
}

@media (max-width: 1024px) {
  .chapter-flow-shell {
    grid-template-columns: minmax(0, 1fr);
    gap: 48px;
  }

  .chapter-flow-identity {
    position: static;
  }

  .chapter-flow-course {
    margin-bottom: 64px;
  }

  .chapter-flow-identity h1 {
    max-width: 12ch;
  }

  .chapter-flow-progress {
    margin-top: 44px;
  }

  .chapter-concept-trace {
    order: 3;
  }
}

@media (max-width: 680px) {
  .chapter-flow-shell {
    padding-top: 44px;
  }

  .chapter-flow-step {
    grid-template-columns: 94px minmax(0, 1fr) 48px;
    gap: 14px;
    min-height: 116px;
  }

  .chapter-flow-step-line {
    display: none;
  }

  .chapter-flow-step-number {
    font-size: 4.4rem;
  }

  .chapter-flow-step-title {
    font-size: 1.28rem;
    letter-spacing: 0.16em;
  }

  .chapter-flow-step-summary {
    display: none;
  }

  .chapter-flow-step-launch {
    width: 44px;
    height: 44px;
  }

  .chapter-concept-trace svg {
    height: 220px;
  }
}
```

- [ ] **Step 2: Run build verification**

Run:

```bash
npm --prefix frontend run build
```

Expected: PASS with no CSS syntax errors.

- [ ] **Step 3: Start the dev server for visual verification**

Run:

```bash
npm --prefix frontend run dev -- --port 5173
```

Expected: Vite serves the app at `http://localhost:5173/`. Keep the server running for Task 6.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/styles/app.css
git commit -m "style: add chapter activity flow layout"
```

---

### Task 6: Verification And Visual Checks

**Files:**
- Verify: `frontend/src/views/ChapterActivityFlowView.vue`
- Verify: `frontend/src/styles/app.css`
- Verify: browser route `/courses/ai-intro/chapters/ai-search`

- [ ] **Step 1: Run the full frontend test suite**

Run:

```bash
npm --prefix frontend run test
```

Expected: PASS for all Vitest suites.

- [ ] **Step 2: Run the production build**

Run:

```bash
npm --prefix frontend run build
```

Expected: PASS and Vite emits `frontend/dist`.

- [ ] **Step 3: Open direct chapter route**

Open:

```text
http://localhost:5173/courses/ai-intro/chapters/ai-search
```

Expected visible content:

- Left identity area shows `AI INTRODUCTION`.
- Chapter label shows `CHAPTER 01` for `ai-search` based on the current seed order.
- Center flow shows `LECTURE`, `CODE LAB`, `COGNITIVE EXPERIMENT`, `NEURO / EEG DATA LAB`, and `QUIZ / REFLECTION`.
- `CODE LAB` uses the published `Code Lab: Heuristic Search Sandbox` activity.
- Right concept trace renders at least one concept dot when graph data is available.

- [ ] **Step 4: Click flow activities**

In the browser:

- Click `CODE LAB`.
- Click `QUIZ / REFLECTION`.

Expected:

- The active number tint changes to Klein blue.
- The detail section title and metadata change without route navigation.
- No text overlaps the launch button.

- [ ] **Step 5: Check mobile width**

Open browser devtools or use a Playwright/browser viewport at 390px wide:

```text
http://localhost:5173/courses/ai-intro/chapters/ai-search
```

Expected:

- Page uses one column.
- Activity rows remain tappable.
- No horizontal scrolling.
- Launch circles are not clipped.
- Concept trace appears below the flow or as a compact strip.

- [ ] **Step 6: Verify course map navigation**

Open:

```text
http://localhost:5173/courses/ai-intro
```

Click the `Search and Problem Solving` chapter node.

Expected: Browser navigates to:

```text
/courses/ai-intro/chapters/ai-search
```

- [ ] **Step 7: Commit verification-only fixes if needed**

If verification reveals concrete defects, fix only the affected files and commit:

```bash
git add frontend/src/views/ChapterActivityFlowView.vue frontend/src/styles/app.css frontend/src/views/CourseView.vue
git commit -m "fix: polish chapter activity flow verification"
```

If verification passes without code changes, do not create an empty commit.

---

## Self-Review Checklist

- Spec coverage: The plan implements the new chapter route, left identity zone, center activity storyline, right concept trace, activity detail selection, fallback sequence, back navigation, focus states, responsive behavior, and build/visual verification.
- Scope control: The plan does not add real code execution, jsPsych runtime, EEG hardware, gradebook, user progress persistence, or teacher authoring changes.
- Data consistency: The plan uses existing API wrappers and backend fields: `Course`, `Chapter`, `LearningActivity`, `Concept`, `GraphEdge`, `QuizItem`, `type`, `chapter_id`, `linked_concept_ids`, and `estimated_minutes`.
- Test strategy: Pure activity-flow behavior is covered by Vitest; route and visual behavior are verified by build and browser checks.
