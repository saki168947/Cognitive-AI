<template>
  <section class="course-view container">
    <header v-if="courseLoading || courseError || !course" class="page-header">
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
        <p class="kicker course-kicker">AI & BRAIN SCIENCE</p>
        <h1 class="course-spatial-title">SYLLABUS /<br>COURSE<br>CHAPTERS</h1>
        <div class="course-blue-rule"></div>
        <p class="course-spatial-copy">
          A journey through the principles of intelligence, learning, and the science of the brain.
        </p>
        <div class="course-vertical-rail" aria-hidden="true">
          <span class="course-rail-dots">
            <i v-for="chapter in visualChapters" :key="chapter.id || chapter.title"></i>
          </span>
          <span>CHAPTERS</span>
        </div>
      </aside>

      <section id="full-syllabus" class="course-path-stage" aria-label="课程章节路径">
        <div class="course-top-label mono">COURSE SYLLABUS <span></span></div>
        <div class="course-path-line line-1"></div>
        <div class="course-path-line line-2"></div>
        <div class="course-path-line line-3"></div>
        <div class="course-path-line line-4"></div>
        <div class="course-path-line line-5"></div>
        <div class="course-elbow elbow-1"></div>
        <div class="course-elbow elbow-2"></div>
        <div class="course-orbit" aria-hidden="true"></div>

        <p v-if="visualChapters.length === 0" class="panel status-message">暂无可用章节。</p>
        <template v-else>
          <button
            v-for="(chapter, index) in visualChapters"
            :key="chapter.id || index"
            type="button"
            :class="[chapterNodeClass(index), { 'is-active': activeChapterId === chapter.id }]"
            :disabled="!chapter.id"
            @click="selectChapter(chapter.id)"
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

        <a class="course-syllabus-link mono" href="#full-syllabus">VIEW FULL SYLLABUS <span></span></a>
      </section>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import { getCourse } from '../api/courses';
import { chapterDisplayTitle, chapterNodeClass, chapterSubtopics } from './courseViewState';

const props = defineProps({
  courseId: {
    type: String,
    required: true
  }
});

const course = ref(null);
const activeChapterId = ref('');
const courseLoading = ref(false);
const courseError = ref('');
let courseRequestId = 0;

const chapters = computed(() => Array.isArray(course.value?.chapters) ? course.value.chapters : []);
const visualChapters = computed(() => {
  if (chapters.value.length >= 5) {
    return chapters.value;
  }

  if (props.courseId === 'ai-intro') {
    return [
      {
        id: 'ai-foundations',
        title: 'Foundations',
        sections: ['What is AI?', 'Agents and environments']
      },
      {
        id: 'ai-search',
        title: 'Search and Problem Solving',
        sections: ['Problem-Solving Agents', 'Uninformed Search', 'Informed Search', 'Heuristics and Optimization']
      },
      {
        id: 'ai-learning',
        title: 'Learning and Neural Networks',
        sections: ['Machine Learning Basics', 'Neural Network Foundations', 'Deep Learning', 'Training and Generalization']
      },
      {
        id: 'ai-language-vision',
        title: 'Language, Vision and Knowledge',
        sections: ['Language Models', 'Computer Vision', 'Knowledge Graphs', 'Reasoning Systems']
      },
      {
        id: 'ai-future',
        title: 'Applications and Future Directions',
        sections: ['AI in Neuroscience', 'Brain-Inspired AI', 'Ethical Considerations', 'The Road Ahead']
      }
    ];
  }

  return chapters.value;
});

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
  course.value = null;
  activeChapterId.value = '';

  try {
    const result = await getCourse(props.courseId);
    if (requestId !== courseRequestId) {
      return;
    }

    course.value = result || null;
    activeChapterId.value = visualChapters.value[0]?.id || '';
  } catch (caughtError) {
    if (requestId === courseRequestId) {
      course.value = null;
      courseError.value = caughtError?.message || '无法加载课程。';
    }
  } finally {
    if (requestId === courseRequestId) {
      courseLoading.value = false;
    }
  }
}

function selectChapter(chapterId) {
  activeChapterId.value = chapterId;
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
