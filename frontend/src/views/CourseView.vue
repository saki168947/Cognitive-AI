<template>
  <section class="view">
    <header class="view-header">
      <p class="view-kicker">Course</p>
      <h1 class="view-title">{{ courseId }}</h1>
      <p class="view-copy">Course route placeholder for learning materials and tutor interactions.</p>
    </header>

    <div class="placeholder-panel">
      <h2>Course placeholder</h2>
      <p>Task 8 can replace this route with the full course experience.</p>
    </div>
  </section>
</template>

<script setup>
defineProps({
  courseId: {
    type: String,
    required: true
  }
});
</script>
