import apiClient from './client';

export function uploadMaterial(courseId, file) {
  const formData = new FormData();
  formData.append('course_id', courseId);
  formData.append('file', file);

  return apiClient.post('/api/materials/upload', formData);
}

/**
 * Async upload — returns immediately with {material, job_id}.
 * Poll getJob() to track processing progress.
 */
export function uploadMaterialAsync(courseId, file) {
  const formData = new FormData();
  formData.append('course_id', courseId);
  formData.append('file', file);

  return apiClient.post('/api/materials/upload?async=1', formData);
}

/**
 * Fetch job status by ID.
 * Returns {id, job_type, status, progress, progress_message, ...}
 */
export function getJob(jobId) {
  return apiClient.get(`/api/jobs/${jobId}`);
}

export function listMaterials(courseId) {
  const params = courseId ? { course_id: courseId } : {};
  return apiClient.get('/api/materials', { params });
}
