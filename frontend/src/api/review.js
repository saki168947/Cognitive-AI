import apiClient from './client';

export function listReviewItems() {
  return apiClient.get('/api/review/items');
}

export function approveReviewItem(id) {
  return apiClient.post(`/api/review/items/${id}/approve`, {
    reviewer: 'teacher'
  });
}

export function rejectReviewItem(id) {
  return apiClient.post(`/api/review/items/${id}/reject`, {
    reviewer: 'teacher'
  });
}

export function publishReviewItem(id) {
  return apiClient.post(`/api/review/items/${id}/publish`);
}
