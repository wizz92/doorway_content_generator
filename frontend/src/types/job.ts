/** Job status types */
export type JobStatus = 'queued' | 'processing' | 'completed' | 'failed';

/** Job interface */
export interface Job {
  id: string;
  status: JobStatus;
  progress: number;
  keywords_completed: number;
  total_keywords: number;
  websites_completed: number;
  num_websites: number;
  lang?: string;
  geo?: string;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

/** Job status response from API */
export interface JobStatusResponse {
  id: string;
  status: string;
  progress: number;
  keywords_completed: number;
  total_keywords: number;
  websites_completed: number;
  num_websites: number;
  error_message: string | null;
  created_at: string | null;
  completed_at: string | null;
}

/** Upload response */
export interface UploadResponse {
  job_id: string;
  keywords_count: number;
  preview: string[];
}

/** Generate request */
export interface GenerateRequest {
  job_id: string;
  lang: string;
  geo: string;
  num_websites: number;
}

/** Type guard to check if value is a valid JobStatus */
export function isJobStatus(value: string): value is JobStatus {
  return ['queued', 'processing', 'completed', 'failed'].includes(value);
}

/** Type guard to check if object is a Job */
export function isJob(value: any): value is Job {
  return (
    value &&
    typeof value === 'object' &&
    typeof value.id === 'string' &&
    isJobStatus(value.status) &&
    typeof value.progress === 'number' &&
    typeof value.keywords_completed === 'number' &&
    typeof value.total_keywords === 'number' &&
    typeof value.websites_completed === 'number' &&
    typeof value.num_websites === 'number' &&
    typeof value.created_at === 'string'
  );
}

/** Discriminated union for job with status */
export type JobWithStatus =
  | { status: 'queued' | 'processing'; progress: number }
  | { status: 'completed'; progress: 100 }
  | { status: 'failed'; error_message: string };

