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
  categories: string;
  tech_stacks: string;
  seniority: string;
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
  categories: string[];
  tech_stacks: string[];
  seniority_levels: string[];
  latest_update: string | null;
}

export interface FilterOptions {
  sources: string[];
  job_types: string[];
  locations: string[];
  categories: string[];
  tech_stacks: string[];
  seniority_levels: string[];
  date_ranges: Record<string, string>;
}

export interface ApiError {
  detail: string;
}

export interface User {
  id: number;
  user_id: string;
  email: string;
  username: string;
  created_at: string | null;
  last_login: string | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

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
  categories: string;
  tech_stacks: string;
  seniority: string;
  is_saved: boolean;
}

export interface RecommendationItem {
  job_id: number;
  job: Job;
  score: number;
  reasons: string[];
}

export interface RecommendationResponse {
  user_id: string;
  recommendations: RecommendationItem[];
  is_hot: boolean;
}

export interface UserProfile {
  user_id: string;
  categories: string[];
  tech_stacks: string[];
  seniority: string | null;
  locations: string[];
  min_salary: number | null;
  max_salary: number | null;
}

export interface SavedJobsResponse {
  job_ids: number[];
  count: number;
}

export interface SaveJobResponse {
  success: boolean;
  saved: boolean;
  message: string;
}

export interface UserSkill {
  id: number;
  user_id: string;
  skill_name: string;
  proficiency: string;
  acquired_date: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface UserSkillCreate {
  skill_name: string;
  proficiency: string;
  acquired_date?: string;
}

export interface UserSkillUpdate {
  skill_name?: string;
  proficiency?: string;
  acquired_date?: string;
}

export interface UserExperience {
  id: number;
  user_id: string;
  company: string;
  position: string;
  start_date: string | null;
  end_date: string | null;
  current: boolean;
  description: string | null;
  achievements: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface UserExperienceCreate {
  company: string;
  position: string;
  start_date?: string;
  end_date?: string;
  current: boolean;
  description?: string;
  achievements?: string;
}

export interface UserExperienceUpdate {
  company?: string;
  position?: string;
  start_date?: string;
  end_date?: string;
  current?: boolean;
  description?: string;
  achievements?: string;
}

export interface UserPreferences {
  user_id: string;
  preferred_industries: string[];
  preferred_job_types: string[];
  preferred_locations: string[];
  min_salary: number | null;
  max_salary: number | null;
  work_mode: string;
  remote_only: boolean;
  created_at: string | null;
  updated_at: string | null;
}

export interface UserPreferencesUpdate {
  preferred_industries?: string[];
  preferred_job_types?: string[];
  preferred_locations?: string[];
  min_salary?: number | null;
  max_salary?: number | null;
  work_mode?: string;
  remote_only?: boolean;
}

export interface CompleteProfile {
  user: User;
  skills: UserSkill[];
  experiences: UserExperience[];
  preferences: UserPreferences | null;
}
