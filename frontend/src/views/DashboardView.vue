<template>
  <section class="view">
    <header class="view-header">
      <p class="view-kicker">Learning dashboard</p>
      <h1 class="view-title">Course workspace</h1>
      <p class="view-copy">Choose a course to review chapters, practice questions, and tutor answers.</p>
    </header>

    <div v-if="loading" class="panel">
      <p class="status-message">Loading courses...</p>
    </div>

    <div v-else-if="error" class="panel">
      <p class="status-message error">{{ error }}</p>
      <button type="button" class="button secondary" @click="loadCourses">Retry</button>
    </div>

    <div v-else-if="courses.length === 0" class="panel">
      <p class="status-message">No courses are available yet.</p>
    </div>

    <div v-else class="grid course-grid">
      <RouterLink
        v-for="course in courses"
        :key="course.id"
        class="panel course-card"
        :to="`/courses/${course.id}`"
      >
        <h2>{{ course.title || course.name || 'Untitled course' }}</h2>
        <p>{{ course.summary || course.description || 'No summary available.' }}</p>
      </RouterLink>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { listCourses } from '../api/courses';

const courses = ref([]);
const loading = ref(false);
const error = ref('');

onMounted(loadCourses);

async function loadCourses() {
  loading.value = true;
  error.value = '';

  try {
    const result = await listCourses();
    courses.value = Array.isArray(result) ? result : [];
  } catch (caughtError) {
    courses.value = [];
    error.value = caughtError?.message || 'Unable to load courses.';
  } finally {
    loading.value = false;
  }
}
</script>
