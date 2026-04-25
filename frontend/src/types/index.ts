export interface Job {
  id: number | null;
  source: string;
  job_id: string;
  title: string;
  company: string;
  company_url: string;
  company_logo: string;
  description: string;
  location: string;
  job_type: string;
  salary: string;
  tags: string;
  job_url: string;
  posted_at: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface JobListResponse {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  jobs: Job[];
  has_new: boolean;
  last_updated: string | null;
}

export interface StatsResponse {
  total_jobs: number;
  by_source: Record<string, number>;
  sources: string[];
  job_types: string[];
  latest_update: string | null;
}

export interface FilterOptions {
  sources: string[];
  job_types: string[];
  locations: string[];
  date_ranges: Record<string, string>;
}

export interface ApiError {
  detail: string;
}
