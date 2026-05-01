<template>
  <div class="review-queue">
    <p v-if="items.length === 0" class="status-message">No pending review items.</p>

    <article v-for="item in items" :key="item.id" class="panel review-item">
      <header class="review-item-header">
        <div>
          <p class="eyebrow">{{ item.status || 'unknown' }}</p>
          <h2>{{ item.title || item.name || item.id || 'Untitled review item' }}</h2>
        </div>
        <div class="review-actions" aria-label="Review actions">
          <button
            v-if="item.status === 'draft'"
            type="button"
            class="button small"
            @click="$emit('approve', item.id)"
          >
            Approve
          </button>
          <button
            v-if="item.status === 'draft'"
            type="button"
            class="button small secondary compact"
            @click="$emit('reject', item.id)"
          >
            Reject
          </button>
          <button
            v-if="item.status === 'reviewed'"
            type="button"
            class="button small"
            @click="$emit('publish', item.id)"
          >
            Publish
          </button>
        </div>
      </header>

      <pre class="payload-preview">{{ formatPayload(item.payload) }}</pre>
    </article>
  </div>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    default: () => []
  }
});

defineEmits(['approve', 'reject', 'publish']);

function formatPayload(payload) {
  return JSON.stringify(payload ?? {}, null, 2);
}
</script>
