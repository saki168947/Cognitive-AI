import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('./client', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn()
  }
}));

const { default: apiClient } = await import('./client');
const { listActivities, listCourseActivities, createActivity } = await import('./activities');
const {
  ACTIVITY_TYPE_LABELS,
  activityTypeLabel,
  safeActivities,
  groupActivitiesByType,
  publishedActivities,
  draftActivities,
  nextPublishedActivity
} = await import('../views/activityState');

describe('activity API wrappers', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('loads all activities and course-scoped activities', async () => {
    apiClient.get.mockResolvedValueOnce([{ id: 'activity-1' }]);
    apiClient.get.mockResolvedValueOnce([{ id: 'activity-2' }]);

    await expect(listActivities()).resolves.toEqual([{ id: 'activity-1' }]);
    await expect(listCourseActivities('ai-intro')).resolves.toEqual([{ id: 'activity-2' }]);

    expect(apiClient.get).toHaveBeenNthCalledWith(1, '/api/activities', { params: {} });
    expect(apiClient.get).toHaveBeenNthCalledWith(2, '/api/courses/ai-intro/activities');
  });

  it('forwards activity query params to the shared api client', async () => {
    const params = { course_id: 'ai-intro', status: 'published' };
    apiClient.get.mockResolvedValue([{ id: 'activity-1' }]);

    await expect(listActivities(params)).resolves.toEqual([{ id: 'activity-1' }]);

    expect(apiClient.get).toHaveBeenCalledWith('/api/activities', { params });
  });

  it('creates activities through the shared api client', async () => {
    const payload = { id: 'activity-new', course_id: 'ai-intro', title: 'New Activity', type: 'reflection' };
    apiClient.post.mockResolvedValue({ id: 'activity-new' });

    await expect(createActivity(payload)).resolves.toEqual({ id: 'activity-new' });

    expect(apiClient.post).toHaveBeenCalledWith('/api/activities', payload);
  });
});

describe('activity state helpers', () => {
  const activities = [
    { id: 'draft', type: 'lecture_deck', status: 'draft' },
    { id: 'lab', type: 'code_lab', status: 'published' },
    { id: 'experiment', type: 'cognitive_experiment', status: 'published' }
  ];

  it('labels and groups activities', () => {
    expect(ACTIVITY_TYPE_LABELS.code_lab).toBe('代码实验');
    expect(activityTypeLabel('code_lab')).toBe('代码实验');
    expect(activityTypeLabel('unknown')).toBe('活动');
    expect(groupActivitiesByType(activities).code_lab[0].id).toBe('lab');
  });

  it('finds published activities and the next published item', () => {
    expect(publishedActivities(activities).map((item) => item.id)).toEqual(['lab', 'experiment']);
    expect(nextPublishedActivity(activities).id).toBe('lab');
  });

  it('normalizes activity collections and finds draft-like activities', () => {
    expect(safeActivities(null)).toEqual([]);
    expect(safeActivities(activities)).toBe(activities);
    expect(draftActivities([
      ...activities,
      { id: 'scheduled', type: 'quiz', status: 'scheduled' }
    ]).map((item) => item.id)).toEqual(['draft', 'scheduled']);
  });
});

const { getDashboardSummary } = await import('./dashboard');

describe('dashboard summary', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('includes activity totals from the activities API', async () => {
    apiClient.get.mockResolvedValueOnce([{ id: 'ai-intro', title: 'AI', chapters: [] }]);
    apiClient.get.mockResolvedValueOnce([]);
    apiClient.get.mockResolvedValueOnce([
      { id: 'activity-1', status: 'published', type: 'code_lab' },
      { id: 'activity-2', status: 'draft', type: 'lecture_deck' }
    ]);
    apiClient.get.mockResolvedValueOnce({ nodes: [], edges: [] });

    const summary = await getDashboardSummary();

    expect(summary.totals.activities).toBe(2);
    expect(summary.totals.publishedActivities).toBe(1);
    expect(summary.totals.draftActivities).toBe(1);
    expect(summary.nextActivities[0].id).toBe('activity-1');
  });

  it('surfaces dashboard source errors instead of silently treating them as empty data', async () => {
    apiClient.get.mockRejectedValueOnce(new Error('courses unavailable'));
    apiClient.get.mockResolvedValueOnce([]);
    apiClient.get.mockResolvedValueOnce([]);

    const summary = await getDashboardSummary();

    expect(summary.courses).toEqual([]);
    expect(summary.errors).toEqual(['课程加载失败：courses unavailable']);
  });

  it('surfaces graph load errors on affected courses', async () => {
    apiClient.get.mockResolvedValueOnce([{ id: 'ai-intro', title: 'AI', chapters: [] }]);
    apiClient.get.mockResolvedValueOnce([]);
    apiClient.get.mockResolvedValueOnce([]);
    apiClient.get.mockRejectedValueOnce(new Error('graph unavailable'));

    const summary = await getDashboardSummary();

    expect(summary.courses[0].graphUnavailable).toBe(true);
    expect(summary.errors).toEqual(['AI图谱加载失败：graph unavailable']);
  });
});
