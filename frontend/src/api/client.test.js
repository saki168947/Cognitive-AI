import { describe, expect, it } from 'vitest';
import { unwrapEnvelope, unwrapEnvelopeError } from './client';

describe('unwrapEnvelope', () => {
  it('returns payload data from a success envelope', () => {
    expect(unwrapEnvelope({ data: { success: true, data: { id: 1 } } })).toEqual({ id: 1 });
  });

  it('throws the envelope error message when success is false', () => {
    expect(() => unwrapEnvelope({ data: { success: false, error: 'Not allowed' } })).toThrow('Not allowed');
  });

  it('returns raw response data when no envelope is present', () => {
    expect(unwrapEnvelope({ data: { status: 'ok' } })).toEqual({ status: 'ok' });
  });

  it('throws backend envelope messages from rejected axios responses', () => {
    const axiosError = {
      response: {
        data: {
          success: false,
          error: 'question is required'
        }
      }
    };

    expect(() => unwrapEnvelopeError(axiosError)).toThrow('question is required');
  });
});
