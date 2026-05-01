<template>
  <aside class="panel tutor-panel">
    <header class="panel-header">
      <p class="eyebrow">AI tutor</p>
      <h2>Ask about this chapter</h2>
    </header>

    <form class="tutor-form" @submit.prevent="submitQuestion">
      <label class="field-label" for="tutor-question">Question</label>
      <textarea
        id="tutor-question"
        v-model="question"
        rows="6"
        placeholder="Ask a question about the current chapter"
      />
      <button type="submit" class="button" :disabled="isAskDisabled">
        {{ loading ? 'Asking...' : 'Ask' }}
      </button>
    </form>

    <p v-if="error" class="status-message error">{{ error }}</p>
    <p v-if="loading" class="status-message">Preparing answer...</p>

    <section v-if="hasTutorResult" class="tutor-answer">
      <p v-if="insufficientEvidence" class="status-message warning">
        The tutor could not find enough supporting evidence for a complete answer.
      </p>
      <template v-if="answer">
        <h3>Answer</h3>
        <p>{{ answer }}</p>
      </template>

      <div v-if="citations.length" class="citations">
        <h3>Citations</h3>
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
      error.value = caughtError?.message || 'Unable to ask the tutor.';
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
