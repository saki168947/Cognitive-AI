import { describe, expect, it } from 'vitest';
import { chapterDisplayTitle, chapterNodeClass, chapterSubtopics } from './courseViewState';

describe('course view state helpers', () => {
  it('builds bilingual chapter titles with fallbacks', () => {
    expect(chapterDisplayTitle({ title: 'Search and Problem Solving' })).toEqual({
      en: 'Search and Problem Solving',
      zh: 'Search and Problem Solving'
    });
    expect(chapterDisplayTitle({ id: 'ai-foundations' })).toEqual({
      en: 'Foundations',
      zh: '基础'
    });
    expect(chapterDisplayTitle({ id: 'unknown-id', name: 'Custom' })).toEqual({
      en: 'Custom',
      zh: 'Custom'
    });
  });

  it('extracts up to four bilingual subtopics from chapter metadata', () => {
    const result = chapterSubtopics({ id: 'ai-search' });
    expect(result).toHaveLength(4);
    expect(result[0]).toEqual({ en: 'Problem-Solving Agents', zh: '问题求解智能体' });

    // fallback with raw sections
    const raw = chapterSubtopics({
      sections: ['Agents', 'Search']
    });
    expect(raw).toEqual([
      { en: 'Agents', zh: 'Agents' },
      { en: 'Search', zh: 'Search' }
    ]);
  });

  it('falls back to a learning action when no subtopics exist', () => {
    expect(chapterSubtopics({})).toEqual([{ en: 'Enter chapter workspace', zh: '进入章节工作台' }]);
  });

  it('cycles path position classes for long courses', () => {
    expect(chapterNodeClass(0)).toBe('course-path-node path-node-1');
    expect(chapterNodeClass(4)).toBe('course-path-node path-node-5');
    expect(chapterNodeClass(5)).toBe('course-path-node path-node-1');
  });
});
