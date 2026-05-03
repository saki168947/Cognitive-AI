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
