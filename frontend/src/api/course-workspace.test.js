import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('./client', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn()
  }
}));

const { default: apiClient } = await import('./client');
const { listCourses, getCourse, getChapter } = await import('./courses');
const { getGraph } = await import('./graph');
const { askTutor } = await import('./tutor');

describe('course workspace API wrappers', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('loads courses, courses by id, and chapters through the shared api client', async () => {
    apiClient.get.mockResolvedValueOnce([{ id: 'course-1' }]);
    apiClient.get.mockResolvedValueOnce({ id: 'course-1' });
    apiClient.get.mockResolvedValueOnce({ id: 'chapter-1' });

    await expect(listCourses()).resolves.toEqual([{ id: 'course-1' }]);
    await expect(getCourse('course-1')).resolves.toEqual({ id: 'course-1' });
    await expect(getChapter('chapter-1')).resolves.toEqual({ id: 'chapter-1' });

    expect(apiClient.get).toHaveBeenNthCalledWith(1, '/api/courses');
    expect(apiClient.get).toHaveBeenNthCalledWith(2, '/api/courses/course-1');
    expect(apiClient.get).toHaveBeenNthCalledWith(3, '/api/chapters/chapter-1');
  });

  it('loads graph data with a course_id query parameter', async () => {
    apiClient.get.mockResolvedValue({ nodes: [], edges: [] });

    await expect(getGraph('course-1')).resolves.toEqual({ nodes: [], edges: [] });

    expect(apiClient.get).toHaveBeenCalledWith('/api/graph', {
      params: {
        course_id: 'course-1'
      }
    });
  });

  it('posts tutor questions without unwrapping a second time', async () => {
    const payload = {
      question: 'What is attention?',
      course_id: 'course-1',
      chapter_id: 'chapter-1'
    };
    const answer = { answer: 'A selective processing mechanism.' };
    apiClient.post.mockResolvedValue(answer);

    await expect(askTutor(payload)).resolves.toBe(answer);

    expect(apiClient.post).toHaveBeenCalledWith('/api/tutor/ask', payload);
  });
});
