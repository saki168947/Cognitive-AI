import { describe, expect, it } from 'vitest';
import { createReferenceNetworkLayout } from './featureNetworkLayout';

describe('createReferenceNetworkLayout', () => {
  it('creates a dense flat knowledge graph filling the viewport', () => {
    const layout = createReferenceNetworkLayout({ seed: 42 });

    expect(layout.nodes.length).toBeGreaterThanOrEqual(220);
    expect(layout.nodes.length).toBeLessThanOrEqual(280);
    expect(layout.faintEdges.length).toBeGreaterThan(layout.nodes.length * 5);
    expect(layout.faintEdges.length).toBeLessThan(layout.nodes.length * 10);
    expect(layout.majorEdges.length).toBeGreaterThanOrEqual(9);
    expect(layout.majorEdges.length).toBeLessThanOrEqual(20);
    expect(layout.blueEdges.length).toBeGreaterThanOrEqual(3);
    expect(layout.blueEdges.length).toBeLessThanOrEqual(5);
    expect(layout.labels).toEqual([]);

    const xValues = layout.nodes.map((node) => node.x);
    const yValues = layout.nodes.map((node) => node.y);
    const zValues = layout.nodes.map((node) => node.z);
    expect(Math.max(...xValues) - Math.min(...xValues)).toBeLessThanOrEqual(9);
    expect(Math.max(...yValues) - Math.min(...yValues)).toBeLessThanOrEqual(9);
    expect(Math.max(...zValues) - Math.min(...zValues)).toBeLessThan(0.08);

    const focus = layout.nodes[layout.focusIndex];
    const longestBluePath = Math.max(
      ...layout.blueEdges.map((edge) => {
        const otherIndex = edge.source === layout.focusIndex ? edge.target : edge.source;
        const other = layout.nodes[otherIndex];
        return Math.hypot(focus.x - other.x, focus.y - other.y);
      })
    );
    expect(longestBluePath).toBeGreaterThan(2.8);
    expect(longestBluePath).toBeLessThan(6.0);

    const longestFaintEdge = Math.max(
      ...layout.faintEdges.map((edge) => {
        const source = layout.nodes[edge.source];
        const target = layout.nodes[edge.target];
        return Math.hypot(source.x - target.x, source.y - target.y);
      })
    );
    expect(longestFaintEdge).toBeLessThan(2.6);

    const longestMajorEdge = Math.max(
      ...layout.majorEdges.map((edge) => {
        const source = layout.nodes[edge.source];
        const target = layout.nodes[edge.target];
        return Math.hypot(source.x - target.x, source.y - target.y);
      })
    );
    expect(longestMajorEdge).toBeLessThan(5.0);
  });
});
