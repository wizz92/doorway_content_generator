import { useCallback } from 'react';
import { jobsService } from '../services/jobs';
import { useError } from '../context/ErrorContext';
import { STATUS_MESSAGES } from '../constants';

interface UseJobActionsReturn {
  handleDownload: (jobId: string) => Promise<void>;
  handleCancel: (jobId: string, onSuccess?: () => void) => Promise<void>;
}

/**
 * Hook for handling job actions (download, cancel).
 */
export function useJobActions(): UseJobActionsReturn {
  const { showError, showSuccess } = useError();

  const handleDownload = useCallback(
    async (jobId: string) => {
      try {
        const blob = await jobsService.downloadJob(jobId);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `content-${jobId}.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        showSuccess(STATUS_MESSAGES.DOWNLOAD_STARTED);
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : STATUS_MESSAGES.DOWNLOAD_ERROR;
        showError(errorMessage);
      }
    },
    [showError, showSuccess]
  );

  const handleCancel = useCallback(
    async (jobId: string, onSuccess?: () => void) => {
      try {
        await jobsService.cancelJob(jobId);
        showSuccess(STATUS_MESSAGES.JOB_CANCELLED);
        onSuccess?.();
      } catch (error: unknown) {
        const errorMessage = error instanceof Error ? error.message : STATUS_MESSAGES.CANCEL_ERROR;
        showError(errorMessage);
      }
    },
    [showError, showSuccess]
  );

  return {
    handleDownload,
    handleCancel,
  };
}

