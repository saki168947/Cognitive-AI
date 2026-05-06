import apiClient from './client';

/**
 * Non-streaming tutor request.
 * Returns the full answer + citations after the LLM completes.
 */
export function askTutor(payload) {
  return apiClient.post('/api/tutor/ask', payload);
}

/**
 * Streaming tutor request via Server-Sent Events.
 *
 * Calls the backend with `?stream=1`. The backend yields events:
 *   {type: 'token',     content: '...'}     — partial text chunk
 *   {type: 'tool_call', content: {name, arguments}}
 *   {type: 'tool_result', content: {name, result_preview}}
 *   {type: 'citations', content: [...]}
 *   {type: 'answer',    content: '...'}     — full answer (non-streaming fallback)
 *   {type: 'metadata',  content: {...}}      — course mode/profile metadata
 *   {type: 'error',     content: '...'}
 *
 * Implementation note: SSE is read via fetch + ReadableStream so we can POST
 * a JSON body (EventSource only supports GET).
 *
 * @param {Object} payload
 *   {question, course_id?, chapter_id?, concept_id?}
 * @param {Object} handlers
 *   {onToken, onToolCall, onToolResult, onCitations, onAnswer, onMetadata, onError, onDone}
 * @param {AbortSignal} [signal] — to cancel the request
 * @returns {Promise<void>} resolves when the stream completes
 */
export async function streamTutor(payload, handlers = {}, signal) {
  const response = await fetch('/api/tutor/ask?stream=1', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    signal
  });

  if (!response.ok) {
    const text = await response.text().catch(() => '');
    throw new Error(`tutor stream failed: ${response.status} ${text || response.statusText}`);
  }
  if (!response.body) {
    throw new Error('tutor stream has no body');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  // SSE frames are separated by blank lines. Each frame contains 1+ "data:" lines.
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let separatorIndex;
    while ((separatorIndex = buffer.indexOf('\n\n')) !== -1) {
      const frame = buffer.slice(0, separatorIndex);
      buffer = buffer.slice(separatorIndex + 2);
      handleFrame(frame, handlers);
    }
  }

  // Flush remaining buffer
  if (buffer.trim()) {
    handleFrame(buffer, handlers);
  }

  if (typeof handlers.onDone === 'function') {
    handlers.onDone();
  }
}

function handleFrame(frame, handlers) {
  // Each frame is one or more lines starting with "data: "
  const dataLines = frame
    .split('\n')
    .filter((line) => line.startsWith('data:'))
    .map((line) => line.slice(5).trim());

  if (dataLines.length === 0) return;

  const data = dataLines.join('\n');
  if (data === '[DONE]') return;

  let parsed;
  try {
    parsed = JSON.parse(data);
  } catch (e) {
    // Ignore malformed frames silently — server sends clean JSON
    return;
  }

  switch (parsed.type) {
    case 'token':
      if (typeof handlers.onToken === 'function') handlers.onToken(parsed.content);
      break;
    case 'tool_call':
      if (typeof handlers.onToolCall === 'function') handlers.onToolCall(parsed.content);
      break;
    case 'tool_result':
      if (typeof handlers.onToolResult === 'function') handlers.onToolResult(parsed.content);
      break;
    case 'citations':
      if (typeof handlers.onCitations === 'function') handlers.onCitations(parsed.content);
      break;
    case 'answer':
      if (typeof handlers.onAnswer === 'function') handlers.onAnswer(parsed.content);
      break;
    case 'metadata':
      if (typeof handlers.onMetadata === 'function') handlers.onMetadata(parsed.content);
      break;
    case 'error':
      if (typeof handlers.onError === 'function') handlers.onError(parsed.content);
      break;
    default:
      // Unknown event type — silently ignore for forward compatibility
      break;
  }
}
