import { describe, expect, it } from 'vitest';
import { chapterDisplayTitle, chapterNodeClass, chapterSubtopics } from './courseViewState';

describe('course view state helpers', () => {
  it('builds readable chapter titles with fallbacks', () => {
    expect(chapterDisplayTitle({ title: 'Search and Problem Solving' })).toBe('Search and Problem Solving');
    expect(chapterDisplayTitle({ name: 'Brain and Cognition' })).toBe('Brain and Cognition');
    expect(chapterDisplayTitle({ id: 'chapter-4' })).toBe('chapter-4');
  });

  it('extracts up to four subtopics from chapter metadata', () => {
    expect(chapterSubtopics({
      sections: ['Agents', 'Search', 'Heuristics', 'Optimization', 'Planning']
    })).toEqual(['Agents', 'Search', 'Heuristics', 'Optimization']);

    expect(chapterSubtopics({
      objectives: ['Understand attention', 'Explain memory']
    })).toEqual(['Understand attention', 'Explain memory']);
  });

  it('falls back to a learning action when no subtopics exist', () => {
    expect(chapterSubtopics({})).toEqual(['进入章节工作台']);
  });

  it('cycles path position classes for long courses', () => {
    expect(chapterNodeClass(0)).toBe('course-path-node path-node-1');
    expect(chapterNodeClass(4)).toBe('course-path-node path-node-5');
    expect(chapterNodeClass(5)).toBe('course-path-node path-node-1');
  });
});
