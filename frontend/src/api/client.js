import axios from 'axios';

export function unwrapEnvelope(response) {
  const payload = response?.data;

  if (payload && typeof payload === 'object' && typeof payload.success === 'boolean') {
    if (payload.success) {
      return payload.data;
    }

    throw new Error(payload.error || payload.message || 'Request failed');
  }

  return payload;
}

export function unwrapEnvelopeError(error) {
  const payload = error?.response?.data;

  if (payload && typeof payload === 'object' && typeof payload.success === 'boolean') {
    throw new Error(payload.error || payload.message || 'Request failed');
  }

  throw error;
}

const apiClient = axios.create({
  baseURL: '',
  timeout: 20000
});

apiClient.interceptors.response.use(unwrapEnvelope, unwrapEnvelopeError);

export default apiClient;
