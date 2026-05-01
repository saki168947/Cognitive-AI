import apiClient from './client';

export function getGraph(courseId) {
  return apiClient.get('/api/graph', {
    params: {
      course_id: courseId
    }
  });
}
