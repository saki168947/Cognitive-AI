import apiClient from './client';

export function uploadMaterial(courseId, file) {
  const formData = new FormData();
  formData.append('course_id', courseId);
  formData.append('file', file);

  return apiClient.post('/api/materials/upload', formData);
}
