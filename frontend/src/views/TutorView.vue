<template>
  <main class="tutor-page">
    <div class="tutor-page-shell">
      <AITutorPanel
        :course-id="activeCourseId"
        :chapter-id="activeChapterId"
        @course-change="onCourseChange"
      />
    </div>
  </main>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import AITutorPanel from '../components/AITutorPanel.vue';

const route = useRoute();
const router = useRouter();

// Resolve course/chapter from query string so the tutor route is bookmarkable:
//   /tutor                           — global, no scope
//   /tutor?course=ai-intro           — course scope
//   /tutor?course=ai-intro&chapter=ai-search
const activeCourseId = computed(() => {
  const v = route.query.course;
  return typeof v === 'string' ? v : '';
});

const activeChapterId = computed(() => {
  const v = route.query.chapter;
  return typeof v === 'string' ? v : '';
});

function onCourseChange(courseId) {
  const query = { ...route.query, course: courseId };
  delete query.chapter;
  router.replace({ query });
}
</script>

<style scoped>
.tutor-page {
  min-height: calc(100vh - var(--nav-height));
  background: var(--surface-0);
  display: flex;
  flex-direction: column;
}

.tutor-page-shell {
  flex: 1;
  display: flex;
  width: 100%;
  max-width: none;
  margin: 0 auto;
  min-height: calc(100vh - var(--nav-height));
}
</style>
