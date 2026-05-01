<template>
  <section class="activity-timeline">
    <ActivityCard
      v-for="activity in visibleActivities"
      :key="activity.id"
      :activity="activity"
    />
    <p v-if="loading" class="status-message">{{ loadingText }}</p>
    <p v-else-if="visibleActivities.length === 0" class="status-message">{{ emptyText }}</p>
  </section>
</template>

<script setup>
import { computed } from 'vue';
import ActivityCard from './ActivityCard.vue';

const props = defineProps({
  activities: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingText: {
    type: String,
    default: '正在加载活动...'
  },
  emptyText: {
    type: String,
    default: '暂无活动。'
  }
});

const visibleActivities = computed(() => props.activities ?? []);
</script>

<style scoped>
.activity-timeline {
  display: grid;
  gap: 12px;
}
</style>
