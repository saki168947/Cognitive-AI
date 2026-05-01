import { describe, expect, it } from 'vitest';
import { filterGraph, toGraphStats, validGraphEdges } from './graphTransform';

const graph = {
  nodes: [
    { id: 'attention', label: 'Attention', type: 'concept', definition: 'Selective focus of cognitive resources.' },
    { id: 'memory', label: 'Working Memory', type: 'process', definition: 'Short-term maintenance and manipulation.' },
    { id: 'control', label: 'Cognitive Control', type: 'process', definition: 'Goal-directed regulation.' }
  ],
  edges: [
    { source: 'attention', target: 'memory', relationship: 'supports', evidence: 'Attention improves maintenance.' },
    { source: 'memory', target: 'control', relationship: 'enables' },
    { source: 'missing', target: 'attention', relationship: 'invalid' }
  ]
};

describe('graph transforms', () => {
  it('counts nodes, valid edges, and unique node types', () => {
    expect(toGraphStats(graph)).toEqual({
      nodeCount: 3,
      edgeCount: 2,
      typeCount: 2
    });
  });

  it('filters invalid edges whose endpoints are not present', () => {
    expect(validGraphEdges(graph)).toEqual([
      { source: 'attention', target: 'memory', relationship: 'supports', evidence: 'Attention improves maintenance.' },
      { source: 'memory', target: 'control', relationship: 'enables' }
    ]);
  });

  it('searches labels and definitions and keeps only visible edges', () => {
    expect(filterGraph(graph, 'memory')).toEqual({
      nodes: [
        { id: 'memory', label: 'Working Memory', type: 'process', definition: 'Short-term maintenance and manipulation.' }
      ],
      edges: []
    });

    expect(filterGraph(graph, 'goal-directed')).toEqual({
      nodes: [
        { id: 'control', label: 'Cognitive Control', type: 'process', definition: 'Goal-directed regulation.' }
      ],
      edges: []
    });
  });
});
