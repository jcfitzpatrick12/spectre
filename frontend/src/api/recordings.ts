/**
 * Recording request types shared between the RecordingsContext and any
 * caller. The actual HTTP call is made from RecordingsContext.start(), which
 * needs to correlate the in-flight state with the fetch promise.
 */

export type RecordingKind = 'signal' | 'spectrogram';

export interface RecordingRequest {
  kind: RecordingKind;
  tags: string[];
  duration: number;
  force_restart?: boolean;
  max_restarts?: number;
  validate?: boolean;
}
