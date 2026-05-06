<script setup>
import { ref, watch, onBeforeUnmount } from 'vue';
import { useIntersectionObserver } from '@vueuse/core';

const props = defineProps({
  value: {
    type: [Number, String],
    default: 0
  },
  label: {
    type: String,
    default: ''
  },
  kicker: {
    type: String,
    default: ''
  },
  suffix: {
    type: String,
    default: ''
  },
  accent: {
    type: String,
    default: 'primary',
    validator: (v) => ['primary', 'amber', 'violet', 'emerald', 'rose', 'cyan'].includes(v)
  },
  duration: {
    type: Number,
    default: 1400
  },
  format: {
    type: String,
    default: 'integer'
  }
});

const tile = ref(null);
const display = ref(0);
const hasAnimated = ref(false);
let raf = null;

const targetValue = () => {
  const n = Number(props.value);
  return Number.isFinite(n) ? n : 0;
};

function easeOutExpo(t) {
  return t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
}

function formatValue(n) {
  if (props.format === 'integer') {
    return Math.round(n).toLocaleString('en-US');
  }
  if (props.format === 'percent') {
    return `${Math.round(n)}`;
  }
  if (props.format === 'decimal') {
    return n.toFixed(1);
  }
  return String(Math.round(n));
}

function runAnimation() {
  if (hasAnimated.value) return;
  hasAnimated.value = true;
  const target = targetValue();
  const start = performance.now();
  const dur = props.duration;

  function step(now) {
    const t = Math.min(1, (now - start) / dur);
    display.value = target * easeOutExpo(t);
    if (t < 1) {
      raf = requestAnimationFrame(step);
    } else {
      display.value = target;
    }
  }

  raf = requestAnimationFrame(step);
}

const { stop } = useIntersectionObserver(
  tile,
  ([entry]) => {
    if (entry?.isIntersecting) {
      runAnimation();
    }
  },
  { threshold: 0.4 }
);

watch(
  () => props.value,
  () => {
    hasAnimated.value = false;
    if (tile.value) {
      const rect = tile.value.getBoundingClientRect();
      if (rect.top < window.innerHeight && rect.bottom > 0) {
        runAnimation();
      }
    }
  }
);

onBeforeUnmount(() => {
  if (raf) cancelAnimationFrame(raf);
  stop();
});
</script>

<template>
  <div ref="tile" class="stat-tile" :data-accent="accent">
    <p v-if="kicker" class="stat-kicker mono">{{ kicker }}</p>
    <p class="stat-value mono">
      <span class="stat-number">{{ formatValue(display) }}</span>
      <span v-if="suffix" class="stat-suffix">{{ suffix }}</span>
    </p>
    <p v-if="label" class="stat-label">{{ label }}</p>
    <div class="stat-glow" aria-hidden="true"></div>
  </div>
</template>

<style scoped>
.stat-tile {
  position: relative;
  display: grid;
  align-content: start;
  gap: 8px;
  padding: 22px 24px 24px;
  border-radius: var(--radius-lg);
  background: rgba(17, 26, 46, 0.5);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border-default);
  overflow: hidden;
  isolation: isolate;
  min-height: 120px;
  transition:
    border-color var(--dur-3) var(--ease-out-expo),
    transform var(--dur-3) var(--ease-out-expo),
    box-shadow var(--dur-3) var(--ease-out-expo);
}

.stat-tile:hover {
  transform: translateY(-2px);
  border-color: var(--border-strong);
  box-shadow: var(--shadow-md);
}

/* Top accent line */
.stat-tile::before {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  height: 2px;
  background: var(--primary);
  opacity: 0.8;
}

/* Background glow */
.stat-glow {
  position: absolute;
  top: -20px;
  right: -20px;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--primary);
  opacity: 0.04;
  filter: blur(30px);
  pointer-events: none;
}

.stat-kicker {
  margin: 0;
  color: var(--text-4);
  font-size: 10px;
  letter-spacing: 0.12em;
}

.stat-value {
  margin: 0;
  display: flex;
  align-items: baseline;
  gap: 6px;
  color: var(--text-1);
  font-size: 36px;
  font-weight: 700;
  line-height: 1;
  font-variant-numeric: tabular-nums;
}

.stat-suffix {
  font-size: 0.45em;
  color: var(--text-3);
  font-weight: 400;
}

.stat-label {
  margin: 0;
  color: var(--text-3);
  font-size: 13px;
  letter-spacing: 0;
}

/* Accent variants */
.stat-tile[data-accent="primary"]::before { background: var(--primary); }
.stat-tile[data-accent="amber"]::before { background: var(--amber); }
.stat-tile[data-accent="violet"]::before { background: var(--violet); }
.stat-tile[data-accent="emerald"]::before { background: var(--emerald); }
.stat-tile[data-accent="rose"]::before { background: var(--rose); }
.stat-tile[data-accent="cyan"]::before { background: var(--cyan); }

.stat-tile[data-accent="primary"] .stat-number { color: var(--primary); }
.stat-tile[data-accent="amber"] .stat-number { color: var(--amber); }
.stat-tile[data-accent="violet"] .stat-number { color: var(--violet); }
.stat-tile[data-accent="emerald"] .stat-number { color: var(--emerald); }
.stat-tile[data-accent="rose"] .stat-number { color: var(--rose); }
.stat-tile[data-accent="cyan"] .stat-number { color: var(--cyan); }

.stat-tile[data-accent="primary"] .stat-glow { background: var(--primary); }
.stat-tile[data-accent="amber"] .stat-glow { background: var(--amber); }
.stat-tile[data-accent="violet"] .stat-glow { background: var(--violet); }
.stat-tile[data-accent="emerald"] .stat-glow { background: var(--emerald); }
.stat-tile[data-accent="rose"] .stat-glow { background: var(--rose); }
.stat-tile[data-accent="cyan"] .stat-glow { background: var(--cyan); }

@media (max-width: 768px) {
  .stat-value {
    font-size: 30px;
  }
}
</style>
