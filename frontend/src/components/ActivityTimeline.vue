<template>
  <section class="activity-timeline">
    <ActivityCard
      v-for="activity in activities"
      :key="activity.id"
      :activity="activity"
    />
    <p v-if="activities.length === 0" class="status-message">{{ emptyText }}</p>
  </section>
</template>

<script setup>
import ActivityCard from './ActivityCard.vue';

defineProps({
  activities: {
    type: Array,
    default: () => []
  },
  emptyText: {
    type: String,
    default: '暂无活动。'
  }
});
</script>

<style scoped>
.activity-timeline {
  display: grid;
  gap: 12px;
}
</style>
