<script setup>
import { ref, onBeforeUnmount } from 'vue';
import { useIntersectionObserver } from '@vueuse/core';

const props = defineProps({
  delay: {
    type: Number,
    default: 0
  },
  stagger: {
    type: Number,
    default: 0
  },
  rise: {
    type: Number,
    default: 24
  },
  threshold: {
    type: Number,
    default: 0.18
  },
  once: {
    type: Boolean,
    default: true
  },
  as: {
    type: String,
    default: 'div'
  }
});

const root = ref(null);
const visible = ref(false);

const { stop } = useIntersectionObserver(
  root,
  ([entry]) => {
    if (entry?.isIntersecting) {
      visible.value = true;
      if (props.once) stop();
    } else if (!props.once) {
      visible.value = false;
    }
  },
  { threshold: props.threshold }
);

onBeforeUnmount(() => stop());
</script>

<template>
  <component
    :is="as"
    ref="root"
    class="reveal"
    :data-visible="visible"
    :style="{
      '--reveal-delay': `${delay}ms`,
      '--reveal-stagger': `${stagger}ms`,
      '--reveal-rise': `${rise}px`
    }"
  >
    <slot :visible="visible" />
  </component>
</template>

<style scoped>
.reveal {
  display: block;
}

.reveal > :deep(*) {
  opacity: 0;
  transform: translateY(var(--reveal-rise));
  filter: blur(8px);
  transition:
    opacity var(--dur-5) var(--ease-out-expo) var(--reveal-delay),
    transform var(--dur-5) var(--ease-out-expo) var(--reveal-delay),
    filter var(--dur-5) var(--ease-out-expo) var(--reveal-delay);
}

.reveal[data-visible="true"] > :deep(*) {
  opacity: 1;
  transform: translateY(0);
  filter: blur(0);
}

.reveal[data-visible="true"] > :deep(*:nth-child(2)) { transition-delay: calc(var(--reveal-delay) + var(--reveal-stagger) * 1); }
.reveal[data-visible="true"] > :deep(*:nth-child(3)) { transition-delay: calc(var(--reveal-delay) + var(--reveal-stagger) * 2); }
.reveal[data-visible="true"] > :deep(*:nth-child(4)) { transition-delay: calc(var(--reveal-delay) + var(--reveal-stagger) * 3); }
.reveal[data-visible="true"] > :deep(*:nth-child(5)) { transition-delay: calc(var(--reveal-delay) + var(--reveal-stagger) * 4); }
.reveal[data-visible="true"] > :deep(*:nth-child(6)) { transition-delay: calc(var(--reveal-delay) + var(--reveal-stagger) * 5); }
.reveal[data-visible="true"] > :deep(*:nth-child(7)) { transition-delay: calc(var(--reveal-delay) + var(--reveal-stagger) * 6); }
.reveal[data-visible="true"] > :deep(*:nth-child(8)) { transition-delay: calc(var(--reveal-delay) + var(--reveal-stagger) * 7); }

@media (prefers-reduced-motion: reduce) {
  .reveal > :deep(*) {
    opacity: 1;
    transform: none;
    filter: none;
  }
}
</style>
