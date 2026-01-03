import { useState, useEffect, useCallback, useRef } from 'react';
import { jobsService, Job } from '../services/jobs';
import { useError } from '../context/ErrorContext';

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
export function useJobs(limit: number = 50): UseJobsReturn {
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
      console.log('🔄 useJobs: Fetching jobs with limit:', limit);
      const data = await jobsService.listJobs(limit);
      console.log('✅ useJobs: Received jobs:', data.length, data);
      setJobs(data);
      if (data.length === 0) {
        console.log('ℹ️ useJobs: No jobs found');
      }
      isInitialLoad.current = false;
    } catch (err: any) {
      console.error('❌ useJobs: Error fetching jobs:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load jobs';
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

