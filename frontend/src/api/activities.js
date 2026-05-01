import apiClient from './client';

export function listActivities(params = {}) {
  return apiClient.get('/api/activities', { params });
}

export function listCourseActivities(courseId) {
  return apiClient.get(`/api/courses/${courseId}/activities`);
}

export function createActivity(payload) {
  return apiClient.post('/api/activities', payload);
}
