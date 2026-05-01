import apiClient from './client';

export function askTutor(payload) {
  return apiClient.post('/api/tutor/ask', payload);
}
