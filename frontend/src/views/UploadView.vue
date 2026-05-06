<template>
  <main class="upload-page">
    <MaterialUploadStudio
      :course-id="activeCourseId"
      @uploaded="onUploaded"
    />
  </main>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import MaterialUploadStudio from '../components/MaterialUploadStudio.vue';

const route = useRoute();

const activeCourseId = computed(() => {
  const v = route.query.course;
  return typeof v === 'string' ? v : 'ai-intro';
});

function onUploaded(job) {
  console.log('[Upload] material processed:', job);
}
</script>

<style scoped>
.upload-page {
  min-height: calc(100vh - var(--nav-height));
  background: var(--surface-0);
}
</style>
