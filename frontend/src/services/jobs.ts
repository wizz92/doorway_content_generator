import api from './api';

import { logger } from '../utils/logger';
import { GenerateRequest, Job, JobStatus, UploadResponse } from '../types/job';
import { normalizeJobs } from '../utils/jobUtils';

export interface JobStatusResponse {
  id: string;
  status: string;
  progress: number;
  keywords_completed: number;
  total_keywords: number;
  websites_completed: number;
  num_websites: number;
  error_message: string | null;
}

// Re-export types and interfaces for convenience
export type { Job, JobStatus };
export type { UploadResponse, GenerateRequest };

export const jobsService = {
  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<{ data: UploadResponse; error: null; message: string }>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    // Unwrap the standardized response format
    return response.data.data;
  },

  async generateContent(request: GenerateRequest): Promise<{ status: string; estimated_time: number; job_id: string }> {
    const response = await api.post('/generate', request);
    return response.data;
  },

  async getJobStatus(jobId: string): Promise<JobStatusResponse> {
    const response = await api.get<JobStatusResponse>(`/job/${jobId}/status`);
    return response.data;
  },

  async downloadJob(jobId: string): Promise<Blob> {
    const response = await api.get(`/job/${jobId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  async listJobs(limit: number = 20): Promise<Job[]> {
    try {
      logger.debug('Calling /jobs with limit:', limit);
      const timestamp = new Date().getTime();
      const response = await api.get(`/jobs?limit=${limit}&_t=${timestamp}`, {
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
        },
      });
      const data = response.data;
      
      logger.debug('API response received', { status: response.status });
      
      if (data && typeof data === 'object') {
        if (Array.isArray(data.logs)) {
          logger.error('Response has "logs" key instead of "jobs"');
          return [];
        }
        
        if (Array.isArray(data.jobs)) {
          return normalizeJobs(data.jobs);
        }
        
        if (Array.isArray(data)) {
          return normalizeJobs(data);
        }
        
        if (Array.isArray(data.data)) {
          return normalizeJobs(data.data);
        }
      }
      
      logger.warn('Unexpected response format:', data);
      return [];
    } catch (error: unknown) {
      logger.error('Error in listJobs:', error);
      throw error;
    }
  },

  async cancelJob(jobId: string): Promise<void> {
    await api.delete(`/job/${jobId}`);
  },
};
