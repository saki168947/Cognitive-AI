<template>
  <article class="panel graph-panel">
    <header class="graph-toolbar">
      <div>
        <p class="eyebrow">Map</p>
        <h2>Knowledge Graph</h2>
      </div>

      <div class="graph-controls">
        <input
          v-model="search"
          class="graph-search"
          type="search"
          placeholder="Search concepts"
          aria-label="Search concepts"
        />
        <label class="graph-toggle">
          <input v-model="showEdgeLabels" type="checkbox" />
          <span>Edge labels</span>
        </label>
      </div>
    </header>

    <div class="graph-stats" aria-label="Knowledge graph statistics">
      <span>{{ stats.nodeCount }} nodes</span>
      <span>{{ stats.edgeCount }} edges</span>
      <span>{{ stats.typeCount }} types</span>
    </div>

    <div class="graph-stage">
      <svg
        ref="svgRef"
        class="graph-svg"
        viewBox="0 0 900 420"
        role="img"
        aria-label="Course knowledge graph"
      ></svg>
      <div v-if="visibleGraph.nodes.length === 0" class="graph-empty">
        <p>No matching concepts are available.</p>
      </div>
    </div>

    <aside v-if="selected" class="graph-detail" aria-live="polite">
      <button type="button" class="graph-detail-close" aria-label="Close graph detail" @click="selected = null">
        Close
      </button>
      <p class="eyebrow">{{ selected.kind }}</p>
      <h3>{{ selectedTitle }}</h3>
      <p v-if="selectedBody">{{ selectedBody }}</p>
      <p v-else class="status-message">No definition or evidence is available.</p>
    </aside>
  </article>
</template>

<script setup>
import * as d3 from 'd3';
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { edgeEndpointId, filterGraph, toGraphStats } from './graphTransform';

const props = defineProps({
  graph: {
    type: Object,
    default: () => ({ nodes: [], edges: [] })
  }
});

const svgRef = ref(null);
const search = ref('');
const selected = ref(null);
const showEdgeLabels = ref(false);
let simulation = null;

const visibleGraph = computed(() => filterGraph(props.graph, search.value));
const stats = computed(() => toGraphStats(visibleGraph.value));
const nodeLabelById = computed(() => {
  const labels = new Map();
  visibleGraph.value.nodes.forEach((node) => {
    labels.set(node.id, node.label || node.name || node.id);
  });
  return labels;
});

const selectedTitle = computed(() => {
  if (!selected.value) {
    return '';
  }

  if (selected.value.kind === 'Concept') {
    return selected.value.item.label || selected.value.item.name || selected.value.item.id;
  }

  const source = nodeLabelById.value.get(edgeEndpointId(selected.value.item.source)) || edgeEndpointId(selected.value.item.source);
  const target = nodeLabelById.value.get(edgeEndpointId(selected.value.item.target)) || edgeEndpointId(selected.value.item.target);
  const relationship = selected.value.item.relationship || selected.value.item.label || 'relates to';
  return `${source} ${relationship} ${target}`;
});

const selectedBody = computed(() => {
  if (!selected.value) {
    return '';
  }

  if (selected.value.kind === 'Relationship') {
    return selected.value.item.evidence || selected.value.item.definition || selected.value.item.description || '';
  }

  return selected.value.item.definition || selected.value.item.description || selected.value.item.evidence || '';
});

onMounted(drawGraph);
onBeforeUnmount(stopSimulation);

watch([visibleGraph, showEdgeLabels], () => {
  selected.value = null;
  drawGraph();
});

function stopSimulation() {
  if (simulation) {
    simulation.stop();
    simulation = null;
  }
}

function drawGraph() {
  if (!svgRef.value) {
    return;
  }

  stopSimulation();
  const svg = d3.select(svgRef.value);
  svg.selectAll('*').remove();

  const width = 900;
  const height = 420;
  const nodes = visibleGraph.value.nodes.map((node) => ({ ...node }));
  const edges = visibleGraph.value.edges.map((edge) => ({
    ...edge,
    source: edgeEndpointId(edge.source),
    target: edgeEndpointId(edge.target)
  }));

  if (nodes.length === 0) {
    return;
  }

  const root = svg.append('g');
  const links = root
    .append('g')
    .attr('class', 'graph-links')
    .selectAll('line')
    .data(edges)
    .join('line')
    .attr('stroke-width', 1.8)
    .on('click', (event, edge) => {
      event.stopPropagation();
      selected.value = { kind: 'Relationship', item: edge };
    });

  const linkLabels = root
    .append('g')
    .attr('class', 'graph-edge-labels')
    .selectAll('text')
    .data(showEdgeLabels.value ? edges : [])
    .join('text')
    .text((edge) => edge.relationship || edge.label || '')
    .attr('text-anchor', 'middle');

  const nodeGroups = root
    .append('g')
    .attr('class', 'graph-nodes')
    .selectAll('g')
    .data(nodes)
    .join('g')
    .attr('class', 'graph-node')
    .call(d3.drag()
      .on('start', dragStarted)
      .on('drag', dragged)
      .on('end', dragEnded))
    .on('click', (event, node) => {
      event.stopPropagation();
      selected.value = { kind: 'Concept', item: node };
    });

  nodeGroups
    .append('circle')
    .attr('r', (node) => node.type ? 17 : 14);

  nodeGroups
    .append('text')
    .attr('y', 31)
    .attr('text-anchor', 'middle')
    .text((node) => node.label || node.name || node.id);

  svg.on('click', () => {
    selected.value = null;
  });

  simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(edges).id((node) => node.id).distance(112).strength(0.55))
    .force('charge', d3.forceManyBody().strength(-360))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide(44))
    .on('tick', () => {
      nodes.forEach((node) => {
        node.x = Math.max(36, Math.min(width - 36, node.x));
        node.y = Math.max(36, Math.min(height - 48, node.y));
      });

      links
        .attr('x1', (edge) => edge.source.x)
        .attr('y1', (edge) => edge.source.y)
        .attr('x2', (edge) => edge.target.x)
        .attr('y2', (edge) => edge.target.y);

      linkLabels
        .attr('x', (edge) => (edge.source.x + edge.target.x) / 2)
        .attr('y', (edge) => (edge.source.y + edge.target.y) / 2);

      nodeGroups.attr('transform', (node) => `translate(${node.x},${node.y})`);
    });
}

function dragStarted(event, node) {
  if (!event.active && simulation) {
    simulation.alphaTarget(0.3).restart();
  }
  node.fx = node.x;
  node.fy = node.y;
}

function dragged(event, node) {
  node.fx = event.x;
  node.fy = event.y;
}

function dragEnded(event, node) {
  if (!event.active && simulation) {
    simulation.alphaTarget(0);
  }
  node.fx = null;
  node.fy = null;
}
</script>
