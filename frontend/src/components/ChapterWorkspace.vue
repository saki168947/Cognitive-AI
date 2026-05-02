<template>
  <article class="panel chapter-workspace course-tool-panel">
    <header class="panel-header course-tool-header">
      <p class="kicker">Selected Chapter</p>
      <h2>{{ chapter.title || '未命名章节' }}</h2>
    </header>

    <section v-if="objectives.length" class="content-block">
      <h3>学习目标</h3>
      <ul class="clean-list objective-list">
        <li v-for="objective in objectives" :key="objective">{{ objective }}</li>
      </ul>
    </section>

    <section v-if="chapter.body" class="content-block">
      <h3>阅读材料</h3>
      <p class="chapter-body">{{ chapter.body }}</p>
    </section>

    <section v-if="quizItems.length" class="content-block">
      <h3>复习题</h3>
      <div class="quiz-list">
        <details v-for="item in quizItems" :key="item.id || item.prompt" class="quiz-item">
          <summary>{{ item.prompt }}</summary>
          <button type="button" class="btn btn-outline btn-sm" @click="$emit('select-question', item.prompt)">
            问导师
          </button>
          <dl class="quiz-details">
            <template v-if="item.answer">
              <dt>答案</dt>
              <dd>{{ item.answer }}</dd>
            </template>
            <template v-if="item.explanation">
              <dt>解释</dt>
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
