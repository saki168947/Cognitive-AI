<template>
  <div class="review-queue">
    <p v-if="items.length === 0" class="status-message">No pending review items.</p>

    <article v-for="item in items" :key="item.id" class="panel review-item">
      <header class="review-item-header">
        <div>
          <p class="eyebrow">{{ item.status || 'unknown' }}</p>
          <h2>{{ item.title || item.name || item.id || 'Untitled review item' }}</h2>
        </div>
        <div class="review-actions" :aria-label="`Review actions for ${item.id}`">
          <button
            v-if="item.status === 'draft'"
            type="button"
            class="button small"
            :disabled="isItemPending(item.id)"
            @click="$emit('approve', item.id)"
          >
            {{ isItemPending(item.id) ? 'Working...' : 'Approve' }}
          </button>
          <button
            v-if="item.status === 'draft'"
            type="button"
            class="button small secondary compact"
            :disabled="isItemPending(item.id)"
            @click="$emit('reject', item.id)"
          >
            Reject
          </button>
          <button
            v-if="item.status === 'reviewed'"
            type="button"
            class="button small"
            :disabled="isItemPending(item.id)"
            @click="$emit('publish', item.id)"
          >
            {{ isItemPending(item.id) ? 'Working...' : 'Publish' }}
          </button>
        </div>
      </header>

      <pre class="payload-preview">{{ formatPayload(item.payload) }}</pre>
    </article>
  </div>
</template>

<script setup>
const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  pendingIds: {
    type: Array,
    default: () => []
  }
});

defineEmits(['approve', 'reject', 'publish']);

function formatPayload(payload) {
  return JSON.stringify(payload ?? {}, null, 2);
}

function isItemPending(id) {
  return id ? props.pendingIds.includes(id) : false;
}
</script>
