<template>
  <section class="view">
    <header class="view-header">
      <p class="view-kicker">Course</p>
      <h1 class="view-title">{{ course?.title || course?.name || courseId }}</h1>
      <p class="view-copy">{{ course?.summary || course?.description || 'Review course material and ask focused questions.' }}</p>
    </header>

    <div v-if="courseLoading" class="panel">
      <p class="status-message">Loading course...</p>
    </div>

    <div v-else-if="courseError" class="panel">
      <p class="status-message error">{{ courseError }}</p>
      <button type="button" class="button secondary" @click="loadCourse">Retry</button>
    </div>

    <div v-else-if="course" class="two-col course-layout">
      <aside class="panel chapter-sidebar">
        <header class="panel-header">
          <p class="eyebrow">Syllabus</p>
          <h2>Chapters</h2>
        </header>

        <p v-if="chapters.length === 0" class="status-message">No chapters are available.</p>
        <div v-else class="chapter-list">
          <button
            v-for="chapter in chapters"
            :key="chapter.id"
            type="button"
            class="chapter-button"
            :class="{ active: activeChapter?.id === chapter.id }"
            @click="loadChapter(chapter.id)"
          >
            {{ chapter.title || chapter.name || chapter.id }}
          </button>
        </div>
      </aside>

      <main class="workspace-stack">
        <div v-if="chapterLoading" class="panel">
          <p class="status-message">Loading chapter...</p>
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
          <p class="status-message">Select a chapter to begin.</p>
        </div>

        <AITutorPanel
          :course-id="courseId"
          :chapter-id="activeChapter?.id || ''"
          :initial-question="selectedQuestion"
        />
      </main>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue';
import { getChapter, getCourse } from '../api/courses';
import AITutorPanel from '../components/AITutorPanel.vue';
import ChapterWorkspace from '../components/ChapterWorkspace.vue';

const props = defineProps({
  courseId: {
    type: String,
    required: true
  }
});

const course = ref(null);
const activeChapter = ref(null);
const selectedQuestion = ref('');
const courseLoading = ref(false);
const chapterLoading = ref(false);
const courseError = ref('');
const chapterError = ref('');
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
  courseError.value = '';
  chapterError.value = '';
  course.value = null;
  activeChapter.value = null;
  selectedQuestion.value = '';
  chapterRequestId += 1;

  try {
    const result = await getCourse(props.courseId);
    if (requestId !== courseRequestId) {
      return;
    }

    course.value = result || null;
    const firstChapter = chapters.value[0];

    if (firstChapter?.id) {
      await loadChapter(firstChapter.id);
    }
  } catch (caughtError) {
    if (requestId === courseRequestId) {
      course.value = null;
      activeChapter.value = null;
      courseError.value = caughtError?.message || 'Unable to load course.';
    }
  } finally {
    if (requestId === courseRequestId) {
      courseLoading.value = false;
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
      chapterError.value = caughtError?.message || 'Unable to load chapter.';
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
