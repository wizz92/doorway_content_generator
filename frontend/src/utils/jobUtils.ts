import { Job, JobStatus, isJobStatus } from '../types/job';

/**
 * Raw job data from API (before normalization).
 */
interface RawJob {
  id?: unknown;
  status?: unknown;
  progress?: unknown;
  keywords_completed?: unknown;
  total_keywords?: unknown;
  websites_completed?: unknown;
  num_websites?: unknown;
  lang?: unknown;
  geo?: unknown;
  error_message?: unknown;
  created_at?: unknown;
  completed_at?: unknown;
  keywords?: unknown;
  keyword_status?: unknown;
}

/**
 * Normalize a job object from API response.
 * Handles various response formats and ensures consistent structure.
 */
export function normalizeJob(job: unknown): Job | null {
  if (!job || typeof job !== 'object') {
    return null;
  }
  
  const rawJob = job as RawJob;
  if (!rawJob.id) {
    return null;
  }
  
  // Normalize status
  let status: JobStatus = 'queued';
  if (rawJob.status) {
    const statusStr = String(rawJob.status).toLowerCase().trim();
    if (isJobStatus(statusStr)) {
      status = statusStr;
    }
  }
  
  return {
    id: String(rawJob.id),
    status,
    progress: rawJob.progress !== undefined && rawJob.progress !== null ? Number(rawJob.progress) : 0,
    keywords_completed: rawJob.keywords_completed !== undefined && rawJob.keywords_completed !== null ? Number(rawJob.keywords_completed) : 0,
    total_keywords: rawJob.total_keywords !== undefined && rawJob.total_keywords !== null ? Number(rawJob.total_keywords) : 0,
    websites_completed: rawJob.websites_completed !== undefined && rawJob.websites_completed !== null ? Number(rawJob.websites_completed) : 0,
    num_websites: rawJob.num_websites !== undefined && rawJob.num_websites !== null ? Number(rawJob.num_websites) : 0,
    lang: typeof rawJob.lang === 'string' ? rawJob.lang : '',
    geo: typeof rawJob.geo === 'string' ? rawJob.geo : '',
    error_message: typeof rawJob.error_message === 'string' ? rawJob.error_message : undefined,
    created_at: typeof rawJob.created_at === 'string' ? rawJob.created_at : new Date().toISOString(),
    completed_at: typeof rawJob.completed_at === 'string' ? rawJob.completed_at : undefined,
    keywords: Array.isArray(rawJob.keywords) ? rawJob.keywords.filter((k): k is string => typeof k === 'string') : undefined,
    keyword_status: rawJob.keyword_status && typeof rawJob.keyword_status === 'object' ? rawJob.keyword_status as Record<string, { completed_websites: number[]; total_websites: number }> : undefined,
  };
}

/**
 * Normalize an array of jobs.
 */
export function normalizeJobs(jobs: unknown): Job[] {
  if (!Array.isArray(jobs)) {
    return [];
  }
  
  return jobs.map(normalizeJob).filter((job): job is Job => job !== null);
}

/**
 * Check if job is in processing state (queued or processing).
 */
export function isJobProcessing(job: Job): boolean {
  return job.status === 'processing' || job.status === 'queued';
}

/**
 * Check if job should show progress bar.
 */
export function shouldShowProgress(job: Job): boolean {
  return isJobProcessing(job) || (job.progress !== undefined && job.progress !== null && job.progress > 0);
}

