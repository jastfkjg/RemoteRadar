import axios from 'axios';
import type { Job, JobListResponse, StatsResponse, FilterOptions } from '../types';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const jobApi = {
  getJobs: async (params: {
    page?: number;
    page_size?: number;
    source?: string;
    job_type?: string;
    location?: string;
    days_ago?: number;
    search?: string;
    sort_by?: string;
    sort_order?: string;
    since_time?: string;
  } = {}): Promise<JobListResponse> => {
    const response = await api.get<JobListResponse>('/jobs', { params });
    return response.data;
  },

  getJobById: async (jobId: number): Promise<Job> => {
    const response = await api.get<Job>(`/jobs/${jobId}`);
    return response.data;
  },

  getStats: async (): Promise<StatsResponse> => {
    const response = await api.get<StatsResponse>('/stats');
    return response.data;
  },

  getFilters: async (): Promise<FilterOptions> => {
    const response = await api.get<FilterOptions>('/filters');
    return response.data;
  },

  getHealth: async (): Promise<{ status: string; total_jobs: number; timestamp: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
