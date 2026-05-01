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

export function filterGraph(graph, search) {
  const normalized = normalizeGraph(graph);
  const query = String(search || '').trim().toLowerCase();

  if (!query) {
    return {
      nodes: normalized.nodes,
      edges: validGraphEdges(normalized)
    };
  }

  const nodes = normalized.nodes.filter((node) => {
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
