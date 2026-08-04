import { useQuery } from '@tanstack/react-query';
import { spectreFetch, API_BASE } from './client';

/* ------------------------- URL helpers ------------------------- */

/**
 * The backend returns fully-qualified URLs from `flask.url_for(_external=True)`,
 * e.g. `http://backend:5001/spectre-data/batches/2026-08-01T00:00:00_sun.png`.
 * We only care about the file_name segment; we rebuild proxy-relative URLs
 * from it so the browser always speaks to same-origin `/api/...`.
 */
export function fileNameFromEndpoint(url: string): string {
  const stripped = url.split(/[?#]/, 1)[0] ?? url;
  const segs = stripped.split('/').filter(Boolean);
  return segs[segs.length - 1] ?? url;
}

export const batchFileUrl = (fileName: string) =>
  `${API_BASE}/spectre-data/batches/${encodeURIComponent(fileName)}`;

export const configFileUrl = (fileName: string) =>
  `${API_BASE}/spectre-data/configs/${encodeURIComponent(fileName)}`;

export const logFileUrl = (fileName: string) =>
  `${API_BASE}/spectre-data/logs/${encodeURIComponent(fileName)}`;

/* ------------------------- Receivers ------------------------- */

export function useReceivers() {
  return useQuery({
    queryKey: ['receivers'],
    queryFn: () => spectreFetch<string[]>('/receivers'),
  });
}

export function useReceiverConnected(name: string | undefined) {
  return useQuery({
    queryKey: ['receiver', name, 'connected'],
    queryFn: () => spectreFetch<boolean>(`/receivers/${encodeURIComponent(name!)}/connected`),
    enabled: !!name,
    // Connection state can flip at any moment; keep it relatively fresh.
    staleTime: 5_000,
    retry: 0,
  });
}

export function useReceiverModes(name: string | undefined) {
  return useQuery({
    queryKey: ['receiver', name, 'modes'],
    queryFn: () => spectreFetch<string[]>(`/receivers/${encodeURIComponent(name!)}/modes`),
    enabled: !!name,
  });
}

export function useReceiverModel(name: string | undefined, mode: string | undefined) {
  return useQuery({
    queryKey: ['receiver', name, 'model', mode],
    queryFn: () =>
      spectreFetch<Record<string, unknown>>(
        `/receivers/${encodeURIComponent(name!)}/model`,
        { query: { receiver_mode: mode } },
      ),
    enabled: !!name && !!mode,
  });
}

/* ------------------------- Configs ------------------------- */

export function useConfigs() {
  return useQuery({
    queryKey: ['configs'],
    queryFn: async () => {
      // The list endpoint has a trailing slash on the backend.
      const endpoints = await spectreFetch<string[]>('/spectre-data/configs/');
      return endpoints.map(fileNameFromEndpoint);
    },
  });
}

export interface ConfigRaw {
  receiver_name: string;
  receiver_mode: string;
  parameters: Record<string, unknown>;
}

export function useConfigRaw(fileName: string | undefined) {
  return useQuery({
    queryKey: ['config', fileName, 'raw'],
    queryFn: () =>
      spectreFetch<ConfigRaw>(
        `/spectre-data/configs/${encodeURIComponent(fileName!)}/raw`,
      ),
    enabled: !!fileName,
  });
}

/* ------------------------- Batches ------------------------- */

export interface BatchFilter {
  year?: number;
  month?: number;
  day?: number;
  tag?: string[];
  extension?: string[];
}

export function useBatchFiles(filter: BatchFilter) {
  return useQuery({
    queryKey: ['batches', filter],
    queryFn: async () => {
      const endpoints = await spectreFetch<string[]>('/spectre-data/batches/', {
        query: {
          year: filter.year,
          month: filter.month,
          day: filter.day,
          tag: filter.tag,
          extension: filter.extension,
        },
      });
      return endpoints.map(fileNameFromEndpoint);
    },
  });
}

export function useBatchTags(scope: Pick<BatchFilter, 'year' | 'month' | 'day'>) {
  return useQuery({
    queryKey: ['batch-tags', scope],
    queryFn: () =>
      spectreFetch<string[]>('/spectre-data/batches/tags', {
        query: { year: scope.year, month: scope.month, day: scope.day },
      }),
  });
}

/* ------------------------- Logs ------------------------- */

export interface LogFilter {
  year?: number;
  month?: number;
  day?: number;
  process_type?: string[];
}

export function useLogFiles(filter: LogFilter) {
  return useQuery({
    queryKey: ['logs', filter],
    queryFn: async () => {
      const endpoints = await spectreFetch<string[]>('/spectre-data/logs/', {
        query: {
          year: filter.year,
          month: filter.month,
          day: filter.day,
          process_type: filter.process_type,
        },
      });
      return endpoints.map(fileNameFromEndpoint);
    },
  });
}

export function useLogRaw(fileName: string | undefined) {
  return useQuery({
    queryKey: ['log', fileName, 'raw'],
    queryFn: () =>
      spectreFetch<string>(
        `/spectre-data/logs/${encodeURIComponent(fileName!)}/raw`,
      ),
    enabled: !!fileName,
  });
}
