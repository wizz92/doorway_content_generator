import { useCallback, useEffect, useRef, useState } from 'react';

import { useError } from '../context/ErrorContext';
import { jobsService, Job } from '../services/jobs';
import { logger } from '../utils/logger';
import { DEFAULT_JOB_LIST_LIMIT } from '../constants';

interface UseJobsReturn {
  jobs: Job[];
  loading: boolean;
  error: string | null;
  fetchJobs: () => Promise<void>;
  refreshJobs: () => Promise<void>;
}

/**
 * Hook for managing job list.
 */
export function useJobs(limit: number = DEFAULT_JOB_LIST_LIMIT): UseJobsReturn {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { showError } = useError();
  const isInitialLoad = useRef(true);

  const fetchJobs = useCallback(async (showLoading: boolean = false) => {
    try {
      // Only show loading spinner on initial load or explicit refresh
      if (showLoading || isInitialLoad.current) {
        setLoading(true);
      }
      setError(null);
      logger.debug('Fetching jobs with limit:', limit);
      const data = await jobsService.listJobs(limit);
      logger.debug('Received jobs:', data.length);
      setJobs(data);
      if (data.length === 0) {
        logger.debug('No jobs found');
      }
      isInitialLoad.current = false;
    } catch (err: unknown) {
      logger.error('Error fetching jobs:', err);
      const errObj = err as { response?: { data?: { detail?: string } }; message?: string };
      const errorMessage = errObj.response?.data?.detail || errObj.message || 'Failed to load jobs';
      setError(errorMessage);
      showError(errorMessage);
      setJobs([]);
      isInitialLoad.current = false;
    } finally {
      setLoading(false);
    }
  }, [limit, showError]);

  const refreshJobs = useCallback(async () => {
    await fetchJobs(true); // Show loading on manual refresh
  }, [fetchJobs]);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  return {
    jobs,
    loading,
    error,
    fetchJobs,
    refreshJobs,
  };
}

