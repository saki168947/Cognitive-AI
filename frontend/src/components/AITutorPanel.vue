<template>
  <aside class="panel tutor-panel course-tool-panel">
    <header class="panel-header course-tool-header">
      <p class="kicker">AI Tutor</p>
      <h2>就本章内容提问</h2>
    </header>

    <form class="tutor-form" @submit.prevent="submitQuestion">
      <label class="field-label" for="tutor-question">问题</label>
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
    </form>

    <p v-if="error" class="status-message error">{{ error }}</p>
    <p v-if="loading" class="status-message">正在准备回答…</p>

    <section v-if="hasTutorResult" class="tutor-answer">
      <p v-if="insufficientEvidence" class="status-message warning">
        导师未能找到足够的支撑证据来给出完整回答。
      </p>
      <template v-if="answer">
        <h3>回答</h3>
        <p>{{ answer }}</p>
      </template>

      <div v-if="citations.length" class="citations">
        <h3>引用来源</h3>
        <ul class="clean-list">
          <li v-for="citation in citations" :key="citationKey(citation)">
            {{ citationText(citation) }}
          </li>
        </ul>
      </div>
    </section>
  </aside>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import { askTutor } from '../api/tutor';
import { createRequestSequence } from './tutorState';

const props = defineProps({
  courseId: {
    type: String,
    required: true
  },
  chapterId: {
    type: String,
    default: ''
  },
  initialQuestion: {
    type: String,
    default: ''
  }
});

const question = ref(props.initialQuestion);
const loading = ref(false);
const error = ref('');
const answer = ref('');
const citations = ref([]);
const insufficientEvidence = ref(false);
const requestSequence = createRequestSequence();

const isAskDisabled = computed(() => loading.value || question.value.trim().length === 0);
const hasTutorResult = computed(() => Boolean(answer.value || insufficientEvidence.value || citations.value.length));

watch(
  () => props.initialQuestion,
  (nextQuestion) => {
    if (nextQuestion !== undefined && nextQuestion !== question.value) {
      question.value = nextQuestion;
    }
  }
);

watch(
  () => [props.courseId, props.chapterId],
  () => {
    requestSequence.invalidate();
    loading.value = false;
    error.value = '';
    answer.value = '';
    citations.value = [];
    insufficientEvidence.value = false;
  }
);

async function submitQuestion() {
  if (isAskDisabled.value) {
    return;
  }

  loading.value = true;
  error.value = '';
  answer.value = '';
  citations.value = [];
  insufficientEvidence.value = false;
  const requestId = requestSequence.next();

  try {
    const result = await askTutor({
      question: question.value.trim(),
      course_id: props.courseId,
      chapter_id: props.chapterId || undefined
    });
    if (!requestSequence.isCurrent(requestId)) {
      return;
    }

    answer.value = result?.answer || '';
    citations.value = Array.isArray(result?.citations) ? result.citations : [];
    insufficientEvidence.value = Boolean(result?.insufficient_evidence || result?.insufficientEvidence);
  } catch (caughtError) {
    if (requestSequence.isCurrent(requestId)) {
      error.value = caughtError?.message || '无法向导师提问。';
    }
  } finally {
    if (requestSequence.isCurrent(requestId)) {
      loading.value = false;
    }
  }
}

function citationText(citation) {
  if (typeof citation === 'string') {
    return citation;
  }

  return citation?.title || citation?.source || citation?.text || JSON.stringify(citation);
}

function citationKey(citation) {
  return typeof citation === 'string' ? citation : citationText(citation);
}
</script>
