import { describe, expect, it } from 'vitest';
import {
  filterGraph,
  graphNeighborhood,
  graphTypeOptions,
  relationshipRows,
  toGraphStats,
  validGraphEdges
} from './graphTransform';

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

  it('returns sorted type options with counts', () => {
    expect(graphTypeOptions(graph)).toEqual([
      { type: 'concept', count: 1 },
      { type: 'process', count: 2 }
    ]);
  });

  it('filters nodes by active type before keeping valid edges', () => {
    expect(filterGraph(graph, '', ['process'])).toEqual({
      nodes: [
        { id: 'memory', label: 'Working Memory', type: 'process', definition: 'Short-term maintenance and manipulation.' },
        { id: 'control', label: 'Cognitive Control', type: 'process', definition: 'Goal-directed regulation.' }
      ],
      edges: [
        { source: 'memory', target: 'control', relationship: 'enables' }
      ]
    });
  });

  it('extracts the direct neighborhood around a selected concept', () => {
    expect(graphNeighborhood(graph, 'memory')).toEqual({
      nodes: [
        { id: 'attention', label: 'Attention', type: 'concept', definition: 'Selective focus of cognitive resources.' },
        { id: 'memory', label: 'Working Memory', type: 'process', definition: 'Short-term maintenance and manipulation.' },
        { id: 'control', label: 'Cognitive Control', type: 'process', definition: 'Goal-directed regulation.' }
      ],
      edges: [
        { source: 'attention', target: 'memory', relationship: 'supports', evidence: 'Attention improves maintenance.' },
        { source: 'memory', target: 'control', relationship: 'enables' }
      ]
    });
  });

  it('builds relationship rows with readable endpoint labels', () => {
    expect(relationshipRows(graph)).toEqual([
      {
        key: 'attention->memory:supports',
        sourceId: 'attention',
        targetId: 'memory',
        sourceLabel: 'Attention',
        targetLabel: 'Working Memory',
        relationship: 'supports',
        evidence: 'Attention improves maintenance.',
        edge: { source: 'attention', target: 'memory', relationship: 'supports', evidence: 'Attention improves maintenance.' }
      },
      {
        key: 'memory->control:enables',
        sourceId: 'memory',
        targetId: 'control',
        sourceLabel: 'Working Memory',
        targetLabel: 'Cognitive Control',
        relationship: 'enables',
        evidence: '',
        edge: { source: 'memory', target: 'control', relationship: 'enables' }
      }
    ]);
  });
});
