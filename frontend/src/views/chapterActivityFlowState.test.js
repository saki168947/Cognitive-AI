import { describe, expect, it } from 'vitest';
import {
  ACTIVITY_FLOW_ORDER,
  buildActivityFlow,
  buildChapterActivityPath,
  buildChapterIdentity,
  buildConceptTrace,
  findActiveActivity,
  progressFromActivities
} from './chapterActivityFlowState';

describe('chapter activity flow state', () => {
  it('builds canonical activity flow with published activities and graceful fallback items', () => {
    const chapter = {
      id: 'ai-search',
      title: 'Search and Problem Solving',
      body: 'Search frames intelligence as finding paths.',
      quiz_items: [
        { id: 'quiz-1', prompt: 'What is a heuristic?', answer: 'An estimate.' }
      ]
    };
    const activities = [
      {
        id: 'activity-ai-search-lab',
        chapter_id: 'ai-search',
        title: 'Code Lab: Heuristic Search Sandbox',
        type: 'code_lab',
        summary: 'Compare search strategies.',
        status: 'published',
        provider: 'jupyterlite',
        estimated_minutes: 40,
        linked_concept_ids: ['concept-search']
      },
      {
        id: 'draft-activity',
        chapter_id: 'ai-search',
        title: 'Draft Deck',
        type: 'lecture_deck',
        status: 'draft'
      },
      {
        id: 'other-chapter',
        chapter_id: 'ai-learning',
        title: 'Other Lab',
        type: 'code_lab',
        status: 'published'
      }
    ];

    const flow = buildActivityFlow({ chapter, activities });

    expect(flow).toHaveLength(ACTIVITY_FLOW_ORDER.length);
    expect(flow.map((item) => item.type)).toEqual([
      'lecture_deck',
      'code_lab',
      'cognitive_experiment',
      'bci_dataset_lab',
      'quiz_reflection'
    ]);
    expect(flow[0]).toMatchObject({
      id: 'ai-search-lecture_deck-generated',
      source: 'generated',
      title: 'Lecture',
      displayTitle: 'LECTURE',
      status: 'available',
      estimated_minutes: 32,
      provider: 'generated',
      linked_concept_ids: []
    });
    expect(flow[1]).toMatchObject({
      id: 'activity-ai-search-lab',
      source: 'activity',
      title: 'Code Lab: Heuristic Search Sandbox',
      displayTitle: 'CODE LAB',
      status: 'published',
      estimated_minutes: 40,
      provider: 'jupyterlite',
      linked_concept_ids: ['concept-search']
    });
    expect(flow[4]).toMatchObject({
      source: 'quiz',
      title: 'Quiz / Reflection',
      displayTitle: 'QUIZ / REFLECTION',
      summary: '1 review prompt available for this chapter.',
      provider: 'generated',
      linked_concept_ids: []
    });
  });

  it('synthesizes canonical fallback flow when activities are malformed', () => {
    const chapter = {
      id: 'ai-foundations',
      title: 'Foundations',
      body: 'Foundations introduce agents, environments, and intelligence.'
    };

    expect(buildActivityFlow({ chapter, activities: null })).toHaveLength(ACTIVITY_FLOW_ORDER.length);
    expect(buildActivityFlow({ chapter, activities: { status: 'published' } }).map((item) => item.type)).toEqual(
      ACTIVITY_FLOW_ORDER
    );
  });

  it('builds chapter identity and route paths', () => {
    const course = { id: 'ai-intro', title: '人工智能导论', summary: 'Course summary' };
    const chapter = {
      id: 'ai-learning',
      title: 'Learning and Neural Networks',
      order: 3,
      body: 'Neural networks learn layered representations from data.'
    };

    expect(buildChapterActivityPath('ai-intro', 'ai-learning')).toBe('/courses/ai-intro/chapters/ai-learning');
    expect(buildChapterIdentity({ course, chapter, chapterIndex: 2 })).toEqual({
      courseLabel: 'AI INTRODUCTION',
      chapterNumber: '03',
      title: 'Learning and Neural Networks',
      description: 'Neural networks learn layered representations from data.',
      backPath: '/courses/ai-intro'
    });
    expect(buildChapterIdentity({
      course: { id: 'brain-cog-intro', title: '脑机与认知科学导论' },
      chapter,
      chapterIndex: 2
    }).courseLabel).toBe('NEUROSCIENCE 101');
  });

  it('computes progress and active activity details', () => {
    const flow = [
      { id: 'a', status: 'completed' },
      { id: 'b', status: 'published' },
      { id: 'c', status: 'available' },
      { id: 'd', status: 'locked' }
    ];

    expect(progressFromActivities(flow)).toBe(25);
    expect(findActiveActivity(flow, 'b')).toBe(flow[1]);
    expect(findActiveActivity(flow, 'missing')).toBe(flow[0]);
  });

  it('builds a concept trace from graph data and active activity concept ids', () => {
    const graph = {
      nodes: [
        { id: 'concept-search', label: 'Heuristic Search' },
        { id: 'concept-rl', label: 'Reinforcement Learning' },
        { id: 'concept-attention', label: 'Attention' }
      ],
      edges: [
        { id: 'edge-1', source: 'concept-search', target: 'concept-rl', relationship: 'PREREQUISITE_OF' },
        { id: 'edge-2', source: 'concept-rl', target: 'concept-attention', relationship: 'RELATED_TO' }
      ]
    };

    const trace = buildConceptTrace(graph, ['concept-search']);
    const repeatedTrace = buildConceptTrace(graph, ['concept-search']);

    expect(trace.nodes).toHaveLength(3);
    expect(trace.nodes[0]).toMatchObject({ id: 'concept-search', label: 'Heuristic Search', active: true });
    expect(trace.nodes.map(({ id, x, y }) => ({ id, x, y }))).toEqual([
      { id: 'concept-search', x: 50, y: 8 },
      { id: 'concept-rl', x: 50, y: 50 },
      { id: 'concept-attention', x: 50, y: 92 }
    ]);
    expect(repeatedTrace.nodes.map(({ id, x, y }) => ({ id, x, y }))).toEqual(
      trace.nodes.map(({ id, x, y }) => ({ id, x, y }))
    );
    expect(trace.edges).toEqual([
      { id: 'edge-1', source: 'concept-search', target: 'concept-rl', active: true },
      { id: 'edge-2', source: 'concept-rl', target: 'concept-attention', active: false }
    ]);
  });
});
