/** Job status types */
export type JobStatus = 'queued' | 'processing' | 'completed' | 'failed';

/** Keyword status interface */
export interface KeywordStatus {
  completed_websites: number[];
  total_websites: number;
}

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
  keywords?: string[];
  keyword_status?: Record<string, KeywordStatus>;
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
export function isJob(value: unknown): value is Job {
  if (!value || typeof value !== 'object') {
    return false;
  }
  
  const obj = value as Record<string, unknown>;
  
  return (
    typeof obj.id === 'string' &&
    typeof obj.status === 'string' &&
    isJobStatus(obj.status) &&
    typeof obj.progress === 'number' &&
    typeof obj.keywords_completed === 'number' &&
    typeof obj.total_keywords === 'number' &&
    typeof obj.websites_completed === 'number' &&
    typeof obj.num_websites === 'number' &&
    typeof obj.created_at === 'string'
  );
}

/** Discriminated union for job with status */
export type JobWithStatus =
  | { status: 'queued' | 'processing'; progress: number }
  | { status: 'completed'; progress: 100 }
  | { status: 'failed'; error_message: string };

