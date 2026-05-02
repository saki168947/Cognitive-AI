export const ACTIVITY_FLOW_ORDER = [
  'lecture_deck',
  'code_lab',
  'cognitive_experiment',
  'bci_dataset_lab',
  'quiz_reflection'
];

const ACTIVITY_FALLBACKS = {
  lecture_deck: {
    title: 'Lecture',
    summary: 'Start with a guided chapter lecture.',
    estimated_minutes: 32
  },
  code_lab: {
    title: 'Code Lab',
    summary: 'Practice the chapter model with an interactive coding task.',
    estimated_minutes: 45
  },
  cognitive_experiment: {
    title: 'Cognitive Experiment',
    summary: 'Run a short experiment that connects behavior to cognition.',
    estimated_minutes: 25
  },
  bci_dataset_lab: {
    title: 'BCI Dataset Lab',
    summary: 'Explore neural data and connect signals to concepts.',
    estimated_minutes: 38
  },
  quiz_reflection: {
    title: 'Quiz / Reflection',
    summary: 'Review the chapter and reflect on the core ideas.',
    estimated_minutes: 12
  }
};

const COURSE_LABELS = {
  'ai-intro': 'AI INTRODUCTION',
  'brain-cog-intro': 'NEUROSCIENCE 101'
};

function chapterIdFor(chapter = {}) {
  return chapter.id || 'chapter';
}

function quizItemsFor(chapter = {}) {
  return Array.isArray(chapter.quiz_items) ? chapter.quiz_items : [];
}

function fallbackFor(type, chapter = {}) {
  const chapterId = chapterIdFor(chapter);
  const fallback = ACTIVITY_FALLBACKS[type] || {
    title: type,
    summary: 'Continue this chapter activity.',
    estimated_minutes: 20
  };

  if (type === 'quiz_reflection') {
    const quizItems = quizItemsFor(chapter);
    const promptLabel = quizItems.length === 1 ? 'prompt' : 'prompts';
    return {
      id: `${chapterId}-${type}-generated`,
      type,
      source: 'quiz',
      title: fallback.title,
      summary: `${quizItems.length} review ${promptLabel} available for this chapter.`,
      status: 'available',
      estimated_minutes: fallback.estimated_minutes,
      quiz_items: quizItems
    };
  }

  return {
    id: `${chapterId}-${type}-generated`,
    type,
    source: 'generated',
    title: fallback.title,
    summary: fallback.summary,
    status: 'available',
    estimated_minutes: fallback.estimated_minutes
  };
}

export function buildActivityFlow({ chapter = {}, activities = [] } = {}) {
  const chapterId = chapterIdFor(chapter);
  const publishedByType = new Map();

  activities
    .filter((activity) => activity?.chapter_id === chapterId && activity.status === 'published')
    .forEach((activity) => {
      if (!publishedByType.has(activity.type)) {
        publishedByType.set(activity.type, activity);
      }
    });

  return ACTIVITY_FLOW_ORDER.map((type, index) => {
    const activity = publishedByType.get(type);
    if (!activity) {
      return {
        ...fallbackFor(type, chapter),
        order: index + 1
      };
    }

    return {
      ...activity,
      type,
      source: 'activity',
      order: index + 1
    };
  });
}

export function buildChapterActivityPath(courseId, chapterId) {
  return `/courses/${courseId}/chapters/${chapterId}`;
}

export function buildChapterIdentity({ course = {}, chapter = {}, chapterIndex = 0 } = {}) {
  const courseId = course.id || 'course';
  const rawChapterNumber = Number.isFinite(chapter.order) ? chapter.order : chapterIndex + 1;
  const courseLabel = COURSE_LABELS[courseId] || String(course.title || courseId).replace(/-/g, ' ').toUpperCase();

  return {
    courseLabel,
    chapterNumber: String(rawChapterNumber).padStart(2, '0'),
    title: chapter.title || chapter.name || 'Untitled Chapter',
    description: chapter.body || chapter.summary || course.summary || '',
    backPath: `/courses/${courseId}`
  };
}

export function progressFromActivities(flow = []) {
  if (!flow.length) {
    return 0;
  }

  const completedCount = flow.filter((item) => item?.status === 'completed').length;
  return Math.round((completedCount / flow.length) * 100);
}

export function findActiveActivity(flow = [], activeActivityId) {
  return flow.find((item) => item?.id === activeActivityId) || flow[0];
}

export function buildConceptTrace(graph = {}, activeConceptIds = []) {
  const activeIds = new Set(activeConceptIds);
  const nodes = Array.isArray(graph.nodes) ? graph.nodes : [];
  const edges = Array.isArray(graph.edges) ? graph.edges : [];

  return {
    nodes: nodes.map((node, index) => {
      const progress = nodes.length <= 1 ? 0.5 : index / (nodes.length - 1);
      return {
        ...node,
        active: activeIds.has(node.id),
        x: Math.round(50 + Math.sin(progress * Math.PI * 2) * 34),
        y: Math.round(8 + progress * 84)
      };
    }),
    edges: edges.map((edge, index) => ({
      id: edge.id || `concept-edge-${index + 1}`,
      source: edge.source,
      target: edge.target,
      active: activeIds.has(edge.source) || activeIds.has(edge.target)
    }))
  };
}
