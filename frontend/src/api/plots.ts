import { useMutation } from '@tanstack/react-query';
import { spectreFetch } from './client';
import { fileNameFromEndpoint } from './queries';

export interface PlotRequest {
  tags: string[];
  obs_date: string; // YYYY-MM-DD
  start_time: string; // HH:MM:SS
  end_time: string; // HH:MM:SS
  lower_freq?: number | null;
  upper_freq?: number | null;
  log_norm?: boolean;
  dBb?: boolean;
  vmin?: number | null;
  vmax?: number | null;
  figsize_x?: number | null;
  figsize_y?: number | null;
}

export interface PlotResult {
  fileName: string;
  createdAt: number;
  request: PlotRequest;
}

export function usePlotMutation() {
  return useMutation({
    mutationFn: async (req: PlotRequest): Promise<PlotResult> => {
      const endpoint = await spectreFetch<string>('/spectre-data/batches/plots', {
        method: 'PUT',
        body: req,
      });
      return {
        fileName: fileNameFromEndpoint(endpoint),
        createdAt: Date.now(),
        request: req,
      };
    },
  });
}
