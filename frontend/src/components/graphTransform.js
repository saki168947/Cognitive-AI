function asArray(value) {
  return Array.isArray(value) ? value : [];
}

export function edgeEndpointId(endpoint) {
  if (endpoint && typeof endpoint === 'object') {
    return endpoint.id;
  }

  return endpoint;
}

export function normalizeGraph(graph) {
  return {
    nodes: asArray(graph?.nodes).filter((node) => node?.id),
    edges: asArray(graph?.edges)
  };
}

export function validGraphEdges(graph) {
  const normalized = normalizeGraph(graph);
  const nodeIds = new Set(normalized.nodes.map((node) => node.id));

  return normalized.edges.filter((edge) => {
    const source = edgeEndpointId(edge?.source);
    const target = edgeEndpointId(edge?.target);
    return nodeIds.has(source) && nodeIds.has(target);
  });
}

export function toGraphStats(graph) {
  const normalized = normalizeGraph(graph);
  const types = new Set(normalized.nodes.map((node) => node.type).filter(Boolean));

  return {
    nodeCount: normalized.nodes.length,
    edgeCount: validGraphEdges(normalized).length,
    typeCount: types.size
  };
}

export function graphTypeOptions(graph) {
  const normalized = normalizeGraph(graph);
  const counts = new Map();

  normalized.nodes.forEach((node) => {
    const type = node.type || 'concept';
    counts.set(type, (counts.get(type) || 0) + 1);
  });

  return [...counts.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([type, count]) => ({ type, count }));
}

export function filterGraph(graph, search, activeTypes = []) {
  const normalized = normalizeGraph(graph);
  const query = String(search || '').trim().toLowerCase();
  const typeSet = new Set(asArray(activeTypes).filter(Boolean));

  const nodes = normalized.nodes.filter((node) => {
    if (typeSet.size > 0 && !typeSet.has(node.type || 'concept')) {
      return false;
    }
    if (!query) {
      return true;
    }
    const haystack = [
      node.label,
      node.name,
      node.definition,
      node.description,
      node.type
    ].filter(Boolean).join(' ').toLowerCase();

    return haystack.includes(query);
  });

  const visibleIds = new Set(nodes.map((node) => node.id));
  const edges = validGraphEdges({ nodes, edges: normalized.edges }).filter((edge) => {
    const source = edgeEndpointId(edge.source);
    const target = edgeEndpointId(edge.target);
    return visibleIds.has(source) && visibleIds.has(target);
  });

  return { nodes, edges };
}

export function graphNeighborhood(graph, centerId) {
  const normalized = normalizeGraph(graph);
  if (!centerId) {
    return {
      nodes: normalized.nodes,
      edges: validGraphEdges(normalized)
    };
  }

  const validEdges = validGraphEdges(normalized);
  const visibleIds = new Set([centerId]);
  const edges = validEdges.filter((edge) => {
    const source = edgeEndpointId(edge.source);
    const target = edgeEndpointId(edge.target);
    const connected = source === centerId || target === centerId;
    if (connected) {
      visibleIds.add(source);
      visibleIds.add(target);
    }
    return connected;
  });

  return {
    nodes: normalized.nodes.filter((node) => visibleIds.has(node.id)),
    edges
  };
}

export function relationshipRows(graph) {
  const normalized = normalizeGraph(graph);
  const labels = new Map(
    normalized.nodes.map((node) => [node.id, node.label || node.name || node.id])
  );

  return validGraphEdges(normalized).map((edge, index) => {
    const sourceId = edgeEndpointId(edge.source);
    const targetId = edgeEndpointId(edge.target);
    return {
      key: edge.id || `${sourceId}->${targetId}:${edge.relationship || edge.label || index}`,
      sourceId,
      targetId,
      sourceLabel: labels.get(sourceId) || sourceId,
      targetLabel: labels.get(targetId) || targetId,
      relationship: edge.relationship || edge.label || 'relates to',
      evidence: edge.evidence || edge.definition || edge.description || '',
      edge
    };
  });
}
