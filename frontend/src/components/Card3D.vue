<script setup>
import { ref } from 'vue';

const props = defineProps({
  intensity: {
    type: Number,
    default: 1
  },
  glow: {
    type: String,
    default: 'cyan',
    validator: (value) => ['cyan', 'violet', 'mixed', 'none'].includes(value)
  },
  as: {
    type: String,
    default: 'div'
  }
});

const card = ref(null);
const tx = ref(0);
const ty = ref(0);
const mx = ref(50);
const my = ref(50);
const isHovering = ref(false);

const MAX_TILT = 8;

function onMove(event) {
  if (!card.value) return;
  const rect = card.value.getBoundingClientRect();
  const px = (event.clientX - rect.left) / rect.width;
  const py = (event.clientY - rect.top) / rect.height;

  mx.value = px * 100;
  my.value = py * 100;

  const factor = MAX_TILT * props.intensity;
  ty.value = (px - 0.5) * factor;
  tx.value = -(py - 0.5) * factor;
}

function onEnter() {
  isHovering.value = true;
}

function onLeave() {
  isHovering.value = false;
  tx.value = 0;
  ty.value = 0;
  mx.value = 50;
  my.value = 50;
}
</script>

<template>
  <component
    :is="as"
    ref="card"
    class="card-3d"
    :data-glow="glow"
    :data-hover="isHovering"
    :style="{
      '--rx': `${tx}deg`,
      '--ry': `${ty}deg`,
      '--mx': `${mx}%`,
      '--my': `${my}%`
    }"
    @pointermove="onMove"
    @pointerenter="onEnter"
    @pointerleave="onLeave"
  >
    <span class="card-3d-edge" aria-hidden="true"></span>
    <span class="card-3d-glow" aria-hidden="true"></span>
    <span class="card-3d-gloss" aria-hidden="true"></span>
    <span class="card-3d-content">
      <slot />
    </span>
  </component>
</template>

<style scoped>
.card-3d {
  position: relative;
  display: block;
  border-radius: var(--radius-lg);
  background:
    linear-gradient(180deg, rgba(28, 28, 43, 0.55), rgba(13, 13, 21, 0.85));
  box-shadow: var(--shadow-md), var(--inner-gloss);
  overflow: hidden;
  isolation: isolate;
  transform-style: preserve-3d;
  transform: perspective(1200px) rotateX(var(--rx, 0deg)) rotateY(var(--ry, 0deg));
  transition:
    transform var(--dur-4) var(--ease-out-expo),
    box-shadow var(--dur-3) var(--ease-out-expo);
  will-change: transform;
  cursor: default;
}

.card-3d[data-hover="true"] {
  transition:
    transform 80ms linear,
    box-shadow var(--dur-3) var(--ease-out-expo);
  box-shadow: var(--shadow-lg), var(--inner-gloss);
}

.card-3d-edge {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.14),
    rgba(255, 255, 255, 0.02) 30%,
    transparent 60%,
    rgba(255, 255, 255, 0.06)
  );
  -webkit-mask:
    linear-gradient(#000, #000) content-box,
    linear-gradient(#000, #000);
          mask:
    linear-gradient(#000, #000) content-box,
    linear-gradient(#000, #000);
  -webkit-mask-composite: xor;
          mask-composite: exclude;
  padding: 1px;
  z-index: 3;
}

.card-3d-glow {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  z-index: 1;
  opacity: 0;
  transition: opacity var(--dur-3) var(--ease-out-expo);
}

.card-3d[data-hover="true"] .card-3d-glow {
  opacity: 1;
}

.card-3d[data-glow="cyan"] .card-3d-glow {
  background: radial-gradient(
    420px 240px at var(--mx) var(--my),
    var(--accent-cyan-soft),
    transparent 65%
  );
}

.card-3d[data-glow="violet"] .card-3d-glow {
  background: radial-gradient(
    420px 240px at var(--mx) var(--my),
    var(--accent-violet-soft),
    transparent 65%
  );
}

.card-3d[data-glow="mixed"] .card-3d-glow {
  background:
    radial-gradient(380px 240px at var(--mx) var(--my), var(--accent-cyan-soft), transparent 60%),
    radial-gradient(280px 200px at calc(100% - var(--mx)) calc(100% - var(--my)), var(--accent-violet-soft), transparent 60%);
}

.card-3d[data-glow="none"] .card-3d-glow {
  display: none;
}

.card-3d-gloss {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  z-index: 2;
  opacity: 0;
  background: radial-gradient(
    160px 80px at var(--mx) var(--my),
    rgba(255, 255, 255, 0.18),
    transparent 70%
  );
  transition: opacity var(--dur-3) var(--ease-out-expo);
}

.card-3d[data-hover="true"] .card-3d-gloss {
  opacity: 1;
}

.card-3d-content {
  position: relative;
  z-index: 4;
  display: block;
  height: 100%;
  transform: translateZ(20px);
}

@media (prefers-reduced-motion: reduce) {
  .card-3d {
    transform: none !important;
  }
}
</style>
