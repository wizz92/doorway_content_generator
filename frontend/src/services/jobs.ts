import api from './api';
import { normalizeJobs } from '../utils/jobUtils';
import { 
  Job, 
  JobStatus, 
  UploadResponse, 
  GenerateRequest 
} from '../types/job';

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
    const response = await api.post<UploadResponse>('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async generateContent(request: GenerateRequest): Promise<{ status: string; estimated_time: number; job_id: string }> {
    const response = await api.post('/api/generate', request);
    return response.data;
  },

  async getJobStatus(jobId: string): Promise<JobStatusResponse> {
    const response = await api.get<JobStatusResponse>(`/api/job/${jobId}/status`);
    return response.data;
  },

  async downloadJob(jobId: string): Promise<Blob> {
    const response = await api.get(`/api/job/${jobId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  async listJobs(limit: number = 20): Promise<Job[]> {
    try {
      console.log('📞 Calling /api/jobs with limit:', limit);
      // Add cache-busting timestamp to prevent browser/proxy caching
      const timestamp = new Date().getTime();
      const response = await api.get(`/api/jobs?limit=${limit}&_t=${timestamp}`, {
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
        },
      });
      const data = response.data;
      
      console.log('📥 API response:', {
        status: response.status,
        data: data,
        isArray: Array.isArray(data),
        length: Array.isArray(data) ? data.length : 'N/A',
      });
      
      // Handle response with "jobs" key (NOT "logs")
      if (data && typeof data === 'object') {
        // CRITICAL: Check for "logs" key - this should NOT happen from /api/jobs
        if (Array.isArray(data.logs)) {
          console.error('❌ ERROR: Response has "logs" key instead of "jobs"! This is wrong!');
          console.error('   This suggests the wrong endpoint (/api/logs/jobs) is being called');
          console.error('   Response keys:', Object.keys(data));
          // Don't return logs - return empty array instead
          return [];
        }
        
        // Correct response: "jobs" key
        if (Array.isArray(data.jobs)) {
          const normalized = normalizeJobs(data.jobs);
          console.log('✅ Normalized jobs from data.jobs:', normalized.length, normalized);
          return normalized;
        }
        // Fallback: if response is directly an array
        if (Array.isArray(data)) {
          const normalized = normalizeJobs(data);
          console.log('✅ Normalized jobs from array:', normalized.length, normalized);
          return normalized;
        }
        // Legacy support for "data" key
        if (Array.isArray(data.data)) {
          return normalizeJobs(data.data);
        }
      }
      
      console.warn('⚠️ Unexpected response format:', data);
      return [];
    } catch (error: any) {
      console.error('❌ Error in listJobs:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
      });
      throw error;
    }
  },

  async cancelJob(jobId: string): Promise<void> {
    await api.delete(`/api/job/${jobId}`);
  },
};
