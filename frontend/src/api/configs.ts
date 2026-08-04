import { useMutation, useQueryClient } from '@tanstack/react-query';
import { spectreFetch } from './client';

export interface CreateConfigInput {
  fileName: string;
  receiver_name: string;
  receiver_mode: string;
  string_parameters: string[];
  force?: boolean;
  validate?: boolean;
}

export interface UpdateConfigInput {
  fileName: string;
  params: string[];
  force?: boolean;
  validate?: boolean;
}

export interface DeleteConfigInput {
  fileName: string;
  dry_run?: boolean;
}

function invalidate(qc: ReturnType<typeof useQueryClient>, fileName?: string) {
  qc.invalidateQueries({ queryKey: ['configs'] });
  if (fileName) {
    qc.invalidateQueries({ queryKey: ['config', fileName, 'raw'] });
  }
}

export function useCreateConfig() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: CreateConfigInput): Promise<string> => {
      const endpoint = await spectreFetch<string>(
        `/spectre-data/configs/${encodeURIComponent(input.fileName)}`,
        {
          method: 'PUT',
          body: {
            receiver_name: input.receiver_name,
            receiver_mode: input.receiver_mode,
            string_parameters: input.string_parameters,
            force: input.force ?? false,
            validate: input.validate ?? true,
          },
        },
      );
      return endpoint;
    },
    onSuccess: (_data, vars) => invalidate(qc, vars.fileName),
  });
}

export function useUpdateConfig() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: UpdateConfigInput): Promise<string> => {
      const endpoint = await spectreFetch<string>(
        `/spectre-data/configs/${encodeURIComponent(input.fileName)}`,
        {
          method: 'PATCH',
          body: {
            params: input.params,
            force: input.force ?? false,
            validate: input.validate ?? true,
          },
        },
      );
      return endpoint;
    },
    onSuccess: (_data, vars) => invalidate(qc, vars.fileName),
  });
}

export function useDeleteConfig() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: DeleteConfigInput): Promise<string> => {
      const endpoint = await spectreFetch<string>(
        `/spectre-data/configs/${encodeURIComponent(input.fileName)}`,
        {
          method: 'DELETE',
          query: { dry_run: input.dry_run ?? false },
        },
      );
      return endpoint;
    },
    onSuccess: (_data, vars) => invalidate(qc, vars.fileName),
  });
}
