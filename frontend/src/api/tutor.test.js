import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { streamTutor } from './tutor';

/**
 * Helpers to build mock SSE responses for fetch.
 * Each chunk is decoded as UTF-8 by the streamTutor's TextDecoder.
 */
function makeStreamResponse(frames) {
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    start(controller) {
      for (const frame of frames) {
        controller.enqueue(encoder.encode(frame));
      }
      controller.close();
    }
  });
  return new Response(stream, {
    status: 200,
    headers: { 'Content-Type': 'text/event-stream' }
  });
}

describe('streamTutor SSE parser', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('parses token events and accumulates text', async () => {
    const frames = [
      'data: {"type":"token","content":"Hello"}\n\n',
      'data: {"type":"token","content":" world"}\n\n',
      'data: [DONE]\n\n'
    ];
    global.fetch.mockResolvedValue(makeStreamResponse(frames));

    const tokens = [];
    let doneCalled = false;
    await streamTutor(
      { question: 'q' },
      {
        onToken: (t) => tokens.push(t),
        onDone: () => { doneCalled = true; }
      }
    );

    expect(tokens).toEqual(['Hello', ' world']);
    expect(doneCalled).toBe(true);
  });

  it('parses tool_call and tool_result events', async () => {
    const frames = [
      'data: {"type":"tool_call","content":{"name":"search_materials","arguments":{"query":"x"}}}\n\n',
      'data: {"type":"tool_result","content":{"name":"search_materials","result_preview":"5 results"}}\n\n',
      'data: [DONE]\n\n'
    ];
    global.fetch.mockResolvedValue(makeStreamResponse(frames));

    const calls = [];
    const results = [];
    await streamTutor(
      { question: 'q' },
      {
        onToolCall: (c) => calls.push(c),
        onToolResult: (r) => results.push(r)
      }
    );

    expect(calls).toEqual([
      { name: 'search_materials', arguments: { query: 'x' } }
    ]);
    expect(results).toEqual([
      { name: 'search_materials', result_preview: '5 results' }
    ]);
  });

  it('parses citations and answer events', async () => {
    const frames = [
      'data: {"type":"citations","content":[{"title":"Ch.3"}]}\n\n',
      'data: {"type":"answer","content":"Final answer"}\n\n',
      'data: [DONE]\n\n'
    ];
    global.fetch.mockResolvedValue(makeStreamResponse(frames));

    let cites;
    let ans;
    await streamTutor(
      { question: 'q' },
      {
        onCitations: (c) => { cites = c; },
        onAnswer: (a) => { ans = a; }
      }
    );

    expect(cites).toEqual([{ title: 'Ch.3' }]);
    expect(ans).toBe('Final answer');
  });

  it('handles frames split across multiple network reads', async () => {
    // First chunk: partial frame; Second chunk: completes frame + adds another
    const frames = [
      'data: {"type":"token","content":"par',
      'tial"}\n\ndata: {"type":"token","content":"second"}\n\n',
      'data: [DONE]\n\n'
    ];
    global.fetch.mockResolvedValue(makeStreamResponse(frames));

    const tokens = [];
    await streamTutor(
      { question: 'q' },
      { onToken: (t) => tokens.push(t) }
    );

    expect(tokens).toEqual(['partial', 'second']);
  });

  it('ignores malformed JSON frames silently', async () => {
    const frames = [
      'data: {invalid json}\n\n',
      'data: {"type":"token","content":"recover"}\n\n',
      'data: [DONE]\n\n'
    ];
    global.fetch.mockResolvedValue(makeStreamResponse(frames));

    const tokens = [];
    await streamTutor(
      { question: 'q' },
      { onToken: (t) => tokens.push(t) }
    );

    expect(tokens).toEqual(['recover']);
  });

  it('throws on non-OK HTTP status', async () => {
    global.fetch.mockResolvedValue(new Response('oops', { status: 500 }));

    await expect(
      streamTutor({ question: 'q' }, {})
    ).rejects.toThrow(/tutor stream failed: 500/);
  });

  it('forwards error events to onError handler', async () => {
    const frames = [
      'data: {"type":"error","content":"something went wrong"}\n\n',
      'data: [DONE]\n\n'
    ];
    global.fetch.mockResolvedValue(makeStreamResponse(frames));

    let err;
    await streamTutor(
      { question: 'q' },
      { onError: (m) => { err = m; } }
    );

    expect(err).toBe('something went wrong');
  });

  it('parses metadata events for course-specific tutor mode', async () => {
    const frames = [
      'data: {"type":"metadata","content":{"course_mode":"cognitive_neuroscience"}}\n\n',
      'data: [DONE]\n\n'
    ];
    global.fetch.mockResolvedValue(makeStreamResponse(frames));

    let metadata;
    await streamTutor(
      { question: 'q', course_id: 'brain-cog-intro' },
      { onMetadata: (m) => { metadata = m; } }
    );

    expect(metadata).toEqual({ course_mode: 'cognitive_neuroscience' });
  });
});
