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
  activityTypeLabel,
  groupActivitiesByType,
  publishedActivities,
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
    expect(activityTypeLabel('code_lab')).toBe('代码实验');
    expect(groupActivitiesByType(activities).code_lab[0].id).toBe('lab');
  });

  it('finds published activities and the next published item', () => {
    expect(publishedActivities(activities).map((item) => item.id)).toEqual(['lab', 'experiment']);
    expect(nextPublishedActivity(activities).id).toBe('lab');
  });
});
