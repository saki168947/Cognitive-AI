<template>
  <section class="course-view container">
    <header class="page-header">
      <div class="indicator mono">
        <div class="dot"></div>
        COURSE VIEW
      </div>
      <h1 class="display">{{ course?.title || course?.name || courseId }}</h1>
      <div class="separator"></div>
      <p class="desc">{{ course?.summary || course?.description || '查看课程材料并提出针对性问题。' }}</p>
    </header>

    <div v-if="courseLoading" class="panel">
      <p class="status-message">正在加载课程…</p>
    </div>

    <div v-else-if="courseError" class="panel">
      <p class="status-message error">{{ courseError }}</p>
      <button type="button" class="btn btn-outline" @click="loadCourse">重试</button>
    </div>

    <div v-else-if="course" class="course-spatial-shell">
      <aside class="course-spatial-intro">
        <p class="kicker course-kicker">COURSE SYLLABUS</p>
        <h1 class="course-spatial-title">{{ course?.title || course?.name || courseId }}</h1>
        <div class="course-blue-rule"></div>
        <p class="course-spatial-copy">
          {{ course?.summary || course?.description || '沿着章节路径进入阅读、AI 导师、知识图谱与复习任务。' }}
        </p>
        <div class="course-vertical-rail" aria-hidden="true">
          <span class="course-rail-dots">
            <i v-for="chapter in chapters" :key="chapter.id || chapter.title"></i>
          </span>
          <span>CHAPTERS</span>
        </div>
      </aside>

      <section class="course-path-stage" aria-label="课程章节路径">
        <div class="course-path-line line-1"></div>
        <div class="course-path-line line-2"></div>
        <div class="course-path-line line-3"></div>
        <div class="course-path-line line-4"></div>

        <p v-if="chapters.length === 0" class="panel status-message">暂无可用章节。</p>
        <template v-else>
          <button
            v-for="(chapter, index) in chapters"
            :key="chapter.id || index"
            type="button"
            :class="[chapterNodeClass(index), { 'is-active': activeChapter?.id === chapter.id }]"
            :disabled="!chapter.id"
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
        </template>

        <main class="course-workbench">
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
        </main>
      </section>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue';
import { getChapter, getCourse } from '../api/courses';
import { getGraph } from '../api/graph';
import AITutorPanel from '../components/AITutorPanel.vue';
import ChapterWorkspace from '../components/ChapterWorkspace.vue';
import GraphPanel from '../components/GraphPanel.vue';
import { chapterDisplayTitle, chapterNodeClass, chapterSubtopics } from './courseViewState';

const props = defineProps({
  courseId: {
    type: String,
    required: true
  }
});

const course = ref(null);
const activeChapter = ref(null);
const graph = ref({ nodes: [], edges: [] });
const selectedQuestion = ref('');
const courseLoading = ref(false);
const chapterLoading = ref(false);
const graphLoading = ref(false);
const courseError = ref('');
const chapterError = ref('');
const graphError = ref('');
let chapterRequestId = 0;
let courseRequestId = 0;

const chapters = computed(() => Array.isArray(course.value?.chapters) ? course.value.chapters : []);

onMounted(loadCourse);

watch(
  () => props.courseId,
  () => {
    loadCourse();
  }
);

async function loadCourse() {
  const requestId = courseRequestId + 1;
  courseRequestId = requestId;
  courseLoading.value = true;
  graphLoading.value = true;
  courseError.value = '';
  chapterError.value = '';
  graphError.value = '';
  course.value = null;
  activeChapter.value = null;
  graph.value = { nodes: [], edges: [] };
  selectedQuestion.value = '';
  chapterRequestId += 1;

  try {
    const [courseResult, graphResult] = await Promise.allSettled([
      getCourse(props.courseId),
      getGraph(props.courseId)
    ]);
    if (requestId !== courseRequestId) {
      return;
    }

    if (graphResult.status === 'fulfilled') {
      graph.value = graphResult.value || { nodes: [], edges: [] };
    } else {
      graph.value = { nodes: [], edges: [] };
      graphError.value = graphResult.reason?.message || '无法加载知识图谱。';
    }
    graphLoading.value = false;

    if (courseResult.status === 'rejected') {
      throw courseResult.reason;
    }

    course.value = courseResult.value || null;
    const firstChapter = chapters.value[0];

    if (firstChapter?.id) {
      await loadChapter(firstChapter.id);
    }
  } catch (caughtError) {
    if (requestId === courseRequestId) {
      course.value = null;
      activeChapter.value = null;
      graph.value = { nodes: [], edges: [] };
      courseError.value = caughtError?.message || '无法加载课程。';
    }
  } finally {
    if (requestId === courseRequestId) {
      courseLoading.value = false;
      graphLoading.value = false;
    }
  }
}

async function loadChapter(chapterId) {
  const requestId = chapterRequestId + 1;
  chapterRequestId = requestId;
  chapterLoading.value = true;
  chapterError.value = '';
  activeChapter.value = null;
  selectedQuestion.value = '';

  try {
    const result = await getChapter(chapterId);
    if (requestId === chapterRequestId) {
      activeChapter.value = result || null;
    }
  } catch (caughtError) {
    if (requestId === chapterRequestId) {
      activeChapter.value = null;
      chapterError.value = caughtError?.message || '无法加载章节。';
    }
  } finally {
    if (requestId === chapterRequestId) {
      chapterLoading.value = false;
    }
  }
}

async function selectTutorQuestion(question) {
  selectedQuestion.value = '';
  await nextTick();
  selectedQuestion.value = question;
}
</script>

<style scoped>
.course-view {
  padding-top: calc(var(--nav-height) + 60px);
  padding-bottom: 100px;
}

.page-header {
  margin-bottom: 60px;
}

.indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 24px;
}

.indicator .dot {
  width: 6px;
  height: 6px;
  background: var(--primary);
  border-radius: 50%;
}

.page-header h1 {
  font-size: 2.5rem;
  color: var(--text-1);
  margin-bottom: 24px;
}

.separator {
  width: 40px;
  height: 2px;
  background: var(--text-1);
  margin-bottom: 24px;
}

.desc {
  color: var(--text-3);
  font-size: 14px;
  line-height: 1.8;
  max-width: 600px;
}

.course-layout {
  align-items: start;
}
</style>
