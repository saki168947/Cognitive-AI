import apiClient from './client';

export function listCourses() {
  return apiClient.get('/api/courses');
}

export function getCourse(courseId) {
  return apiClient.get(`/api/courses/${courseId}`);
}

export function getChapter(chapterId) {
  return apiClient.get(`/api/chapters/${chapterId}`);
}
