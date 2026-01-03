import { Job, JobStatus, isJobStatus } from '../types/job';

/**
 * Normalize a job object from API response.
 * Handles various response formats and ensures consistent structure.
 */
export function normalizeJob(job: any): Job | null {
  if (!job) {
    return null;
  }
  
  if (!job.id) {
    return null;
  }
  
  // Normalize status
  let status: JobStatus = 'queued';
  if (job.status) {
    const statusStr = String(job.status).toLowerCase().trim();
    if (isJobStatus(statusStr)) {
      status = statusStr;
    }
  }
  
  return {
    id: String(job.id),
    status,
    progress: job.progress !== undefined && job.progress !== null ? Number(job.progress) : 0,
    keywords_completed: job.keywords_completed !== undefined && job.keywords_completed !== null ? Number(job.keywords_completed) : 0,
    total_keywords: job.total_keywords !== undefined && job.total_keywords !== null ? Number(job.total_keywords) : 0,
    websites_completed: job.websites_completed !== undefined && job.websites_completed !== null ? Number(job.websites_completed) : 0,
    num_websites: job.num_websites !== undefined && job.num_websites !== null ? Number(job.num_websites) : 0,
    lang: job.lang || '',
    geo: job.geo || '',
    error_message: job.error_message || undefined,
    created_at: job.created_at || new Date().toISOString(),
    completed_at: job.completed_at || undefined,
    keywords: Array.isArray(job.keywords) ? job.keywords : undefined,
    keyword_status: job.keyword_status && typeof job.keyword_status === 'object' ? job.keyword_status : undefined,
  };
}

/**
 * Normalize an array of jobs.
 */
export function normalizeJobs(jobs: any[]): Job[] {
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

