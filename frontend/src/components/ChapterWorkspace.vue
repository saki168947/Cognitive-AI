<template>
  <article class="panel chapter-workspace">
    <header class="panel-header">
      <p class="eyebrow">Chapter</p>
      <h2>{{ chapter.title || 'Untitled chapter' }}</h2>
    </header>

    <section v-if="objectives.length" class="content-block">
      <h3>Objectives</h3>
      <ul class="clean-list objective-list">
        <li v-for="objective in objectives" :key="objective">{{ objective }}</li>
      </ul>
    </section>

    <section v-if="chapter.body" class="content-block">
      <h3>Reading</h3>
      <p class="chapter-body">{{ chapter.body }}</p>
    </section>

    <section v-if="quizItems.length" class="content-block">
      <h3>Review Questions</h3>
      <div class="quiz-list">
        <details v-for="item in quizItems" :key="item.id || item.prompt" class="quiz-item">
          <summary>{{ item.prompt }}</summary>
          <button type="button" class="button small" @click="$emit('select-question', item.prompt)">
            Ask tutor
          </button>
          <dl class="quiz-details">
            <template v-if="item.answer">
              <dt>Answer</dt>
              <dd>{{ item.answer }}</dd>
            </template>
            <template v-if="item.explanation">
              <dt>Explanation</dt>
              <dd>{{ item.explanation }}</dd>
            </template>
          </dl>
        </details>
      </div>
    </section>
  </article>
</template>

<script setup>
import { computed } from 'vue';
import { normalizeObjectives } from './chapterWorkspace';

const props = defineProps({
  chapter: {
    type: Object,
    required: true
  }
});

defineEmits(['select-question']);

const objectives = computed(() => normalizeObjectives(props.chapter.objectives));
const quizItems = computed(() => Array.isArray(props.chapter.quiz_items) ? props.chapter.quiz_items : []);
</script>
