<template>
  <aside class="chapter-concept-trace" aria-label="Chapter concept trace">
    <svg viewBox="0 0 260 420" role="img" aria-label="Concept relationships">
      <path
        v-for="edge in renderedEdges"
        :key="edge.id"
        :d="edge.path"
        :class="['concept-trace-edge', { 'is-active': edge.active }]"
      />
      <g
        v-for="node in renderedNodes"
        :key="node.id"
        :class="['concept-trace-node', { 'is-active': node.active }]"
      >
        <circle :cx="node.x" :cy="node.y" :r="node.active ? 7 : 4" />
        <text :x="node.labelX" :y="node.labelY">{{ node.label }}</text>
      </g>
    </svg>
  </aside>
</template>

<script setup>
import { computed } from 'vue';

const VIEWBOX_WIDTH = 260;
const VIEWBOX_HEIGHT = 420;
const TRACE_PADDING_X = 34;
const TRACE_PADDING_Y = 28;

const props = defineProps({
  trace: {
    type: Object,
    default: () => ({ nodes: [], edges: [] })
  }
});

function safeNumber(value, fallback) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function projectCoordinate(value, size, padding) {
  const number = safeNumber(value, 50);
  const usableSize = size - padding * 2;

  return padding + (number / 100) * usableSize;
}

const normalizedTrace = computed(() => {
  if (!props.trace || typeof props.trace !== 'object' || Array.isArray(props.trace)) {
    return { nodes: [], edges: [] };
  }

  return props.trace;
});

const renderedNodes = computed(() => {
  const nodes = Array.isArray(normalizedTrace.value.nodes) ? normalizedTrace.value.nodes : [];

  return nodes
    .filter((node) => node?.id)
    .map((node) => {
      const x = Math.round(projectCoordinate(node.x, VIEWBOX_WIDTH, TRACE_PADDING_X));
      const y = Math.round(projectCoordinate(node.y, VIEWBOX_HEIGHT, TRACE_PADDING_Y));

      return {
        ...node,
        x,
        y,
        label: node.label || node.name || node.id,
        labelX: x + 12,
        labelY: y + 4
      };
    });
});

const nodeMap = computed(() =>
  renderedNodes.value.reduce((map, node) => {
    map.set(node.id, node);
    return map;
  }, new Map())
);

const renderedEdges = computed(() => {
  const edges = Array.isArray(normalizedTrace.value.edges) ? normalizedTrace.value.edges : [];

  return edges
    .map((edge, index) => {
      if (!edge || typeof edge !== 'object' || edge.source == null || edge.target == null) {
        return null;
      }

      const source = nodeMap.value.get(edge.source);
      const target = nodeMap.value.get(edge.target);

      if (!source || !target) return null;

      const direction = index % 2 === 0 ? 1 : -1;
      const midX = (source.x + target.x) / 2 + 36 * direction;
      const midY = (source.y + target.y) / 2;

      return {
        ...edge,
        id: edge.id || `${edge.source}-${edge.target}-${index}`,
        path: `M ${source.x} ${source.y} C ${midX} ${source.y}, ${midX} ${target.y}, ${target.x} ${target.y}`,
        midY
      };
    })
    .filter(Boolean);
});
</script>

<style scoped>
.chapter-concept-trace {
  width: min(100%, 260px);
  min-width: 180px;
  color: var(--text-1, #111);
  pointer-events: none;
}

.chapter-concept-trace svg {
  display: block;
  width: 100%;
  height: auto;
  overflow: visible;
}

.concept-trace-edge {
  fill: none;
  stroke: currentColor;
  stroke-width: 0.8;
  stroke-linecap: round;
  opacity: 0.18;
}

.concept-trace-edge.is-active {
  stroke-width: 1.2;
  opacity: 0.55;
}

.concept-trace-node {
  fill: currentColor;
  opacity: 0.56;
}

.concept-trace-node circle {
  transition: r 180ms ease, opacity 180ms ease;
}

.concept-trace-node text {
  fill: currentColor;
  font-size: 9px;
  font-weight: 650;
  letter-spacing: 0;
  opacity: 0;
}

.concept-trace-node.is-active {
  opacity: 1;
}

.concept-trace-node.is-active circle {
  fill: currentColor;
}

.concept-trace-node.is-active text {
  opacity: 0.62;
}
</style>
